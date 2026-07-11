import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    resume_id = Column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_description_id = Column(
        UUID(as_uuid=True),
        ForeignKey("job_descriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Category Scores (0-100)
    overall_match = Column(Integer, nullable=False, default=0)
    skill_match = Column(Integer, nullable=False, default=0)
    experience_match = Column(Integer, nullable=False, default=0)
    education_match = Column(Integer, nullable=False, default=0)
    keyword_match = Column(Integer, nullable=False, default=0)

    # Overlaps & Suggestions
    missing_skills = Column(JSON, nullable=False, default=list)
    matching_skills = Column(JSON, nullable=False, default=list)
    missing_keywords = Column(JSON, nullable=False, default=list)
    recommendations = Column(JSON, nullable=False, default=list)

    # Detailed Explainability Breakdown
    score_explanations = Column(JSON, nullable=False, default=dict)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    resume = relationship("Resume", back_populates="job_matches")
    job_description = relationship("JobDescription", back_populates="job_matches")

    def __repr__(self) -> str:
        return f"<JobMatch id={self.id} resume_id={self.resume_id} job_description_id={self.job_description_id} score={self.overall_match}>"
