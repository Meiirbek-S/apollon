from datetime import datetime

from pydantic import BaseModel, Field

from app.models.submission import SubmissionStatus, SubmissionType


class FileSubmissionCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=512)
    sha256: str | None = Field(default=None, min_length=64, max_length=64)


class SubmissionCreateResponse(BaseModel):
    submission_id: int
    status: SubmissionStatus
    task_id: str


class SubmissionRead(BaseModel):
    id: int
    source_type: SubmissionType
    filename: str
    sha256: str | None
    status: SubmissionStatus
    created_at: datetime

    model_config = {"from_attributes": True}
