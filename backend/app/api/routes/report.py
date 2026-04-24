from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.services.report_service import ReportService
from app.utils.localization import normalize_locale

router = APIRouter(prefix="/report", tags=["report"])


@router.get("/shops/{shop_id}")
def download_shop_report(
    shop_id: int,
    locale: str = "zh",
    db: Session = Depends(get_db_session),
) -> FileResponse:
    try:
        report = ReportService().generate_shop_report(
            db,
            shop_id,
            locale=normalize_locale(locale),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return FileResponse(
        report.file_path,
        media_type="application/pdf",
        filename=report.file_name,
    )
