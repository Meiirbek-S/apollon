import hashlib
import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.static_analysis import StaticAnalysisResult
from app.models.submission import Submission, SubmissionStatus, SubmissionType
from app.schemas.submission import (
    FileSubmissionCreate,
    StaticAnalysisRead,
    SubmissionCreateResponse,
    SubmissionRead,
)
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

    # 1) Ищем лучший source для дедупа: сначала с готовым static report.
    source_with_report = db.execute(
        select(Submission)
        .join(StaticAnalysisResult, StaticAnalysisResult.submission_id == Submission.id)
        .where(Submission.sha256 == file_hash)
        .where(Submission.storage_key.is_not(None))
        .order_by(Submission.id.desc())
        .limit(1)
    ).scalar_one_or_none()

    # 2) Fallback: любой загруженный артефакт с таким hash.
    latest_artifact = db.execute(
        select(Submission)
        .where(Submission.sha256 == file_hash)
        .where(Submission.storage_key.is_not(None))
        .order_by(Submission.id.desc())
        .limit(1)
    ).scalar_one_or_none()

    dedup_source = source_with_report or latest_artifact

    if dedup_source:
        os.unlink(temp_path)

        has_ready_report = source_with_report is not None
        status = SubmissionStatus.DONE if has_ready_report else SubmissionStatus.QUEUED

        submission = Submission(
            source_type=SubmissionType.FILE,
            filename=file.filename,
            sha256=file_hash,
            content_type=dedup_source.content_type,
            size_bytes=dedup_source.size_bytes,
            storage_key=dedup_source.storage_key,
            reused_from_submission_id=dedup_source.id,
            status=status,
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        if has_ready_report:
            return SubmissionCreateResponse(
                submission_id=submission.id,
                status=submission.status,
                task_id="reused-existing-report",
                deduplicated=True,
                reused_from_submission_id=dedup_source.id,
            )

        task = process_file_submission.delay(submission.id)
        return SubmissionCreateResponse(
            submission_id=submission.id,
            status=submission.status,
            task_id=task.id,
            deduplicated=True,
            reused_from_submission_id=dedup_source.id,
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


@router.get("/{submission_id}/report", response_model=StaticAnalysisRead)
def get_static_report(submission_id: int, db: Session = Depends(get_db)) -> StaticAnalysisRead:
    # 1) Прямой lookup
    result = db.query(StaticAnalysisResult).filter_by(submission_id=submission_id).one_or_none()
    if result:
        return StaticAnalysisRead.model_validate(result)

    # 2) Цепочка reused_from_submission_id
    current_id = submission_id
    visited: set[int] = set()

    while current_id and current_id not in visited:
        visited.add(current_id)
        submission = db.get(Submission, current_id)
        if not submission:
            break

        if not submission.reused_from_submission_id:
            break

        current_id = submission.reused_from_submission_id
        reused_result = db.query(StaticAnalysisResult).filter_by(submission_id=current_id).one_or_none()
        if reused_result:
            return StaticAnalysisRead.model_validate(reused_result)

    raise HTTPException(status_code=404, detail="static analysis report not found")
