"""Notification model — in-app notifications for users and admins."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class Notification(Base):
    """In-app notification record sent to a specific user."""

    __tablename__ = "notifications"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    # e.g. "info", "success", "warning", "error", "system"
    type = Column(String(50), nullable=False, default="info")
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationship
    user = relationship("User", foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_notifications_user_read", "user_id", "is_read"),
        Index("ix_notifications_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Notification id={self.id} user_id={self.user_id} "
            f"title={self.title!r} is_read={self.is_read}>"
        )
