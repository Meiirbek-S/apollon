from fastapi import APIRouter, HTTPException

from app.api.v1.endpoints.submit import SUBMISSION_STATE
from app.schemas.report import ReportResponse
from app.services.scoring.risk_engine import RiskEngine

router = APIRouter()


@router.get("/submissions/{submission_id}/report", response_model=ReportResponse)
def get_report(submission_id: str) -> ReportResponse:
    state = SUBMISSION_STATE.get(submission_id)
    if not state:
        raise HTTPException(status_code=404, detail="Submission not found")

    risk = RiskEngine.evaluate(static_score=8, dynamic_score=0, url_score=0)
    return ReportResponse(
        submission_id=submission_id,
        verdict=risk.verdict,
        score=risk.total_score,
        score_breakdown=risk.breakdown,
        summary="Draft report. Connect persisted analysis tables for full results.",
    )
