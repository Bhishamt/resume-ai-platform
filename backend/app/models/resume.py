import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_status = Column(String(50), nullable=False, default="pending")  # pending, success, failed
    storage_path = Column(String(500), nullable=False)
    parsed_text = Column(Text, nullable=True)
    upload_date = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="resumes")
    upload_histories = relationship("UploadHistory", back_populates="resume", cascade="all, delete-orphan")
    analysis_reports = relationship("AnalysisReport", back_populates="resume", cascade="all, delete-orphan")


    def __repr__(self) -> str:
        return f"<Resume id={self.id} title={self.title} user_id={self.user_id}>"
