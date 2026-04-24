from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.models import AnalysisResult, Feedback, ScoreHistory, Shop
from app.schemas.common import ApiResponse
from app.schemas.feedback import FeedbackAnalyzeRequest, FeedbackOverviewResponse
from app.services.llm_analysis_service import LlmAnalysisService
from app.services.metrics_service import MetricsService
from app.services.scoring_service import ScoringService
from app.services.text_clean_service import TextCleanService

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/analyze", response_model=ApiResponse)
def analyze_feedback(
    payload: FeedbackAnalyzeRequest,
    db: Session = Depends(get_db_session),
) -> ApiResponse:
    clean_result = TextCleanService().clean_text(payload.text)
    analysis_envelope = LlmAnalysisService().analyze(clean_result)
    score_result = ScoringService().calculate(analysis_envelope.result)

    target_shop = None
    if analysis_envelope.result.shop_name != "未知商铺":
        target_shop = (
            db.query(Shop)
            .filter(Shop.name == analysis_envelope.result.shop_name)
            .one_or_none()
        )

    feedback = Feedback(
        shop_id=target_shop.id if target_shop else None,
        audio_path=payload.audio_path,
        original_text=payload.text,
        cleaned_text=clean_result.cleaned_text,
        language=payload.language,
        created_at=datetime.utcnow(),
    )
    db.add(feedback)
    db.flush()

    analysis = AnalysisResult(
        feedback_id=feedback.id,
        shop_name=analysis_envelope.result.shop_name,
        sentiment_label=analysis_envelope.result.sentiment_label,
        sentiment_positive=analysis_envelope.result.sentiment_scores.positive,
        sentiment_negative=analysis_envelope.result.sentiment_scores.negative,
        sentiment_neutral=analysis_envelope.result.sentiment_scores.neutral,
        issue_categories=analysis_envelope.result.issue_categories,
        issue_weights=analysis_envelope.result.issue_weights,
        urgency=analysis_envelope.result.urgency,
        summary=analysis_envelope.result.summary,
        summary_en=analysis_envelope.result.summary_en,
        total_score=score_result.total_score,
        created_at=datetime.utcnow(),
    )
    db.add(analysis)

    if target_shop is not None:
        db.add(
            ScoreHistory(
                shop_id=target_shop.id,
                score=score_result.total_score,
                sentiment_label=analysis_envelope.result.sentiment_label,
                recorded_at=datetime.utcnow(),
            )
        )
        db.flush()
        MetricsService().refresh_shop_metrics(db, target_shop.id)

    db.commit()

    response = FeedbackOverviewResponse(
        feedback_id=feedback.id,
        shop_id=target_shop.id if target_shop else None,
        shop_code=target_shop.code if target_shop else None,
        shop_name=analysis_envelope.result.shop_name,
        shop_name_en=target_shop.name_en if target_shop else "",
        sentiment_label=analysis_envelope.result.sentiment_label,
        sentiment_scores=analysis_envelope.result.sentiment_scores,
        issue_categories=analysis_envelope.result.issue_categories,
        issue_weights=analysis_envelope.result.issue_weights,
        urgency=analysis_envelope.result.urgency,
        total_score=score_result.total_score,
        summary=analysis_envelope.result.summary,
        summary_en=analysis_envelope.result.summary_en,
        cleaned_text=clean_result.cleaned_text,
        fallback_used=analysis_envelope.fallback_used,
        analysis_source=analysis_envelope.source,
    )
    return ApiResponse(data=response.model_dump())
