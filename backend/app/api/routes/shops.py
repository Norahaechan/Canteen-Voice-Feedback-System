from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.models import Feedback, Shop, ShopMetric
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/shops", tags=["shops"])


def _serialize_shop_base(shop: Shop) -> dict:
    return {
        "id": shop.id,
        "code": shop.code,
        "name": shop.name,
        "name_en": shop.name_en,
        "category": shop.category,
        "category_en": shop.category_en,
        "latest_summary_en": shop.latest_summary_en,
    }


def _build_feedback_windows(
    feedbacks: list[Feedback],
) -> tuple[int, int]:
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    today_count = 0
    week_count = 0

    for feedback in feedbacks:
        created_at = feedback.created_at
        if created_at.date() == now.date():
            today_count += 1
        if created_at >= week_ago:
            week_count += 1

    return today_count, week_count


@router.get("", response_model=ApiResponse)
def list_shops(db: Session = Depends(get_db_session)) -> ApiResponse:
    shops = db.query(Shop).order_by(Shop.id.asc()).all()
    metrics = {metric.shop_id: metric for metric in db.query(ShopMetric).all()}
    feedback_rows = db.query(Feedback).order_by(Feedback.created_at.desc()).all()
    feedback_map: dict[int, list[Feedback]] = {}

    for feedback in feedback_rows:
        if feedback.shop_id is None:
            continue
        feedback_map.setdefault(feedback.shop_id, []).append(feedback)

    data = []
    for shop in shops:
        today_count, week_count = _build_feedback_windows(feedback_map.get(shop.id, []))
        data.append(
            {
                **_serialize_shop_base(shop),
                "current_score": shop.current_score,
                "feedback_count": shop.feedback_count,
                "today_feedback_count": today_count,
                "week_feedback_count": week_count,
                "primary_sentiment": shop.primary_sentiment,
                "latest_summary": shop.latest_summary,
                "top_issue_tags": [tag for tag in shop.top_issue_tags.split(",") if tag],
                "mini_trend_points": (
                    metrics[shop.id].trend_points[-6:]
                    if shop.id in metrics
                    else []
                ),
            }
        )
    return ApiResponse(data=data)


@router.get("/{shop_id}", response_model=ApiResponse)
def get_shop_detail(shop_id: int, db: Session = Depends(get_db_session)) -> ApiResponse:
    shop = db.get(Shop, shop_id)
    if shop is None:
        raise HTTPException(status_code=404, detail="商铺不存在")
    metric = db.query(ShopMetric).filter(ShopMetric.shop_id == shop_id).one_or_none()
    feedbacks = (
        db.query(Feedback)
        .filter(Feedback.shop_id == shop_id)
        .order_by(Feedback.created_at.desc())
        .all()
    )
    today_count, week_count = _build_feedback_windows(feedbacks)
    data = {
        **_serialize_shop_base(shop),
        "current_score": shop.current_score,
        "feedback_count": shop.feedback_count,
        "today_feedback_count": today_count,
        "week_feedback_count": week_count,
        "primary_sentiment": shop.primary_sentiment,
        "latest_summary": shop.latest_summary,
        "top_issue_tags": [tag for tag in shop.top_issue_tags.split(",") if tag],
        "metrics": metric.sentiment_distribution if metric else {},
        "issue_distribution": metric.issue_distribution if metric else {},
        "trend_points": metric.trend_points if metric else [],
        "mini_trend_points": metric.trend_points[-6:] if metric else [],
    }
    return ApiResponse(data=data)
