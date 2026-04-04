from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.static_analysis import RiskLevel


class UrlAnalysisResult(Base):
    __tablename__ = "url_analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"), unique=True, index=True)
    normalized_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    resolved_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    uses_https: Mapped[bool] = mapped_column(Boolean, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
