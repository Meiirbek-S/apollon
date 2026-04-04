import hashlib
import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.submission import Submission, SubmissionStatus, SubmissionType
from app.schemas.submission import FileSubmissionCreate, SubmissionCreateResponse, SubmissionRead
from app.services.object_storage import ensure_bucket_exists, get_minio_client, upload_file
from app.tasks.submission_tasks import process_file_submission

router = APIRouter(prefix="/api/v1/submissions", tags=["submissions"])


@router.post("/file", response_model=SubmissionCreateResponse, status_code=201)
def create_file_submission(payload: FileSubmissionCreate, db: Session = Depends(get_db)) -> SubmissionCreateResponse:
    if payload.sha256 and len(payload.sha256) != 64:
        raise HTTPException(status_code=400, detail="sha256 must be 64 characters")

    submission = Submission(
        source_type=SubmissionType.FILE,
        filename=payload.filename,
        sha256=payload.sha256,
        status=SubmissionStatus.QUEUED,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    task = process_file_submission.delay(submission.id)

    return SubmissionCreateResponse(submission_id=submission.id, status=submission.status, task_id=task.id)


@router.post("/file/upload", response_model=SubmissionCreateResponse, status_code=201)
def upload_file_submission(file: UploadFile = File(...), db: Session = Depends(get_db)) -> SubmissionCreateResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="filename is required")

    max_size = settings.max_upload_size_mb * 1024 * 1024
    total_size = 0
    digest = hashlib.sha256()

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        temp_path = tmp.name
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > max_size:
                os.unlink(temp_path)
                raise HTTPException(status_code=413, detail=f"file too large, limit is {settings.max_upload_size_mb} MB")
            digest.update(chunk)
            tmp.write(chunk)

    file_hash = digest.hexdigest()

    # Дедуп только среди реально загруженных артефактов (storage_key is not null).
    existing_artifact = db.execute(
        select(Submission)
        .where(Submission.sha256 == file_hash)
        .where(Submission.storage_key.is_not(None))
        .order_by(Submission.id.desc())
        .limit(1)
    ).scalar_one_or_none()

    if existing_artifact:
        os.unlink(temp_path)

        submission = Submission(
            source_type=SubmissionType.FILE,
            filename=file.filename,
            sha256=file_hash,
            content_type=existing_artifact.content_type,
            size_bytes=existing_artifact.size_bytes,
            storage_key=existing_artifact.storage_key,
            status=SubmissionStatus.QUEUED,
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        task = process_file_submission.delay(submission.id)

        return SubmissionCreateResponse(
            submission_id=submission.id,
            status=submission.status,
            task_id=task.id,
            deduplicated=True,
            reused_from_submission_id=existing_artifact.id,
        )

    client = get_minio_client()
    ensure_bucket_exists(client)

    ext = os.path.splitext(file.filename)[1]
    object_name = f"samples/{file_hash}{ext}"
    content_type = file.content_type or "application/octet-stream"

    upload_file(client, object_name=object_name, file_path=temp_path, content_type=content_type)
    os.unlink(temp_path)

    submission = Submission(
        source_type=SubmissionType.FILE,
        filename=file.filename,
        sha256=file_hash,
        content_type=content_type,
        size_bytes=total_size,
        storage_key=object_name,
        status=SubmissionStatus.QUEUED,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    task = process_file_submission.delay(submission.id)

    return SubmissionCreateResponse(
        submission_id=submission.id,
        status=submission.status,
        task_id=task.id,
        deduplicated=False,
    )


@router.get("/{submission_id}", response_model=SubmissionRead)
def get_submission(submission_id: int, db: Session = Depends(get_db)) -> SubmissionRead:
    submission = db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="submission not found")
    return SubmissionRead.model_validate(submission)
