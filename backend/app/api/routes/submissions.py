import hashlib
import os
import tempfile
from typing import Any
<<<<<<< HEAD
=======
from urllib.parse import urlparse
>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.static_analysis import StaticAnalysisResult
from app.models.submission import Submission, SubmissionStatus, SubmissionType
from app.models.url_analysis import UrlAnalysisResult
from app.schemas.submission import (
    FileSubmissionCreate,
    StaticAnalysisRead,
    SubmissionCreateResponse,
    SubmissionRead,
    UrlAnalysisRead,
    UrlSubmissionCreate,
)
from app.services.object_storage import ensure_bucket_exists, get_minio_client, upload_file
from app.tasks.submission_tasks import process_file_submission, process_url_submission

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


@router.post("/url", response_model=SubmissionCreateResponse, status_code=201)
def create_url_submission(payload: UrlSubmissionCreate, db: Session = Depends(get_db)) -> SubmissionCreateResponse:
    normalized = payload.url.strip()
<<<<<<< HEAD
=======
    parsed = urlparse(normalized if "://" in normalized else f"http://{normalized}")
    if not parsed.hostname:
        raise HTTPException(status_code=422, detail="invalid URL: hostname is required")

>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
    submission = Submission(
        source_type=SubmissionType.URL,
        filename=normalized,
        target_url=normalized,
        status=SubmissionStatus.QUEUED,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    task = process_url_submission.delay(submission.id)

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

    source_with_report = db.execute(
        select(Submission)
        .join(StaticAnalysisResult, StaticAnalysisResult.submission_id == Submission.id)
        .where(Submission.sha256 == file_hash)
        .where(Submission.storage_key.is_not(None))
        .order_by(Submission.id.desc())
        .limit(1)
    ).scalar_one_or_none()

    latest_artifact = db.execute(
        select(Submission)
        .where(Submission.sha256 == file_hash)
        .where(Submission.storage_key.is_not(None))
        .order_by(Submission.id.desc())
        .limit(1)
    ).scalar_one_or_none()

<<<<<<< HEAD
    dedup_source = source_with_report or latest_artifact

    if dedup_source:
        os.unlink(temp_path)

        source_report = None
        has_ready_report = False
        if source_with_report is not None:
            source_report = db.query(StaticAnalysisResult).filter_by(submission_id=source_with_report.id).one_or_none()
            has_ready_report = bool(source_report and _is_static_report_complete(source_report))

        status = SubmissionStatus.DONE if has_ready_report else SubmissionStatus.QUEUED

=======
    source_report = None
    has_ready_report = False
    if source_with_report is not None:
        source_report = db.query(StaticAnalysisResult).filter_by(submission_id=source_with_report.id).one_or_none()
        has_ready_report = bool(source_report and _is_static_report_complete(source_report))

    # CASE 1: есть готовый повторно используемый отчет -> deduplicated=true и DONE без нового анализа
    if source_with_report is not None and has_ready_report:
        os.unlink(temp_path)
>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
        submission = Submission(
            source_type=SubmissionType.FILE,
            filename=file.filename,
            sha256=file_hash,
<<<<<<< HEAD
            content_type=dedup_source.content_type,
            size_bytes=dedup_source.size_bytes,
            storage_key=dedup_source.storage_key,
            reused_from_submission_id=dedup_source.id,
            status=status,
=======
            content_type=source_with_report.content_type,
            size_bytes=source_with_report.size_bytes,
            storage_key=source_with_report.storage_key,
            reused_from_submission_id=source_with_report.id,
            status=SubmissionStatus.DONE,
>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
<<<<<<< HEAD

        if has_ready_report:
            return SubmissionCreateResponse(
                submission_id=submission.id,
                status=submission.status,
                task_id="reused-existing-report",
                deduplicated=True,
                reused_from_submission_id=dedup_source.id,
            )
=======
        return SubmissionCreateResponse(
            submission_id=submission.id,
            status=submission.status,
            task_id="reused-existing-report",
            deduplicated=True,
            reused_from_submission_id=source_with_report.id,
        )

    # CASE 2: готового отчета нет -> НЕ считаем это dedup-готовым результатом.
    # Можно переиспользовать уже загруженный артефакт, но анализ запускается заново.
    if latest_artifact and latest_artifact.storage_key:
        os.unlink(temp_path)
        submission = Submission(
            source_type=SubmissionType.FILE,
            filename=file.filename,
            sha256=file_hash,
            content_type=latest_artifact.content_type,
            size_bytes=latest_artifact.size_bytes,
            storage_key=latest_artifact.storage_key,
            status=SubmissionStatus.QUEUED,
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5

        task = process_file_submission.delay(submission.id)
        return SubmissionCreateResponse(
            submission_id=submission.id,
            status=submission.status,
            task_id=task.id,
<<<<<<< HEAD
            deduplicated=True,
            reused_from_submission_id=dedup_source.id,
=======
            deduplicated=False,
            reused_from_submission_id=None,
>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
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




def _is_static_report_complete(report: StaticAnalysisResult) -> bool:
    # базовые поля должны быть заполнены
    if not (report.original_filename and report.verdict_reason):
        return False

    # после scoring v2, если есть suspicious imports,
    # ожидаем детальные индикаторы вида "suspicious import: ... (+N)".
    if report.suspicious_imports:
        has_weighted_import_indicator = any(
            indicator.startswith("suspicious import:") for indicator in (report.risk_indicators or [])
        )
        if not has_weighted_import_indicator:
            return False

    return True

@router.get("/{submission_id}", response_model=SubmissionRead)
def get_submission(submission_id: int, db: Session = Depends(get_db)) -> SubmissionRead:
    submission = db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="submission not found")
    return SubmissionRead.model_validate(submission)


def _resolve_static_report(submission_id: int, db: Session) -> StaticAnalysisRead | None:
<<<<<<< HEAD
=======
    submission = db.get(Submission, submission_id)
    if not submission:
        return None

>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
    result = db.query(StaticAnalysisResult).filter_by(submission_id=submission_id).one_or_none()
    if result:
        return StaticAnalysisRead.model_validate(result)

    current_id = submission_id
    visited: set[int] = set()

    while current_id and current_id not in visited:
        visited.add(current_id)
        submission = db.get(Submission, current_id)
        if not submission or not submission.reused_from_submission_id:
            break

        current_id = submission.reused_from_submission_id
        reused_result = db.query(StaticAnalysisResult).filter_by(submission_id=current_id).one_or_none()
        if reused_result:
            return StaticAnalysisRead.model_validate(reused_result)

<<<<<<< HEAD
=======
    # fallback для старых/несвязанных дедуп-цепочек: ищем готовый отчет по тому же sha256
    if submission.sha256:
        same_hash_result = (
            db.query(StaticAnalysisResult)
            .join(Submission, Submission.id == StaticAnalysisResult.submission_id)
            .filter(Submission.sha256 == submission.sha256)
            .order_by(StaticAnalysisResult.created_at.desc())
            .first()
        )
        if same_hash_result:
            return StaticAnalysisRead.model_validate(same_hash_result)

>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
    return None


@router.get("/{submission_id}/report", response_model=dict[str, Any])
def get_report(submission_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    submission = db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="submission not found")

    if submission.source_type == SubmissionType.FILE:
        static_report = _resolve_static_report(submission_id, db)
        if not static_report:
<<<<<<< HEAD
=======
            if submission.status in {SubmissionStatus.QUEUED, SubmissionStatus.PROCESSING}:
                raise HTTPException(status_code=404, detail="static analysis report not ready yet")
            if submission.status == SubmissionStatus.FAILED:
                raise HTTPException(status_code=404, detail="static analysis failed or report unavailable")
>>>>>>> codex/design-web-system-for-malware-analysis-5z4ma5
            raise HTTPException(status_code=404, detail="static analysis report not found")

        payload = static_report.model_dump()
        if payload.get("submission_id") != submission_id:
            payload["submission_id"] = submission_id
            if submission.filename:
                payload["original_filename"] = submission.filename

        return {"report_type": "FILE", "report": payload}

    if submission.source_type == SubmissionType.URL:
        url_report = db.query(UrlAnalysisResult).filter_by(submission_id=submission_id).one_or_none()
        if not url_report:
            raise HTTPException(status_code=404, detail="url analysis report not found")
        return {"report_type": "URL", "report": UrlAnalysisRead.model_validate(url_report).model_dump()}

    raise HTTPException(status_code=400, detail="unsupported submission type")


@router.get("/{submission_id}/url-report", response_model=UrlAnalysisRead)
def get_url_report(submission_id: int, db: Session = Depends(get_db)) -> UrlAnalysisRead:
    result = db.query(UrlAnalysisResult).filter_by(submission_id=submission_id).one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail="url analysis report not found")
    return UrlAnalysisRead.model_validate(result)
