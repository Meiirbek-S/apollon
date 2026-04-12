from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
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


class DynamicAnalysisStatus(StrEnum):
    NOT_REQUESTED = "NOT_REQUESTED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_type: Mapped[SubmissionType] = mapped_column(Enum(SubmissionType), nullable=False)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    target_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    content_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    reused_from_submission_id: Mapped[int | None] = mapped_column(
        ForeignKey("submissions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus), default=SubmissionStatus.QUEUED, nullable=False
    )
    dynamic_requested: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dynamic_status: Mapped[DynamicAnalysisStatus] = mapped_column(
        Enum(DynamicAnalysisStatus), default=DynamicAnalysisStatus.NOT_REQUESTED, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
