import hashlib
import ipaddress
import logging
import os
import socket
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import filetype
import pefile
from celery.exceptions import SoftTimeLimitExceeded

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.static_analysis import RiskLevel, StaticAnalysisResult
from app.models.submission import Submission, SubmissionStatus
from app.models.url_analysis import UrlAnalysisResult
from app.services.object_storage import download_file, get_minio_client
from app.tasks.celery_app import celery_app

SUSPICIOUS_IMPORT_WEIGHTS = {
    "virtualalloc": 10,
    "createremotethread": 12,
    "writeprocessmemory": 12,
    "createprocess": 8,
    "createprocessa": 8,
    "createprocessw": 8,
    "loadlibrary": 5,
    "loadlibrarya": 5,
    "loadlibraryw": 5,
    "getprocaddress": 8,
    "winexec": 8,
    "shellexecute": 6,
    "internetopen": 5,
    "internetconnect": 5,
    "urlmon": 5,
    "regsetvalue": 6,
}

ABNORMAL_SECTION_NAMES = {".asdf", ".boom", ".x", "upx0", "upx1", "upx2", ".upx"}
logger = logging.getLogger(__name__)

def _process_file_submission_impl(submission_id: int) -> dict[str, int | str]:
    db = SessionLocal()
    temp_path = None
    try:
        submission = db.get(Submission, submission_id)
        if not submission:
            return {"submission_id": submission_id, "result": "submission_not_found"}

        submission.status = SubmissionStatus.PROCESSING
        db.commit()

        if not submission.storage_key:
            submission.status = SubmissionStatus.FAILED
            db.commit()
            return {"submission_id": submission_id, "result": "missing_storage_key"}

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            temp_path = tmp.name

        client = get_minio_client()
        download_file(client, submission.storage_key, temp_path)

        static_data = _analyze_file(temp_path=temp_path, original_filename=submission.filename)

        existing = db.query(StaticAnalysisResult).filter_by(submission_id=submission.id).one_or_none()
        if existing:
            db.delete(existing)
            db.commit()

        result = StaticAnalysisResult(submission_id=submission.id, **static_data)
        db.add(result)

        submission.status = SubmissionStatus.DONE
        db.commit()

        return {
            "submission_id": submission_id,
            "result": "analyzed",
            "risk": static_data["risk_level"].value,
            "risk_score": static_data["risk_score"],
        }
    except Exception:
        submission = db.get(Submission, submission_id)
        if submission:
            submission.status = SubmissionStatus.FAILED
            db.commit()
        logger.exception("process_file_submission failed", extra={"submission_id": submission_id})
        raise
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
        db.close()


def _process_url_submission_impl(submission_id: int) -> dict[str, int | str]:
    db = SessionLocal()
    try:
        submission = db.get(Submission, submission_id)
        if not submission:
            return {"submission_id": submission_id, "result": "submission_not_found"}

        if not submission.target_url:
            submission.status = SubmissionStatus.FAILED
            db.commit()
            return {"submission_id": submission_id, "result": "missing_target_url"}

        submission.status = SubmissionStatus.PROCESSING
        db.commit()

        normalized_url, parsed_info = _normalize_url(submission.target_url)
        domain = parsed_info["hostname"]
        uses_https = parsed_info["uses_https"]
        resolved_ip = _resolve_domain(domain)
        risk_data = _estimate_url_risk(
            normalized_url=normalized_url,
            hostname=domain,
            uses_https=uses_https,
            resolved_ip=resolved_ip,
            port=parsed_info["port"],
            query_present=parsed_info["query_present"],
        )

        existing = db.query(UrlAnalysisResult).filter_by(submission_id=submission.id).one_or_none()
        if existing:
            db.delete(existing)
            db.commit()

        result = UrlAnalysisResult(
            submission_id=submission.id,
            normalized_url=normalized_url,
            domain=domain,
            scheme=parsed_info["scheme"],
            hostname=domain,
            path=parsed_info["path"],
            query_present=parsed_info["query_present"],
            port=parsed_info["port"],
            resolved_ip=resolved_ip,
            dns_resolved=bool(resolved_ip),
            uses_https=uses_https,
            final_url=normalized_url,
            redirect_count=0,
            risk_score=risk_data["risk_score"],
            risk_level=risk_data["risk_level"],
            risk_indicators=risk_data["risk_indicators"],
            verdict_reason=risk_data["verdict_reason"],
            analyzed_at=datetime.now(timezone.utc),
        )
        db.add(result)
        submission.status = SubmissionStatus.DONE
        db.commit()

        return {
            "submission_id": submission_id,
            "result": "url_analyzed",
            "risk": risk_data["risk_level"].value,
            "risk_score": risk_data["risk_score"],
        }
    except Exception:
        submission = db.get(Submission, submission_id)
        if submission:
            submission.status = SubmissionStatus.FAILED
            db.commit()
        logger.exception("process_url_submission failed", extra={"submission_id": submission_id})
        raise
    finally:
        db.close()


@celery_app.task(name="submission.process_file", soft_time_limit=settings.analysis_task_soft_time_limit_sec)
def process_file_submission(submission_id: int) -> dict[str, int | str]:
    return _process_file_submission_impl(submission_id)


# Совместимость со старыми producer'ами, которые могли отправлять имя задачи по умолчанию.
@celery_app.task(name="app.tasks.submission_tasks.process_file_submission", soft_time_limit=settings.analysis_task_soft_time_limit_sec)
def process_file_submission_legacy(submission_id: int) -> dict[str, int | str]:
    return _process_file_submission_impl(submission_id)


@celery_app.task(name="submission.process_url", soft_time_limit=settings.analysis_task_soft_time_limit_sec)
def process_url_submission(submission_id: int) -> dict[str, int | str]:
    return _process_url_submission_impl(submission_id)


# Совместимость со старыми producer'ами, которые могли отправлять имя задачи по умолчанию.
@celery_app.task(name="app.tasks.submission_tasks.process_url_submission", soft_time_limit=settings.analysis_task_soft_time_limit_sec)
def process_url_submission_legacy(submission_id: int) -> dict[str, int | str]:
    return _process_url_submission_impl(submission_id)


def _analyze_file(temp_path: str, original_filename: str) -> dict:
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()
    file_size = 0

    with open(temp_path, "rb") as src:
        while True:
            chunk = src.read(1024 * 1024)
            if not chunk:
                break
            file_size += len(chunk)
            md5_hash.update(chunk)
            sha256_hash.update(chunk)

    kind = filetype.guess(temp_path)
    mime_type = kind.mime if kind else "application/octet-stream"
    detected_ext = kind.extension.lower() if kind and kind.extension else ""
    file_ext = Path(original_filename).suffix.lower().lstrip(".")
    extension_mismatch = bool(file_ext and detected_ext and file_ext != detected_ext)

    indicators: list[str] = []
    score = 0

    if extension_mismatch:
        indicators.append(f"extension mismatch: .{file_ext} vs .{detected_ext}")
        score += 10

    pe_info = _analyze_pe(temp_path, original_filename, file_size)

    if pe_info["pe_score"]:
        score += pe_info["pe_score"]
    if pe_info["pe_indicators"]:
        indicators.extend(pe_info["pe_indicators"])

    risk_level = _score_to_level(score)
    verdict_reason = _build_verdict_reason(score, risk_level, indicators)

    return {
        "original_filename": original_filename,
        "md5": md5_hash.hexdigest(),
        "sha256": sha256_hash.hexdigest(),
        "file_size": file_size,
        "mime_type": mime_type,
        "extension": file_ext,
        "extension_mismatch": extension_mismatch,
        "risk_score": score,
        "risk_level": risk_level,
        "risk_indicators": indicators,
        "verdict_reason": verdict_reason,
        "is_pe": pe_info["is_pe"],
        "machine_type": pe_info["machine_type"],
        "compile_timestamp": pe_info["compile_timestamp"],
        "entry_point": pe_info["entry_point"],
        "image_base": pe_info["image_base"],
        "pe_sections": pe_info["sections"],
        "imported_functions": pe_info["imported_functions"],
        "suspicious_imports": pe_info["suspicious_imports"],
    }


def _analyze_pe(temp_path: str, original_filename: str, file_size: int) -> dict:
    result = {
        "is_pe": False,
        "machine_type": None,
        "compile_timestamp": None,
        "entry_point": None,
        "image_base": None,
        "sections": [],
        "imported_functions": [],
        "suspicious_imports": [],
        "pe_score": 0,
        "pe_indicators": [],
    }

    likely_pe = original_filename.lower().endswith((".exe", ".dll", ".sys", ".scr"))
    deep_parse_limit = settings.pe_deep_parse_max_size_mb * 1024 * 1024
    if file_size > deep_parse_limit:
        return {
            **result,
            "pe_indicators": [f"PE deep parse skipped: file size {file_size} bytes exceeds limit"],
            "pe_score": 5 if likely_pe else 0,
        }

    try:
        pe = pefile.PE(temp_path, fast_load=True)
        if hasattr(pe, "parse_data_directories"):
            pe.parse_data_directories(
                directories=[
                    pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                ]
            )
    except SoftTimeLimitExceeded:
        raise
    except Exception:
        return result if not likely_pe else {**result, "pe_indicators": ["file has PE-like extension but parse failed"], "pe_score": 25}

    result["is_pe"] = True
    machine_type = hex(pe.FILE_HEADER.Machine)
    result["machine_type"] = machine_type
    try:
        ts = datetime.fromtimestamp(pe.FILE_HEADER.TimeDateStamp, tz=timezone.utc).isoformat()
    except Exception:
        ts = None
    result["compile_timestamp"] = ts
    if ts:
        try:
            year = datetime.fromisoformat(ts).year
            current_year = datetime.now(timezone.utc).year
            if year < 2000 or year > current_year + 1:
                result["pe_score"] += 5
                result["pe_indicators"].append(f"suspicious compile timestamp year: {year}")
        except Exception:
            pass

    result["entry_point"] = hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint)
    result["image_base"] = hex(pe.OPTIONAL_HEADER.ImageBase)

    pe_sections = []
    suspicious_imports = set()
    imported_functions = []

    for section in pe.sections:
        name = section.Name.decode(errors="ignore").strip("\x00").lower()
        entropy = float(section.get_entropy())
        characteristics = int(section.Characteristics)

        pe_sections.append(
            {
                "name": name,
                "virtual_size": int(section.Misc_VirtualSize),
                "raw_size": int(section.SizeOfRawData),
                "entropy": round(entropy, 4),
                "characteristics": hex(characteristics),
            }
        )

        if entropy >= 7.2:
            result["pe_score"] += 10
            result["pe_indicators"].append(f"high entropy section: {name} ({entropy:.2f})")

        is_exec = bool(characteristics & 0x20000000)
        is_write = bool(characteristics & 0x80000000)
        if is_exec and is_write:
            result["pe_score"] += 15
            result["pe_indicators"].append(f"RWX section detected: {name}")

        if name in ABNORMAL_SECTION_NAMES:
            result["pe_score"] += 10
            result["pe_indicators"].append(f"abnormal section name: {name}")

    if pe_sections and all(s["entropy"] >= 7.0 for s in pe_sections):
        result["pe_score"] += 15
        result["pe_indicators"].append("possible packed/obfuscated PE: all sections high entropy")

    if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
        for entry in pe.DIRECTORY_ENTRY_IMPORT:
            dll_name = entry.dll.decode(errors="ignore") if entry.dll else "unknown.dll"
            for imp in entry.imports:
                func_name = imp.name.decode(errors="ignore") if imp.name else f"ordinal_{imp.ordinal}"
                full_name = f"{dll_name}!{func_name}"
                imported_functions.append(full_name)
                lowered = func_name.lower()
                matched_weight = 0
                for keyword, weight in SUSPICIOUS_IMPORT_WEIGHTS.items():
                    if keyword in lowered:
                        matched_weight = max(matched_weight, weight)
                if matched_weight:
                    suspicious_imports.add(full_name)
                    result["pe_score"] += matched_weight
                    result["pe_indicators"].append(f"suspicious import: {full_name} (+{matched_weight})")

    if suspicious_imports:
        count_bonus = min(15, 2 * len(suspicious_imports))
        result["pe_score"] += count_bonus
        result["pe_indicators"].append(f"suspicious imports count bonus: {len(suspicious_imports)} (+{count_bonus})")

    result["sections"] = pe_sections
    result["imported_functions"] = sorted(imported_functions)
    result["suspicious_imports"] = sorted(suspicious_imports)
    return result


def _score_to_level(score: int) -> RiskLevel:
    if score >= 60:
        return RiskLevel.MALWARE_LIKE
    if score >= 25:
        return RiskLevel.SUSPICIOUS
    return RiskLevel.SAFE


def _build_verdict_reason(score: int, risk_level: RiskLevel, indicators: list[str]) -> str:
    if not indicators:
        return f"{risk_level.value}: no suspicious static indicators found (score={score})"

    categories: list[str] = []
    if any("high entropy section" in i for i in indicators):
        categories.append("high entropy")
    if any("suspicious import:" in i for i in indicators):
        categories.append("suspicious imports")
    if any("RWX section detected" in i for i in indicators):
        categories.append("RWX sections")
    if any("abnormal section name" in i for i in indicators):
        categories.append("abnormal section names")
    if any("extension mismatch" in i for i in indicators):
        categories.append("extension mismatch")

    if categories:
        summary = " + ".join(categories[:3])
        return f"{risk_level.value}: {summary} (score={score})"

    top = "; ".join(indicators[:3])
    return f"{risk_level.value}: {top} (score={score})"


def _normalize_url(raw_url: str) -> tuple[str, dict[str, str | int | bool | None]]:
    candidate = raw_url.strip()
    parsed = urlparse(candidate)
    if parsed.scheme not in ("http", "https"):
        candidate = f"http://{candidate}"
        parsed = urlparse(candidate)

    if not parsed.hostname:
        raise ValueError("invalid URL: hostname is required")

    normalized_url = parsed.geturl()
    path = parsed.path if parsed.path else "/"
    return normalized_url, {
        "scheme": parsed.scheme.lower(),
        "hostname": parsed.hostname.lower(),
        "path": path,
        "query_present": bool(parsed.query),
        "port": parsed.port,
        "uses_https": parsed.scheme.lower() == "https",
    }


def _resolve_domain(domain: str) -> str | None:
    try:
        return socket.gethostbyname(domain)
    except Exception:
        return None


def _estimate_url_risk(
    normalized_url: str,
    hostname: str,
    uses_https: bool,
    resolved_ip: str | None,
    port: int | None,
    query_present: bool,
) -> dict[str, RiskLevel | int | list[str] | str]:
    score = 0
    indicators: list[str] = []

    if not uses_https:
        score += 20
        indicators.append("URL не использует HTTPS")
    else:
        indicators.append("Сайт использует HTTPS")

    try:
        ipaddress.ip_address(hostname)
        score += 20
        indicators.append("Используется прямой IP вместо доменного имени")
    except ValueError:
        indicators.append("Используется доменное имя")

    if "xn--" in hostname:
        score += 15
        indicators.append("Обнаружен punycode-домен (возможна имитация)")

    if resolved_ip is None:
        score += 10
        indicators.append("DNS-имя не резолвится")
    else:
        indicators.append("Домен успешно резолвится в IP")

    if query_present:
        score += 5
        indicators.append("URL содержит параметры запроса")
    else:
        indicators.append("URL не содержит параметров запроса")

    if port and port not in {80, 443}:
        score += 15
        indicators.append(f"Обнаружен нестандартный порт: {port}")
    else:
        indicators.append("Подозрительный порт не обнаружен")

    host_labels = hostname.split(".")
    if len(hostname) > 60 or any(len(label) > 30 for label in host_labels):
        score += 10
        indicators.append("Домен выглядит необычно длинным")

    if len(normalized_url) > 180:
        score += 10
        indicators.append("URL слишком длинный")

    risk_level = RiskLevel.MALWARE_LIKE if score >= 60 else RiskLevel.SUSPICIOUS if score >= 25 else RiskLevel.SAFE

    if risk_level == RiskLevel.SAFE:
        verdict_reason = f"SAFE: явных опасных признаков не выявлено (score={score})"
    elif risk_level == RiskLevel.SUSPICIOUS:
        verdict_reason = f"SUSPICIOUS: обнаружены признаки, требующие проверки (score={score})"
    else:
        verdict_reason = f"MALWARE-LIKE: URL содержит несколько опасных признаков (score={score})"

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "risk_indicators": indicators,
        "verdict_reason": verdict_reason,
    }
