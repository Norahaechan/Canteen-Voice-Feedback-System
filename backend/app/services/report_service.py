from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR, get_settings
from app.models import Shop, ShopMetric
from app.schemas.report import ReportMeta
from app.utils.localization import (
    format_distribution,
    normalize_locale,
    translate_issue_category,
    translate_sentiment,
)


class ReportService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.report_dir = BACKEND_DIR / self.settings.report_storage_dir
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def generate_shop_report(
        self,
        db: Session,
        shop_id: int,
        locale: str = "zh",
    ) -> ReportMeta:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.pdfgen import canvas

        shop = db.get(Shop, shop_id)
        if shop is None:
            raise ValueError("商铺不存在。")

        from reportlab.lib.utils import simpleSplit

        normalized_locale = normalize_locale(locale)
        use_english = normalized_locale == "en"
        if not use_english:
            pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        metric = (
            db.query(ShopMetric).filter(ShopMetric.shop_id == shop_id).one_or_none()
        )
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        locale_suffix = "en" if use_english else "zh"
        file_name = f"shop_report_{shop_id}_{locale_suffix}_{timestamp}.pdf"
        file_path = self.report_dir / file_name

        pdf = canvas.Canvas(str(file_path), pagesize=A4)
        title_font = "Helvetica-Bold" if use_english else "STSong-Light"
        body_font = "Helvetica" if use_english else "STSong-Light"
        pdf.setFont(title_font, 16)
        pdf.drawString(
            40,
            800,
            "Cafeteria Feedback Analysis Report"
            if use_english
            else "食堂反馈分析报告",
        )
        pdf.setFont(body_font, 11)

        if use_english:
            lines = [
                f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Shop: {shop.name_en or shop.name}",
                f"Category: {shop.category_en or shop.category}",
                f"Overall score: {shop.current_score}",
                f"Feedback count: {shop.feedback_count}",
                f"Primary sentiment: {translate_sentiment(shop.primary_sentiment)}",
                f"Top issue tags: {', '.join(translate_issue_category(tag) for tag in shop.top_issue_tags.split(',') if tag) or 'None'}",
                f"Latest summary: {shop.latest_summary_en or 'No summary available.'}",
            ]
        else:
            lines = [
                f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"商铺名称: {shop.name}",
                f"窗口类别: {shop.category}",
                f"当前综合评分: {shop.current_score}",
                f"反馈数量: {shop.feedback_count}",
                f"主要情感倾向: {shop.primary_sentiment}",
                f"高频问题标签: {shop.top_issue_tags or '暂无'}",
                f"最新摘要: {shop.latest_summary or '暂无'}",
            ]
        if metric is not None:
            if use_english:
                lines.extend(
                    [
                        "Sentiment distribution: "
                        + format_distribution(
                            metric.sentiment_distribution,
                            key_formatter=translate_sentiment,
                        ),
                        "Issue distribution: "
                        + format_distribution(
                            metric.issue_distribution,
                            key_formatter=translate_issue_category,
                        ),
                        f"Trend points: {len(metric.trend_points)}",
                    ]
                )
            else:
                lines.extend(
                    [
                        f"情感分布: {metric.sentiment_distribution}",
                        f"问题分布: {metric.issue_distribution}",
                        f"趋势点数: {len(metric.trend_points)}",
                    ]
                )

        y = 760
        max_width = 515
        for line in lines:
            wrapped_lines = simpleSplit(line, body_font, 11, max_width)
            for wrapped_line in wrapped_lines:
                if y < 60:
                    pdf.showPage()
                    pdf.setFont(body_font, 11)
                    y = 800
                pdf.drawString(40, y, wrapped_line)
                y -= 22

        pdf.save()
        return ReportMeta(
            file_name=file_name,
            file_path=str(file_path),
            generated_at=datetime.now().isoformat(timespec="seconds"),
        )
