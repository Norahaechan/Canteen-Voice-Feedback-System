from pydantic import BaseModel, Field


class SentimentScores(BaseModel):
    positive: float = 0.0
    negative: float = 0.0
    neutral: float = 0.0


class AnalysisResultData(BaseModel):
    shop_name: str
    sentiment_label: str
    sentiment_scores: SentimentScores
    issue_categories: list[str] = Field(default_factory=list)
    issue_weights: dict[str, float] = Field(default_factory=dict)
    urgency: str
    summary: str
    summary_en: str = ""


class AnalysisResultEnvelope(BaseModel):
    result: AnalysisResultData
    source: str = "llm"
    fallback_used: bool = False
