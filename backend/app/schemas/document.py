from pydantic import BaseModel, Field
from datetime import datetime


class DocumentResponse(BaseModel):
    id: int
    user_id: int | None = None
    title: str
    file_type: str
    file_path: str
    file_size: int | None = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True



class DocumentUpdate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
        description="New document title"
    )


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]