from fastapi import APIRouter

from app.api.routes.asr import router as asr_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.report import router as report_router
from app.api.routes.shops import router as shops_router
from app.api.routes.system import router as system_router

api_router = APIRouter()
api_router.include_router(asr_router)
api_router.include_router(feedback_router)
api_router.include_router(shops_router)
api_router.include_router(dashboard_router)
api_router.include_router(report_router)
api_router.include_router(system_router)
