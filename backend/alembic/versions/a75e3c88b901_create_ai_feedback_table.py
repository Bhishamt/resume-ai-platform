"""create_ai_feedback_table

Revision ID: a75e3c88b901
Revises: 7a66451e71c
Create Date: 2026-07-10 21:10:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a75e3c88b901"
down_revision: Union[str, Sequence[str], None] = "7a66451e71c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "ai_feedback",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("resume_id", sa.UUID(), nullable=True),
        sa.Column("analysis_id", sa.UUID(), nullable=True),
        sa.Column("job_match_id", sa.UUID(), nullable=True),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("prompt_type", sa.String(length=100), nullable=False),
        sa.Column("prompt_version", sa.String(length=20), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column("token_usage", sa.JSON(), nullable=False),
        sa.Column("response_time", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["analysis_id"], ["analysis_reports.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["job_match_id"], ["job_matches.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_ai_feedback_analysis_id"), "ai_feedback", ["analysis_id"], unique=False
    )
    op.create_index(
        op.f("ix_ai_feedback_job_match_id"),
        "ai_feedback",
        ["job_match_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_feedback_resume_id"), "ai_feedback", ["resume_id"], unique=False
    )
    op.create_index(
        op.f("ix_ai_feedback_user_id"), "ai_feedback", ["user_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_ai_feedback_user_id"), table_name="ai_feedback")
    op.drop_index(op.f("ix_ai_feedback_resume_id"), table_name="ai_feedback")
    op.drop_index(op.f("ix_ai_feedback_job_match_id"), table_name="ai_feedback")
    op.drop_index(op.f("ix_ai_feedback_analysis_id"), table_name="ai_feedback")
    op.drop_table("ai_feedback")
