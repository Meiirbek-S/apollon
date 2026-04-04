from datetime import datetime

from pydantic import BaseModel, Field

from app.models.static_analysis import RiskLevel
from app.models.submission import SubmissionStatus, SubmissionType


class FileSubmissionCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=512)
    sha256: str | None = Field(default=None, min_length=64, max_length=64)


class SubmissionCreateResponse(BaseModel):
    submission_id: int
    status: SubmissionStatus
    task_id: str
    deduplicated: bool = False
    reused_from_submission_id: int | None = None


class SubmissionRead(BaseModel):
    id: int
    source_type: SubmissionType
    filename: str
    sha256: str | None
    content_type: str | None
    size_bytes: int | None
    storage_key: str | None
    status: SubmissionStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class StaticAnalysisRead(BaseModel):
    submission_id: int
    md5: str
    sha256: str
    file_size: int
    mime_type: str
    risk_level: RiskLevel
    created_at: datetime

    model_config = {"from_attributes": True}
