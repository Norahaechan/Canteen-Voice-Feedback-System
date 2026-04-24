import json
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import AnalysisResult, Feedback, ScoreHistory, Shop, ShopMetric
from app.utils.localization import build_summary_en

SEED_DIR = BACKEND_DIR / "data" / "seeds"
SHOPS_FILE = SEED_DIR / "shops.json"
FEEDBACKS_FILE = SEED_DIR / "sample_feedbacks.json"


def ensure_shop_columns() -> None:
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns("shops")}
    required_columns = {
        "code": "ALTER TABLE shops ADD COLUMN code VARCHAR(100) NOT NULL DEFAULT ''",
        "name_en": "ALTER TABLE shops ADD COLUMN name_en VARCHAR(120) NOT NULL DEFAULT ''",
        "category_en": "ALTER TABLE shops ADD COLUMN category_en VARCHAR(80) NOT NULL DEFAULT ''",
        "aliases_en": "ALTER TABLE shops ADD COLUMN aliases_en TEXT NOT NULL DEFAULT ''",
        "latest_summary_en": "ALTER TABLE shops ADD COLUMN latest_summary_en TEXT NOT NULL DEFAULT ''",
    }
    with engine.begin() as connection:
        for column_name, statement in required_columns.items():
            if column_name not in columns:
                connection.execute(text(statement))


def load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def seed_shops(db: Session) -> dict[str, Shop]:
    shops_payload = load_json(SHOPS_FILE)
    existing_shops = {
        shop.name: shop for shop in db.execute(select(Shop)).scalars().all()
    }

    for item in shops_payload:
        shop = existing_shops.get(item["name"])
        aliases = ",".join(item.get("aliases", []))
        aliases_en = ",".join(item.get("aliases_en", []))
        if shop is None:
            shop = Shop(
                code=item["code"],
                name=item["name"],
                name_en=item.get("name_en", ""),
                category=item["category"],
                category_en=item.get("category_en", ""),
                aliases=aliases,
                aliases_en=aliases_en,
                current_score=item.get("current_score", 100.0),
                feedback_count=item.get("feedback_count", 0),
                primary_sentiment=item.get("primary_sentiment", "中性"),
                latest_summary=item.get("latest_summary", ""),
                latest_summary_en=item.get("latest_summary_en", ""),
                top_issue_tags=",".join(item.get("top_issue_tags", [])),
            )
            db.add(shop)
            existing_shops[item["name"]] = shop
        else:
            shop.code = item["code"]
            shop.category = item["category"]
            shop.name_en = item.get("name_en", shop.name_en)
            shop.category_en = item.get("category_en", shop.category_en)
            shop.aliases = aliases
            shop.aliases_en = aliases_en
            shop.current_score = item.get("current_score", shop.current_score)
            shop.feedback_count = item.get("feedback_count", shop.feedback_count)
            shop.primary_sentiment = item.get(
                "primary_sentiment", shop.primary_sentiment
            )
            shop.latest_summary = item.get("latest_summary", shop.latest_summary)
            shop.latest_summary_en = item.get("latest_summary_en", shop.latest_summary_en)
            shop.top_issue_tags = ",".join(item.get("top_issue_tags", []))

    db.flush()
    return existing_shops


def seed_feedbacks(db: Session, shops: dict[str, Shop]) -> None:
    feedback_payload = load_json(FEEDBACKS_FILE)
    existing_feedbacks = {
        feedback.original_text: feedback
        for feedback in db.execute(select(Feedback)).scalars().all()
    }

    for item in feedback_payload:
        existing_feedback = existing_feedbacks.get(item["original_text"])
        if existing_feedback is not None:
            analysis = db.execute(
                select(AnalysisResult).where(
                    AnalysisResult.feedback_id == existing_feedback.id
                )
            ).scalar_one_or_none()
            if analysis is not None and not analysis.summary_en:
                target_shop = shops.get(item["shop_name"])
                analysis.summary_en = item.get("summary_en", "") or build_summary_en(
                    shop_name=item["shop_name"],
                    shop_name_en=target_shop.name_en if target_shop else "",
                    summary=item.get("summary", ""),
                    sentiment_label=item["sentiment_label"],
                    issue_categories=item["issue_categories"],
                    urgency=item["urgency"],
                )
            continue

        shop = shops[item["shop_name"]]
        created_at = datetime.fromisoformat(item["created_at"])
        feedback = Feedback(
            shop_id=shop.id,
            audio_path=item.get("audio_path", ""),
            original_text=item["original_text"],
            cleaned_text=item["cleaned_text"],
            language=item.get("language", "zh"),
            created_at=created_at,
        )
        db.add(feedback)
        db.flush()

        analysis = AnalysisResult(
            feedback_id=feedback.id,
            shop_name=item["shop_name"],
            sentiment_label=item["sentiment_label"],
            sentiment_positive=item["sentiment_scores"]["positive"],
            sentiment_negative=item["sentiment_scores"]["negative"],
            sentiment_neutral=item["sentiment_scores"]["neutral"],
            issue_categories=item["issue_categories"],
            issue_weights=item["issue_weights"],
            urgency=item["urgency"],
            summary=item["summary"],
            summary_en=item.get("summary_en", "")
            or build_summary_en(
                shop_name=item["shop_name"],
                shop_name_en=shop.name_en,
                summary=item.get("summary", ""),
                sentiment_label=item["sentiment_label"],
                issue_categories=item["issue_categories"],
                urgency=item["urgency"],
            ),
            total_score=item["total_score"],
            created_at=created_at,
        )
        db.add(analysis)

        history = ScoreHistory(
            shop_id=shop.id,
            score=item["total_score"],
            sentiment_label=item["sentiment_label"],
            recorded_at=created_at,
        )
        db.add(history)

    db.flush()

    for shop_name, shop in shops.items():
        shop_entries = [
            item for item in feedback_payload if item["shop_name"] == shop_name
        ]
        if not shop_entries:
            continue

        latest_entry = max(shop_entries, key=lambda entry: entry["created_at"])
        sentiment_distribution: dict[str, int] = {}
        issue_distribution: dict[str, int] = {}
        trend_points: list[dict[str, float | str]] = []

        for entry in shop_entries:
            sentiment = entry["sentiment_label"]
            sentiment_distribution[sentiment] = (
                sentiment_distribution.get(sentiment, 0) + 1
            )
            for category in entry["issue_categories"]:
                issue_distribution[category] = issue_distribution.get(category, 0) + 1
            trend_points.append(
                {
                    "date": entry["created_at"][:10],
                    "score": entry["total_score"],
                }
            )

        average_score = round(
            sum(entry["total_score"] for entry in shop_entries) / len(shop_entries), 2
        )

        shop.current_score = average_score
        shop.feedback_count = len(shop_entries)
        shop.primary_sentiment = max(
            sentiment_distribution, key=sentiment_distribution.get
        )
        shop.latest_summary = latest_entry["summary"]
        shop.latest_summary_en = latest_entry.get("summary_en", "")
        top_tags = sorted(
            issue_distribution, key=issue_distribution.get, reverse=True
        )[:3]
        shop.top_issue_tags = ",".join(top_tags)


def ensure_analysis_result_columns() -> None:
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns("analysis_results")}
    required_columns = {
        "summary_en": "ALTER TABLE analysis_results ADD COLUMN summary_en TEXT NOT NULL DEFAULT ''",
    }
    with engine.begin() as connection:
        for column_name, statement in required_columns.items():
            if column_name not in columns:
                connection.execute(text(statement))


def backfill_analysis_summary_en(db: Session) -> None:
    rows = (
        db.execute(
            select(AnalysisResult, Feedback, Shop)
            .join(Feedback, Feedback.id == AnalysisResult.feedback_id)
            .outerjoin(Shop, Shop.id == Feedback.shop_id)
        )
        .all()
    )
    for analysis, _feedback, shop in rows:
        if analysis.summary_en.strip():
            continue
        analysis.summary_en = build_summary_en(
            shop_name=analysis.shop_name,
            shop_name_en=shop.name_en if shop else "",
            summary=analysis.summary,
            sentiment_label=analysis.sentiment_label,
            issue_categories=analysis.issue_categories,
            urgency=analysis.urgency,
        )

    for shop in db.execute(select(Shop)).scalars().all():
        if shop.latest_summary_en.strip():
            continue
        latest_analysis = (
            db.execute(
                select(AnalysisResult)
                .join(Feedback, Feedback.id == AnalysisResult.feedback_id)
                .where(Feedback.shop_id == shop.id)
                .order_by(AnalysisResult.created_at.desc())
            )
            .scalars()
            .first()
        )
        if latest_analysis is not None:
            shop.latest_summary_en = latest_analysis.summary_en


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_shop_columns()
    ensure_analysis_result_columns()
    with SessionLocal() as db:
        shops = seed_shops(db)
        seed_feedbacks(db, shops)
        backfill_analysis_summary_en(db)
        db.commit()


if __name__ == "__main__":
    init_db()
