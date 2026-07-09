"""Pydantic validation schemas for Resume and History operations."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class ResumeResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    original_filename: str
    stored_filename: str
    file_type: str
    file_size: int
    upload_status: str
    storage_path: str
    parsed_text: Optional[str] = None
    upload_date: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class PaginatedResumes(BaseModel):
    items: list[ResumeResponse]
    total: int
    page: int
    limit: int

class UploadHistoryResponse(BaseModel):
    id: UUID
    user_id: UUID
    resume_id: UUID
    action: str
    timestamp: datetime
    resume_title: Optional[str] = None

    model_config = {"from_attributes": True}

class ResumeUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Update resume title")
