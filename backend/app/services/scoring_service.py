from app.schemas.analysis import AnalysisResultData
from app.schemas.score import ScoreResult

ISSUE_PENALTIES = {
    "卫生": 15,
    "服务态度": 10,
    "排队效率": 8,
    "口味": 8,
    "分量": 7,
    "食材新鲜度": 12,
    "价格": 6,
    "其他": 5,
}

URGENCY_PENALTIES = {"高": 10, "中": 5, "低": 0}
SENTIMENT_ADJUSTMENTS = {"正面": 3, "中性": -2, "负面": -6}


class ScoringService:
    def calculate(self, analysis: AnalysisResultData) -> ScoreResult:
        base_score = 100.0
        issue_deductions: dict[str, float] = {}

        for category in analysis.issue_categories:
            weight = analysis.issue_weights.get(category, 0.0)
            penalty_base = ISSUE_PENALTIES.get(category, ISSUE_PENALTIES["其他"])
            issue_deductions[category] = round(weight * penalty_base, 2)

        issue_total = sum(issue_deductions.values())
        urgency_deduction = float(URGENCY_PENALTIES.get(analysis.urgency, 0))
        sentiment_adjustment = float(
            SENTIMENT_ADJUSTMENTS.get(analysis.sentiment_label, 0)
        )
        total_score = round(
            max(0.0, min(100.0, base_score - issue_total - urgency_deduction + sentiment_adjustment)),
            2,
        )

        return ScoreResult(
            total_score=total_score,
            base_score=base_score,
            issue_deductions=issue_deductions,
            urgency_deduction=urgency_deduction,
            sentiment_adjustment=sentiment_adjustment,
        )
