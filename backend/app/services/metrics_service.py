from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AnalysisResult, Feedback, Shop, ShopMetric


class MetricsService:
    def refresh_shop_metrics(self, db: Session, shop_id: int) -> ShopMetric:
        shop = db.get(Shop, shop_id)
        if shop is None:
            raise ValueError(f"商铺不存在: {shop_id}")

        query = (
            select(Feedback, AnalysisResult)
            .join(AnalysisResult, AnalysisResult.feedback_id == Feedback.id)
            .where(Feedback.shop_id == shop_id)
            .order_by(Feedback.created_at.asc())
        )
        rows = db.execute(query).all()
        if not rows:
            raise ValueError(f"商铺 {shop.name} 缺少反馈数据，无法更新统计。")

        sentiment_distribution: dict[str, int] = {}
        issue_distribution: dict[str, int] = {}
        trend_points: list[dict[str, float | str]] = []
        scores: list[float] = []

        for feedback, analysis in rows:
            sentiment_distribution[analysis.sentiment_label] = (
                sentiment_distribution.get(analysis.sentiment_label, 0) + 1
            )
            for category in analysis.issue_categories:
                issue_distribution[category] = issue_distribution.get(category, 0) + 1
            trend_points.append(
                {
                    "date": feedback.created_at.strftime("%Y-%m-%d"),
                    "score": analysis.total_score,
                }
            )
            scores.append(analysis.total_score)

        average_score = round(sum(scores) / len(scores), 2)
        top_tags = sorted(
            issue_distribution, key=issue_distribution.get, reverse=True
        )[:3]

        shop.current_score = average_score
        shop.feedback_count = len(rows)
        shop.primary_sentiment = max(
            sentiment_distribution, key=sentiment_distribution.get
        )
        shop.latest_summary = rows[-1][1].summary
        shop.latest_summary_en = rows[-1][1].summary_en
        shop.top_issue_tags = ",".join(top_tags)

        metric = db.execute(
            select(ShopMetric).where(ShopMetric.shop_id == shop_id)
        ).scalar_one_or_none()
        if metric is None:
            metric = ShopMetric(shop_id=shop_id)
            db.add(metric)

        metric.average_score = average_score
        metric.sentiment_distribution = sentiment_distribution
        metric.issue_distribution = issue_distribution
        metric.trend_points = trend_points
        metric.updated_at = datetime.utcnow()
        db.flush()
        return metric
