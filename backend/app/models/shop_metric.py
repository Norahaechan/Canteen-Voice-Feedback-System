from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ShopMetric(Base):
    __tablename__ = "shop_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    shop_id: Mapped[int] = mapped_column(
        ForeignKey("shops.id"), unique=True, nullable=False
    )
    average_score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    sentiment_distribution: Mapped[dict[str, int]] = mapped_column(
        JSON, default=dict, nullable=False
    )
    issue_distribution: Mapped[dict[str, int]] = mapped_column(
        JSON, default=dict, nullable=False
    )
    trend_points: Mapped[list[dict[str, float | str]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    shop = relationship("Shop", back_populates="metrics")
