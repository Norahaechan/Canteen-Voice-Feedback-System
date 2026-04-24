from pathlib import Path
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = BACKEND_DIR / "meal_feedback.db"


class Settings(BaseSettings):
    app_name: str = Field(default="Meal Feedback Analytics API")
    app_version: str = Field(default="0.1.0")
    api_prefix: str = Field(default="/api/v1")
    debug: bool = Field(default=True)
    database_url: str = Field(default=f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}")
    audio_storage_dir: str = Field(default="storage/audio")
    report_storage_dir: str = Field(default="reports")
    allowed_audio_extensions: list[str] = Field(
        default_factory=lambda: [
            "wav",
            "mp3",
            "m4a",
            "aac",
            "ogg",
            "opus",
            "amr",
            "flac",
            "mp4",
            "webm",
        ]
    )
    audio_max_size_mb: int = Field(default=512)
    audio_max_duration_seconds: int = Field(default=7200)
    oss_endpoint: str = Field(default="https://oss-cn-beijing.aliyuncs.com")
    oss_bucket_name: str = Field(default="")
    oss_access_key_id: str = Field(default="")
    oss_access_key_secret: str = Field(default="")
    oss_url_expire_seconds: int = Field(default=86400)
    oss_object_prefix: str = Field(default="meal-feedback/audio")
    dashscope_api_key: str = Field(default="")
    aliyun_asr_model: str = Field(default="paraformer-v2")
    aliyun_asr_submit_url: str = Field(
        default="https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription"
    )
    aliyun_asr_task_url_template: str = Field(
        default="https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    )
    llm_model_name: str = Field(default="qwen3.5-plus")
    llm_api_base: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @classmethod
    def parse_env_var(cls, field_name: str, raw_value: str):
        if field_name in {"cors_origins", "allowed_audio_extensions"}:
            return [item.strip() for item in raw_value.split(",") if item.strip()]
        return raw_value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
