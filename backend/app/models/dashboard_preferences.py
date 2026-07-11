import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class DashboardPreferences(Base):
    __tablename__ = "dashboard_preferences"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    layout = Column(
        JSON, nullable=False, default=list
    )  # List of widget IDs representing order
    widgets = Column(
        JSON, nullable=False, default=dict
    )  # Widget visibility / settings map
    theme = Column(String(50), nullable=False, default="dark")
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User")

    def __repr__(self) -> str:
        return f"<DashboardPreferences id={self.id} user_id={self.user_id} theme={self.theme}>"
