from __future__ import annotations

import shutil
import uuid
import wave
from pathlib import Path

from fastapi import UploadFile

from app.core.config import BACKEND_DIR, get_settings
from app.schemas.asr import AudioFileMeta


class AudioValidationError(ValueError):
    """Raised when uploaded audio does not meet service constraints."""


class AudioService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.audio_dir = BACKEND_DIR / self.settings.audio_storage_dir
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def save_upload_file(self, upload_file: UploadFile) -> AudioFileMeta:
        file_ext = self._extract_extension(
            upload_file.filename or "",
            upload_file.content_type,
        )
        if file_ext not in self.settings.allowed_audio_extensions:
            raise AudioValidationError(f"不支持的音频格式: {file_ext}")

        file_name = f"{uuid.uuid4().hex}.{file_ext}"
        target_path = self.audio_dir / file_name

        upload_file.file.seek(0)
        with target_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

        file_size = target_path.stat().st_size
        max_bytes = self.settings.audio_max_size_mb * 1024 * 1024
        if file_size > max_bytes:
            target_path.unlink(missing_ok=True)
            raise AudioValidationError(
                f"音频文件过大，最大支持 {self.settings.audio_max_size_mb}MB"
            )

        duration_seconds = self._estimate_duration(target_path, file_ext)
        if (
            duration_seconds is not None
            and duration_seconds > self.settings.audio_max_duration_seconds
        ):
            target_path.unlink(missing_ok=True)
            raise AudioValidationError(
                f"音频时长过长，最大支持 {self.settings.audio_max_duration_seconds} 秒"
            )

        return AudioFileMeta(
            file_path=str(target_path),
            file_name=file_name,
            file_ext=file_ext,
            file_size=file_size,
            duration_seconds=duration_seconds,
        )

    @staticmethod
    def _extract_extension(filename: str, content_type: str | None = None) -> str:
        suffix = Path(filename).suffix.lower().lstrip(".")
        if suffix:
            return suffix

        mime_to_ext = {
            "audio/wav": "wav",
            "audio/x-wav": "wav",
            "audio/mpeg": "mp3",
            "audio/mp3": "mp3",
            "audio/mp4": "mp4",
            "audio/x-m4a": "m4a",
            "audio/aac": "aac",
            "audio/ogg": "ogg",
            "audio/opus": "opus",
            "audio/amr": "amr",
            "audio/flac": "flac",
            "audio/webm": "webm",
        }
        return mime_to_ext.get((content_type or "").lower(), "")

    @staticmethod
    def _estimate_duration(path: Path, file_ext: str) -> float | None:
        if file_ext != "wav":
            return None

        with wave.open(str(path), "rb") as wav_file:
            frame_rate = wav_file.getframerate()
            frame_count = wav_file.getnframes()
            if frame_rate <= 0:
                return None
            return round(frame_count / float(frame_rate), 3)
