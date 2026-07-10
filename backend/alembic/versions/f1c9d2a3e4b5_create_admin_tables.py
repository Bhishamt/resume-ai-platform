"""create_admin_tables

Revision ID: f1c9d2a3e4b5
Revises: 48a66451e71b
Create Date: 2026-07-10 22:10:00.000000

Creates three tables required for Phase 9 — Enterprise Admin Panel:
  - admin_logs     : audit trail for all admin actions
  - system_settings: key-value platform configuration store
  - notifications  : in-app notification centre

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f1c9d2a3e4b5"
down_revision: Union[str, Sequence[str], None] = "48a66451e71b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create admin_logs, system_settings, and notifications tables."""

    # ------------------------------------------------------------------
    # admin_logs
    # ------------------------------------------------------------------
    op.create_table(
        "admin_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "admin_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.String(255), nullable=True),
        sa.Column(
            "log_metadata",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_admin_logs_admin_id", "admin_logs", ["admin_id"])
    op.create_index("ix_admin_logs_action", "admin_logs", ["action"])
    op.create_index("ix_admin_logs_entity", "admin_logs", ["entity"])
    op.create_index("ix_admin_logs_created_at", "admin_logs", ["created_at"])
    op.create_index(
        "ix_admin_logs_admin_created",
        "admin_logs",
        ["admin_id", "created_at"],
    )
    op.create_index(
        "ix_admin_logs_entity_action",
        "admin_logs",
        ["entity", "action"],
    )

    # ------------------------------------------------------------------
    # system_settings
    # ------------------------------------------------------------------
    op.create_table(
        "system_settings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("key", sa.String(255), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "updated_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.UniqueConstraint("key", name="uq_system_settings_key"),
    )
    op.create_index("ix_system_settings_key", "system_settings", ["key"], unique=True)

    # ------------------------------------------------------------------
    # notifications
    # ------------------------------------------------------------------
    op.create_table(
        "notifications",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("type", sa.String(50), nullable=False, server_default="info"),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])
    op.create_index(
        "ix_notifications_user_read",
        "notifications",
        ["user_id", "is_read"],
    )
    op.create_index(
        "ix_notifications_user_created",
        "notifications",
        ["user_id", "created_at"],
    )

    # ------------------------------------------------------------------
    # Seed default system settings
    # ------------------------------------------------------------------
    op.execute(
        """
        INSERT INTO system_settings (id, key, value, description, updated_at)
        VALUES
          (gen_random_uuid(), 'max_upload_size_mb', '10',
           'Maximum resume upload size in megabytes', NOW()),
          (gen_random_uuid(), 'maintenance_mode', 'false',
           'Put the platform in read-only maintenance mode', NOW()),
          (gen_random_uuid(), 'ai_provider', 'groq',
           'Default AI provider for analysis requests', NOW()),
          (gen_random_uuid(), 'max_resumes_per_user', '20',
           'Maximum number of resumes a single user may upload', NOW()),
          (gen_random_uuid(), 'allow_registrations', 'true',
           'Allow new user registrations', NOW()),
          (gen_random_uuid(), 'session_timeout_minutes', '30',
           'JWT access token expiry in minutes', NOW())
        ON CONFLICT (key) DO NOTHING;
        """
    )


def downgrade() -> None:
    """Drop admin_logs, system_settings, and notifications tables."""
    op.drop_table("notifications")
    op.drop_table("system_settings")
    op.drop_table("admin_logs")
