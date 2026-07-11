from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class JobDescriptionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    location: Optional[str] = None
    employment_type: Optional[str] = None
    description: str = Field(..., min_length=10)
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    required_experience: Optional[str] = None
    education_requirement: Optional[str] = None


class JobDescriptionResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    company: str
    location: Optional[str]
    employment_type: Optional[str]
    description: str
    required_skills: List[str]
    preferred_skills: List[str]
    required_experience: Optional[str]
    education_requirement: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobMatchRequest(BaseModel):
    resume_id: UUID
    job_description_id: Optional[UUID] = None
    job_description: Optional[JobDescriptionCreate] = None


class JobMatchResponse(BaseModel):
    id: UUID
    resume_id: UUID
    job_description_id: UUID
    overall_match: int
    skill_match: int
    experience_match: int
    education_match: int
    keyword_match: int
    missing_skills: List[str]
    matching_skills: List[str]
    missing_keywords: List[str]
    recommendations: List[str]
    score_explanations: dict
    created_at: datetime
    job_description: Optional[JobDescriptionResponse] = None

    model_config = {"from_attributes": True}
