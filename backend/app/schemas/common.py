from typing import Any

from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    success: bool = True
    message: str = "ok"
    data: Any = None
    error: str | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str = "error"
    data: Any = None
    error: str
