from fastapi import APIRouter

router = APIRouter()


@router.post("/admin/reanalyze/{submission_id}")
def reanalyze_submission(submission_id: str) -> dict:
    return {"submission_id": submission_id, "status": "queued", "message": "Reanalysis queued"}
