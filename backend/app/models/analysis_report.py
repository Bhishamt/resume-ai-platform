import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Scores
    ats_score = Column(Integer, nullable=False, default=0)
    resume_score = Column(Integer, nullable=False, default=0)
    keyword_score = Column(Integer, nullable=False, default=0)
    formatting_score = Column(Integer, nullable=False, default=0)
    experience_score = Column(Integer, nullable=False, default=0)
    education_score = Column(Integer, nullable=False, default=0)
    projects_score = Column(Integer, nullable=False, default=0)
    grammar_score = Column(Integer, nullable=False, default=0)
    
    # Heuristics Data
    strengths = Column(JSON, nullable=False, default=list)
    weaknesses = Column(JSON, nullable=False, default=list)
    missing_keywords = Column(JSON, nullable=False, default=list)
    suggestions = Column(JSON, nullable=False, default=list)
    scoring_explanations = Column(JSON, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    resume = relationship("Resume", back_populates="analysis_reports")

    def __repr__(self) -> str:
        return f"<AnalysisReport id={self.id} resume_id={self.resume_id} ats_score={self.ats_score}>"
