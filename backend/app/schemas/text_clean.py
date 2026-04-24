from pydantic import BaseModel, Field


class TextCleanResult(BaseModel):
    original_text: str
    cleaned_text: str
    shop_candidates: list[str] = Field(default_factory=list)
    removed_fillers: list[str] = Field(default_factory=list)
