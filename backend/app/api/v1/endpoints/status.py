from fastapi import APIRouter, HTTPException

from app.api.v1.endpoints.submit import SUBMISSION_STATE
from app.schemas.report import StatusResponse

router = APIRouter()


@router.get("/submissions/{submission_id}/status", response_model=StatusResponse)
def get_status(submission_id: str) -> StatusResponse:
    state = SUBMISSION_STATE.get(submission_id)
    if not state:
        raise HTTPException(status_code=404, detail="Submission not found")
    return StatusResponse(submission_id=submission_id, status=state["status"], stage=state["stage"])
