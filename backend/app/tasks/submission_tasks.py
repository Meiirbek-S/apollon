import hashlib
import ipaddress
import os
import socket
import tempfile
from urllib.parse import urlparse

import filetype

from app.db.session import SessionLocal
from app.models.static_analysis import RiskLevel, StaticAnalysisResult
from app.models.submission import Submission, SubmissionStatus
from app.models.url_analysis import UrlAnalysisResult
from app.services.object_storage import download_file, get_minio_client
from app.tasks.celery_app import celery_app


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

        risk = _estimate_file_risk(submission.filename, mime_type)

        existing = db.query(StaticAnalysisResult).filter_by(submission_id=submission.id).one_or_none()
        if existing:
            db.delete(existing)
            db.commit()

        result = StaticAnalysisResult(
            submission_id=submission.id,
            md5=md5_hash.hexdigest(),
            sha256=sha256_hash.hexdigest(),
            file_size=file_size,
            mime_type=mime_type,
            risk_level=risk,
        )
        db.add(result)

        submission.status = SubmissionStatus.DONE
        db.commit()

        return {"submission_id": submission_id, "result": "analyzed", "risk": risk.value}
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


def _estimate_file_risk(filename: str, mime_type: str) -> RiskLevel:
    lowered = filename.lower()
    suspicious_ext = (".exe", ".dll", ".bat", ".cmd", ".scr", ".ps1")
    if lowered.endswith(suspicious_ext):
        return RiskLevel.SUSPICIOUS
    if "x-dosexec" in mime_type or "x-msdownload" in mime_type:
        return RiskLevel.SUSPICIOUS
    return RiskLevel.SAFE


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
