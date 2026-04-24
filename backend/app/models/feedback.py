from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    shop_id: Mapped[int | None] = mapped_column(ForeignKey("shops.id"), nullable=True)
    audio_path: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    cleaned_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    language: Mapped[str] = mapped_column(String(20), default="zh", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    shop = relationship("Shop", back_populates="feedbacks")
    analysis_result = relationship(
        "AnalysisResult", back_populates="feedback", uselist=False
    )
