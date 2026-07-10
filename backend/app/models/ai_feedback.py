import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class AIFeedback(Base):
    __tablename__ = "ai_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=True, index=True)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analysis_reports.id", ondelete="CASCADE"), nullable=True, index=True)
    job_match_id = Column(UUID(as_uuid=True), ForeignKey("job_matches.id", ondelete="CASCADE"), nullable=True, index=True)
    
    provider = Column(String(50), nullable=False)
    prompt_type = Column(String(100), nullable=False)
    prompt_version = Column(String(20), nullable=False)
    response = Column(Text, nullable=False)
    token_usage = Column(JSON, nullable=False, default=dict)
    response_time = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User")
    resume = relationship("Resume")
    analysis = relationship("AnalysisReport")
    job_match = relationship("JobMatch")

    def __repr__(self) -> str:
        return f"<AIFeedback id={self.id} user_id={self.user_id} prompt_type={self.prompt_type} provider={self.provider}>"
