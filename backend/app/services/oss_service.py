from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.core.config import get_settings


class OssServiceError(RuntimeError):
    """Raised when OSS upload or URL signing fails."""


class OssService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def upload_file(self, local_path: str, original_name: str) -> tuple[str, str]:
        if not self.settings.oss_bucket_name:
            raise OssServiceError("未配置 OSS_BUCKET_NAME。")
        if (
            not self.settings.oss_access_key_id
            or not self.settings.oss_access_key_secret
        ):
            raise OssServiceError(
                "未配置 OSS_ACCESS_KEY_ID / OSS_ACCESS_KEY_SECRET。"
            )

        import oss2

        auth = oss2.Auth(
            self.settings.oss_access_key_id,
            self.settings.oss_access_key_secret,
        )
        bucket = oss2.Bucket(
            auth,
            self.settings.oss_endpoint,
            self.settings.oss_bucket_name,
        )

        local_file = Path(local_path)
        suffix = local_file.suffix
        safe_name = Path(original_name or local_file.name).stem.replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        object_key = (
            f"{self.settings.oss_object_prefix}/{timestamp}_{safe_name}{suffix}"
        )
        bucket.put_object_from_file(object_key, str(local_file))
        signed_url = bucket.sign_url(
            "GET",
            object_key,
            self.settings.oss_url_expire_seconds,
        )
        return object_key, signed_url
