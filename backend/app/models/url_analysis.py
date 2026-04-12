from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.static_analysis import RiskLevel


class UrlAnalysisResult(Base):
    __tablename__ = "url_analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"), unique=True, index=True)
    normalized_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    scheme: Mapped[str] = mapped_column(String(16), nullable=False, default="http")
    hostname: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    path: Mapped[str] = mapped_column(String(2048), nullable=False, default="/")
    query_present: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resolved_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    dns_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    uses_https: Mapped[bool] = mapped_column(Boolean, nullable=False)
    final_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    redirect_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), nullable=False)
    risk_indicators: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    verdict_reason: Mapped[str] = mapped_column(Text, nullable=False, default="")
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
