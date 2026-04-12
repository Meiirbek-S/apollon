from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.static_analysis import RiskLevel


class DynamicAnalysisResult(Base):
    __tablename__ = "dynamic_analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"), unique=True, index=True)

    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    sandbox_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), nullable=False)
    suspicious_actions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    network_connections: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    file_changes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    registry_changes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    verdict_reason: Mapped[str] = mapped_column(Text, nullable=False, default="")
    raw_report: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
