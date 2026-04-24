from pydantic import BaseModel, Field

from app.schemas.analysis import SentimentScores


class FeedbackAnalyzeRequest(BaseModel):
    text: str = Field(min_length=1)
    audio_path: str = ""
    language: str = "unknown"


class FeedbackOverviewResponse(BaseModel):
    feedback_id: int
    shop_id: int | None
    shop_code: str | None = None
    shop_name: str
    shop_name_en: str = ""
    sentiment_label: str
    sentiment_scores: SentimentScores = Field(default_factory=SentimentScores)
    issue_categories: list[str] = Field(default_factory=list)
    issue_weights: dict[str, float] = Field(default_factory=dict)
    urgency: str
    total_score: float
    summary: str
    summary_en: str = ""
    cleaned_text: str
    fallback_used: bool = False
    analysis_source: str = "llm"
