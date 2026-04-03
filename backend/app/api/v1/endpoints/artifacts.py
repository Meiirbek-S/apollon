from fastapi import APIRouter, HTTPException

from app.api.v1.endpoints.submit import SUBMISSION_META
from app.schemas.report import ArtifactItem

router = APIRouter()


@router.get("/submissions/{submission_id}/artifacts", response_model=list[ArtifactItem])
def get_artifacts(submission_id: str) -> list[ArtifactItem]:
    meta = SUBMISSION_META.get(submission_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Submission not found")

    artifacts: list[ArtifactItem] = []
    if meta.get("storage_path"):
        artifacts.append(ArtifactItem(kind="sample", path=meta["storage_path"]))
    return artifacts
