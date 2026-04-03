from pydantic import BaseModel


class StatusResponse(BaseModel):
    submission_id: str
    status: str
    stage: str


class ReportResponse(BaseModel):
    submission_id: str
    verdict: str
    score: int
    score_breakdown: dict[str, int]
    summary: str


class ArtifactItem(BaseModel):
    kind: str
    path: str
