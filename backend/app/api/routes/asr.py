from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.common import ApiResponse
from app.schemas.asr import (
    AsrTaskQueryResponse,
    AsrTaskSubmitRequest,
    AsrUploadBridgeResponse,
)
from app.services.asr_service import AliyunAsrService, AsrServiceError
from app.services.audio_service import AudioService, AudioValidationError
from app.services.oss_service import OssService, OssServiceError

router = APIRouter(prefix="/asr", tags=["asr"])


@router.post("/tasks", response_model=ApiResponse)
def submit_asr_task(payload: AsrTaskSubmitRequest) -> ApiResponse:
    service = AliyunAsrService()
    try:
        result = service.submit_transcription_task(
            file_urls=payload.file_urls,
            language_hints=payload.language_hints,
        )
    except AsrServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ApiResponse(data=result)


@router.get("/tasks/{task_id}", response_model=ApiResponse)
def query_asr_task(task_id: str) -> ApiResponse:
    service = AliyunAsrService()
    try:
        result = service.query_task(task_id)
    except AsrServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    extracted_text = service.extract_text_from_task_result(result)
    parsed = AsrTaskQueryResponse(
        task_id=task_id,
        task_status=result.get("output", {}).get("task_status", "UNKNOWN"),
        results=result.get("output", {}).get("results", []),
        transcript_text=extracted_text,
    )
    return ApiResponse(data=parsed.model_dump())


@router.post("/upload-and-submit", response_model=ApiResponse)
def upload_and_submit_asr_task(file: UploadFile = File(...)) -> ApiResponse:
    try:
        audio_meta = AudioService().save_upload_file(file)
        object_key, oss_url = OssService().upload_file(
            audio_meta.file_path,
            file.filename or audio_meta.file_name,
        )
        task_result = AliyunAsrService().submit_transcription_task([oss_url])
    except (AudioValidationError, OssServiceError, AsrServiceError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    output = task_result.get("output", {})
    response = AsrUploadBridgeResponse(
        local_file_name=audio_meta.file_name,
        local_file_path=audio_meta.file_path,
        oss_object_key=object_key,
        oss_url=oss_url,
        task_id=output.get("task_id", ""),
        task_status=output.get("task_status", "UNKNOWN"),
    )
    return ApiResponse(data=response.model_dump())
