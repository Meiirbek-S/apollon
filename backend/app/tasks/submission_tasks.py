import hashlib
import ipaddress
import os
import socket
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import filetype
import pefile

from app.db.session import SessionLocal
from app.models.static_analysis import RiskLevel, StaticAnalysisResult
from app.models.submission import Submission, SubmissionStatus
from app.models.url_analysis import UrlAnalysisResult
from app.services.object_storage import download_file, get_minio_client
from app.tasks.celery_app import celery_app

SUSPICIOUS_IMPORT_KEYWORDS = (
    "virtualalloc",
    "writeprocessmemory",
    "createremotethread",
    "winexec",
    "shellexecute",
    "urlmon",
    "internetopen",
    "internetconnect",
    "regsetvalue",
    "createprocess",
    "loadlibrary",
    "getprocaddress",
)

ABNORMAL_SECTION_NAMES = {".asdf", ".boom", ".x", "upx0", "upx1", "upx2"}


@celery_app.task(name="submission.process_file")
def process_file_submission(submission_id: int) -> dict[str, int | str]:
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
        raise
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
        db.close()


@celery_app.task(name="submission.process_url")
def process_url_submission(submission_id: int) -> dict[str, int | str]:
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

        normalized_url, domain, uses_https = _normalize_url(submission.target_url)
        resolved_ip = _resolve_domain(domain)
        risk = _estimate_url_risk(domain=domain, uses_https=uses_https, resolved_ip=resolved_ip)

        existing = db.query(UrlAnalysisResult).filter_by(submission_id=submission.id).one_or_none()
        if existing:
            db.delete(existing)
            db.commit()

        result = UrlAnalysisResult(
            submission_id=submission.id,
            normalized_url=normalized_url,
            domain=domain,
            resolved_ip=resolved_ip,
            uses_https=uses_https,
            risk_level=risk,
        )
        db.add(result)
        submission.status = SubmissionStatus.DONE
        db.commit()

        return {"submission_id": submission_id, "result": "url_analyzed", "risk": risk.value}
    except Exception:
        submission = db.get(Submission, submission_id)
        if submission:
            submission.status = SubmissionStatus.FAILED
            db.commit()
        raise
    finally:
        db.close()


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

    pe_info = _analyze_pe(temp_path, original_filename)

    if pe_info["is_pe"]:
        score += pe_info["pe_score"]
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


def _analyze_pe(temp_path: str, original_filename: str) -> dict:
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

    try:
        pe = pefile.PE(temp_path, fast_load=False)
    except Exception:
        return result if not likely_pe else {**result, "pe_indicators": ["file has PE-like extension but parse failed"], "pe_score": 15}

    result["is_pe"] = True
    machine_type = hex(pe.FILE_HEADER.Machine)
    result["machine_type"] = machine_type
    try:
        ts = datetime.fromtimestamp(pe.FILE_HEADER.TimeDateStamp, tz=timezone.utc).isoformat()
    except Exception:
        ts = None
    result["compile_timestamp"] = ts
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
            result["pe_score"] += 12
            result["pe_indicators"].append(f"high entropy section: {name} ({entropy:.2f})")

        is_exec = bool(characteristics & 0x20000000)
        is_write = bool(characteristics & 0x80000000)
        if is_exec and is_write:
            result["pe_score"] += 15
            result["pe_indicators"].append(f"section is executable and writable: {name}")

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
                if any(keyword in lowered for keyword in SUSPICIOUS_IMPORT_KEYWORDS):
                    suspicious_imports.add(full_name)

    if suspicious_imports:
        result["pe_score"] += min(30, 5 * len(suspicious_imports))
        result["pe_indicators"].append(f"suspicious imports count: {len(suspicious_imports)}")

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
    top = "; ".join(indicators[:3])
    return f"{risk_level.value}: {top} (score={score})"


def _normalize_url(raw_url: str) -> tuple[str, str, bool]:
    candidate = raw_url.strip()
    parsed = urlparse(candidate)
    if parsed.scheme not in ("http", "https"):
        candidate = f"http://{candidate}"
        parsed = urlparse(candidate)

    if not parsed.hostname:
        raise ValueError("invalid URL: hostname is required")

    normalized_url = parsed.geturl()
    return normalized_url, parsed.hostname.lower(), parsed.scheme == "https"


def _resolve_domain(domain: str) -> str | None:
    try:
        return socket.gethostbyname(domain)
    except Exception:
        return None


def _estimate_url_risk(domain: str, uses_https: bool, resolved_ip: str | None) -> RiskLevel:
    score = 0
    if not uses_https:
        score += 20

    try:
        ipaddress.ip_address(domain)
        score += 20
    except ValueError:
        pass

    if "xn--" in domain:
        score += 15

    if resolved_ip is None:
        score += 10

    return RiskLevel.SUSPICIOUS if score >= 20 else RiskLevel.SAFE
