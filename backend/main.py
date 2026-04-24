from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.init_db import init_db


configure_logging()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于大语言模型的食堂语音反馈分析系统后端服务",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", tags=["system"])
def read_root() -> dict[str, str]:
    return {
        "message": "Meal Feedback Analytics backend is running.",
        "docs_url": "/docs",
    }
