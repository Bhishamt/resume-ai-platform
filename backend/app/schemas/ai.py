from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AIReviewRequest(BaseModel):
    resume_id: UUID = Field(..., description="ID of the resume to review")
    analysis_id: Optional[UUID] = Field(
        None, description="Optional ID of a specific analysis report"
    )


class AICoverLetterRequest(BaseModel):
    resume_id: UUID = Field(..., description="ID of the resume")
    job_description_id: Optional[UUID] = Field(
        None, description="Optional ID of job description to match against"
    )
    company_name: Optional[str] = Field(None, description="Optional company name")
    job_title: Optional[str] = Field(None, description="Optional job title")
    job_text: Optional[str] = Field(
        None, description="Optional raw text of the job description"
    )


class AIImproveSummaryRequest(BaseModel):
    resume_id: UUID = Field(..., description="ID of the resume")


class AIImproveProjectsRequest(BaseModel):
    resume_id: UUID = Field(..., description="ID of the resume")


class AIInterviewRequest(BaseModel):
    resume_id: UUID = Field(..., description="ID of the resume")
    job_description_id: Optional[UUID] = Field(
        None, description="Optional ID of job description"
    )


class AICareerRequest(BaseModel):
    resume_id: UUID = Field(..., description="ID of the resume")


class AIFeedbackResponse(BaseModel):
    id: UUID
    user_id: UUID
    resume_id: Optional[UUID] = None
    analysis_id: Optional[UUID] = None
    job_match_id: Optional[UUID] = None
    provider: str
    prompt_type: str
    prompt_version: str
    response: str
    token_usage: Dict[str, Any]
    response_time: float
    created_at: datetime

    model_config = {"from_attributes": True}
