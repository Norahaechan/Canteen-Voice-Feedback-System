from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Shop(Base):
    __tablename__ = "shops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    category_en: Mapped[str] = mapped_column(String(80), default="", nullable=False)
    aliases: Mapped[str] = mapped_column(Text, default="", nullable=False)
    aliases_en: Mapped[str] = mapped_column(Text, default="", nullable=False)
    current_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    feedback_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    primary_sentiment: Mapped[str] = mapped_column(
        String(20), default="中性", nullable=False
    )
    latest_summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    latest_summary_en: Mapped[str] = mapped_column(Text, default="", nullable=False)
    top_issue_tags: Mapped[str] = mapped_column(Text, default="", nullable=False)

    feedbacks = relationship("Feedback", back_populates="shop")
    metrics = relationship("ShopMetric", back_populates="shop", uselist=False)
    score_histories = relationship("ScoreHistory", back_populates="shop")
