from datetime import datetime

from pydantic import BaseModel, HttpUrl


class UrlSubmit(BaseModel):
    url: HttpUrl


class SubmissionCreated(BaseModel):
    submission_id: str
    status: str


class FileSubmissionCreated(SubmissionCreated):
    sha256: str
    md5: str


class SubmissionInfo(BaseModel):
    submission_id: str
    type: str
    status: str
    created_at: datetime
