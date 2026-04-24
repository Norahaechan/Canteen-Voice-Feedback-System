from __future__ import annotations

import logging
from typing import Any

import requests

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class AsrServiceError(RuntimeError):
    """Raised when Alibaba ASR fails."""


class AliyunAsrService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def submit_transcription_task(
        self, file_urls: list[str], language_hints: list[str] | None = None
    ) -> dict[str, Any]:
        api_key = self._resolve_api_key()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        }
        payload = {
            "model": self.settings.aliyun_asr_model,
            "input": {"file_urls": file_urls},
            "parameters": {
                "language_hints": language_hints or ["zh", "en"],
                "disfluency_removal_enabled": False,
                "timestamp_alignment_enabled": True,
            },
        }
        response = requests.post(
            self.settings.aliyun_asr_submit_url,
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        output = data.get("output", {})
        if not output.get("task_id"):
            raise AsrServiceError(f"阿里长音频转写任务提交失败: {data}")
        return data

    def query_task(self, task_id: str) -> dict[str, Any]:
        api_key = self._resolve_api_key()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        }
        task_url = self.settings.aliyun_asr_task_url_template.format(task_id=task_id)
        response = requests.post(task_url, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def extract_text_from_task_result(task_payload: dict[str, Any]) -> str:
        results = task_payload.get("output", {}).get("results", [])
        text_parts: list[str] = []
        for result in results:
            transcription_url = result.get("transcription_url")
            if transcription_url:
                response = requests.get(transcription_url, timeout=60)
                response.raise_for_status()
                transcription_payload = response.json()
                for transcript in transcription_payload.get("transcripts", []):
                    text = str(transcript.get("text", "")).strip()
                    if text:
                        text_parts.append(text)
                continue

            transcript = result.get("transcript")
            if transcript:
                text_parts.append(str(transcript).strip())
        return "\n".join(part for part in text_parts if part).strip()

    def _resolve_api_key(self) -> str:
        api_key = self.settings.dashscope_api_key
        if not api_key:
            raise AsrServiceError("未配置 DASHSCOPE_API_KEY，无法调用阿里长音频转写。")
        return api_key
