from pydantic import BaseModel, Field


class AudioFileMeta(BaseModel):
    file_path: str
    file_name: str
    file_ext: str
    file_size: int
    duration_seconds: float | None = None


class AsrResult(BaseModel):
    text: str = Field(default="")
    language: str = Field(default="unknown")
    duration_ms: int = Field(default=0)
    task_id: str = Field(default="")
    provider: str = Field(default="aliyun-nls")


class AsrTaskSubmitRequest(BaseModel):
    file_urls: list[str] = Field(min_length=1, max_length=100)
    language_hints: list[str] = Field(default_factory=lambda: ["zh", "en"])


class AsrTaskQueryResponse(BaseModel):
    task_id: str
    task_status: str
    results: list[dict] = Field(default_factory=list)
    transcript_text: str = ""


class AsrUploadBridgeResponse(BaseModel):
    local_file_name: str
    local_file_path: str
    oss_object_key: str
    oss_url: str
    task_id: str
    task_status: str
