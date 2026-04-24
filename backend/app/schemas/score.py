from pydantic import BaseModel, Field


class ScoreResult(BaseModel):
    total_score: float
    base_score: float = 100.0
    issue_deductions: dict[str, float] = Field(default_factory=dict)
    urgency_deduction: float = 0.0
    sentiment_adjustment: float = 0.0
