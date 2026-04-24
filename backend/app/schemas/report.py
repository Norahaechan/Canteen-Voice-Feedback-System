from pydantic import BaseModel


class ReportMeta(BaseModel):
    file_name: str
    file_path: str
    generated_at: str
