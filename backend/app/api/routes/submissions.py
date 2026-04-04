from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.submission import Submission, SubmissionStatus, SubmissionType
from app.schemas.submission import FileSubmissionCreate, SubmissionCreateResponse, SubmissionRead
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


@router.get("/{submission_id}", response_model=SubmissionRead)
def get_submission(submission_id: int, db: Session = Depends(get_db)) -> SubmissionRead:
    submission = db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="submission not found")
    return SubmissionRead.model_validate(submission)
