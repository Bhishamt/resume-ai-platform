"""AdminLog model — records every admin action for audit purposes."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class AdminLog(Base):
    """Audit log entry created whenever an administrator performs an action."""

    __tablename__ = "admin_logs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    admin_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    # e.g. "disable_account", "change_role", "delete_user", "update_settings"
    action = Column(String(100), nullable=False, index=True)
    # e.g. "user", "resume", "system_setting", "notification"
    entity = Column(String(100), nullable=False, index=True)
    # UUID string of the affected resource (may be None for system-level actions)
    entity_id = Column(String(255), nullable=True)
    # Arbitrary JSON payload — before/after values, extra context
    log_metadata = Column(JSON, nullable=False, default=dict)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationship — nullable because admin may be deleted
    admin = relationship("User", foreign_keys=[admin_id])

    __table_args__ = (
        Index("ix_admin_logs_admin_created", "admin_id", "created_at"),
        Index("ix_admin_logs_entity_action", "entity", "action"),
    )

    def __repr__(self) -> str:
        return (
            f"<AdminLog id={self.id} action={self.action} "
            f"entity={self.entity} admin_id={self.admin_id}>"
        )
