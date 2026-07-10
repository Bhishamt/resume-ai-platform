"""SystemSetting model — key-value store for runtime platform configuration."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class SystemSetting(Base):
    """Platform-wide key/value configuration managed by admins."""

    __tablename__ = "system_settings"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    # Unique setting key, e.g. "max_upload_size", "ai_provider", "maintenance_mode"
    key = Column(String(255), nullable=False, unique=True, index=True)
    # Stored as text; the service layer handles type coercion
    value = Column(Text, nullable=True)
    # Description shown in the UI
    description = Column(Text, nullable=True)
    # Who last modified this setting
    updated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship to the admin who last changed this setting
    updated_by_user = relationship("User", foreign_keys=[updated_by])

    __table_args__ = (UniqueConstraint("key", name="uq_system_settings_key"),)

    def __repr__(self) -> str:
        return f"<SystemSetting key={self.key} value={self.value}>"
