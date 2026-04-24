from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    feedback_id: Mapped[int] = mapped_column(
        ForeignKey("feedbacks.id"), unique=True, nullable=False
    )
    shop_name: Mapped[str] = mapped_column(String(100), nullable=False)
    sentiment_label: Mapped[str] = mapped_column(String(20), nullable=False)
    sentiment_positive: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sentiment_negative: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    sentiment_neutral: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    issue_categories: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    issue_weights: Mapped[dict[str, float]] = mapped_column(
        JSON, default=dict, nullable=False
    )
    urgency: Mapped[str] = mapped_column(String(20), default="低", nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    summary_en: Mapped[str] = mapped_column(Text, default="", nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    feedback = relationship("Feedback", back_populates="analysis_result")
