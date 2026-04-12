from datetime import datetime
from enum import StrEnum

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RiskLevel(StrEnum):
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    MALWARE_LIKE = "MALWARE-LIKE"


class StaticAnalysisResult(Base):
    __tablename__ = "static_analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"), unique=True, index=True)

    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    md5: Mapped[str] = mapped_column(String(32), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)
    extension: Mapped[str] = mapped_column(String(32), nullable=False)
    extension_mismatch: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), nullable=False)
    risk_indicators: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    verdict_reason: Mapped[str] = mapped_column(Text, nullable=False, default="")

    is_pe: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    machine_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    compile_timestamp: Mapped[str | None] = mapped_column(String(64), nullable=True)
    entry_point: Mapped[str | None] = mapped_column(String(32), nullable=True)
    image_base: Mapped[str | None] = mapped_column(String(32), nullable=True)
    pe_sections: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    imported_functions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    suspicious_imports: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    antivirus_detection: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
