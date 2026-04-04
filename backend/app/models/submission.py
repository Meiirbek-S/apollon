from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SubmissionType(StrEnum):
    FILE = "FILE"
    URL = "URL"


class SubmissionStatus(StrEnum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_type: Mapped[SubmissionType] = mapped_column(Enum(SubmissionType), nullable=False)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus), default=SubmissionStatus.QUEUED, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
