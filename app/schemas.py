from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class DocumentOut(BaseModel):
    id: int
    original_filename: str
    category: str
    hashtags: str
    description: str
    notes: str
    is_private: bool
    uploaded_by: int
    uploaded_at: datetime
    document_date: Optional[datetime] = None
    uploader_name: str = ""

    class Config:
        from_attributes = True
