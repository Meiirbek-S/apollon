from fastapi import APIRouter

router = APIRouter()


@router.get("/metrics")
def metrics() -> dict:
    return {"submissions_total": 0, "queue_depth": 0, "sandbox_errors": 0}
