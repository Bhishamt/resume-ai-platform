from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AnalysisReportResponse(BaseModel):
    id: UUID
    resume_id: UUID
    ats_score: int
    resume_score: int
    keyword_score: int
    formatting_score: int
    experience_score: int
    education_score: int
    projects_score: int
    grammar_score: int
    strengths: list[str]
    weaknesses: list[str]
    missing_keywords: list[str]
    suggestions: list[str]
    scoring_explanations: dict
    created_at: datetime

    model_config = {"from_attributes": True}
