from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.schemas.submission import FileSubmissionCreated, SubmissionCreated, UrlSubmit
from app.services.static_analysis.hash_service import HashService
from app.workers.tasks import run_dynamic_analysis, run_static_analysis, run_url_analysis

router = APIRouter()

SUBMISSION_STATE: dict[str, dict[str, str]] = {}
SUBMISSION_META: dict[str, dict] = {}


def _storage_path(submission_id: str, filename: str) -> Path:
    base = Path(settings.storage_dir)
    base.mkdir(parents=True, exist_ok=True)
    safe_name = filename.replace("/", "_")
    return base / f"{submission_id}_{safe_name}"


@router.post("/submit/file", response_model=FileSubmissionCreated)
async def submit_file(file: UploadFile = File(...)) -> FileSubmissionCreated:
    payload = await file.read()
    if len(payload) > settings.upload_max_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    hashes = HashService.calculate_from_bytes(payload)
    submission_id = f"subm_{uuid4().hex[:12]}"
    store_path = _storage_path(submission_id, file.filename or "sample.bin")
    store_path.write_bytes(payload)

    SUBMISSION_STATE[submission_id] = {"status": "queued", "stage": "queued"}
    SUBMISSION_META[submission_id] = {
        "type": "file",
        "created_at": "pending-db",
        "storage_path": str(store_path),
        "hashes": hashes,
    }

    run_static_analysis.delay(submission_id)
    run_dynamic_analysis.delay(submission_id)

    return FileSubmissionCreated(submission_id=submission_id, status="queued", sha256=hashes["sha256"], md5=hashes["md5"])


@router.post("/submit/url", response_model=SubmissionCreated)
def submit_url(payload: UrlSubmit) -> SubmissionCreated:
    submission_id = f"subm_{uuid4().hex[:12]}"
    SUBMISSION_STATE[submission_id] = {"status": "queued", "stage": "queued"}
    SUBMISSION_META[submission_id] = {
        "type": "url",
        "created_at": "pending-db",
        "url": str(payload.url),
    }
    run_url_analysis.delay(submission_id)
    return SubmissionCreated(submission_id=submission_id, status="queued")
