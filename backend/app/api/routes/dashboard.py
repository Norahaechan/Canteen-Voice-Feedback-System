from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.models import AnalysisResult, Shop, ShopMetric
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=ApiResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db_session),
) -> ApiResponse:
    shops = db.query(Shop).order_by(Shop.id.asc()).all()
    metrics = db.query(ShopMetric).all()
    analysis_results = db.query(AnalysisResult).all()

    shop_scores = [
        {
            "shop_id": shop.id,
            "shop_code": shop.code,
            "shop_name": shop.name,
            "shop_name_en": shop.name_en,
            "score": shop.current_score,
        }
        for shop in shops
    ]

    issue_counter: Counter[str] = Counter()
    sentiment_counter: Counter[str] = Counter()
    trend_points: list[dict] = []

    for analysis in analysis_results:
        issue_counter.update(analysis.issue_categories)
        sentiment_counter.update([analysis.sentiment_label])

    for metric in metrics:
        trend_points.extend(metric.trend_points)

    data = {
        "shop_scores": shop_scores,
        "issue_distribution": dict(issue_counter),
        "sentiment_distribution": dict(sentiment_counter),
        "trend_points": trend_points,
    }
    return ApiResponse(data=data)
