from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.api.v1.endpoints.submit import SUBMISSION_META, SUBMISSION_STATE
from app.schemas.submission import SubmissionInfo

router = APIRouter()


@router.get("/submissions/{submission_id}", response_model=SubmissionInfo)
def get_submission(submission_id: str) -> SubmissionInfo:
    meta = SUBMISSION_META.get(submission_id)
    state = SUBMISSION_STATE.get(submission_id)
    if not meta or not state:
        raise HTTPException(status_code=404, detail="Submission not found")

    return SubmissionInfo(
        submission_id=submission_id,
        type=meta["type"],
        status=state["status"],
        created_at=datetime.utcnow(),
    )
