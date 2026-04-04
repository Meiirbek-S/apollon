import hashlib
import os
import tempfile

import filetype

from app.db.session import SessionLocal
from app.models.static_analysis import RiskLevel, StaticAnalysisResult
from app.models.submission import Submission, SubmissionStatus
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

        risk = _estimate_risk(submission.filename, mime_type)

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


def _estimate_risk(filename: str, mime_type: str) -> RiskLevel:
    lowered = filename.lower()
    suspicious_ext = (".exe", ".dll", ".bat", ".cmd", ".scr", ".ps1")
    if lowered.endswith(suspicious_ext):
        return RiskLevel.SUSPICIOUS
    if "x-dosexec" in mime_type or "x-msdownload" in mime_type:
        return RiskLevel.SUSPICIOUS
    return RiskLevel.SAFE
