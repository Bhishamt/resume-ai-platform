"""create_job_matching_tables

Revision ID: 7a66451e71c
Revises: 48a66451e71b
Create Date: 2026-07-10 20:50:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7a66451e71c"
down_revision: Union[str, Sequence[str], None] = "48a66451e71b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create job_descriptions table
    op.create_table(
        "job_descriptions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("employment_type", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("required_skills", sa.JSON(), nullable=False),
        sa.Column("preferred_skills", sa.JSON(), nullable=False),
        sa.Column("required_experience", sa.String(length=255), nullable=True),
        sa.Column("education_requirement", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_job_descriptions_user_id"),
        "job_descriptions",
        ["user_id"],
        unique=False,
    )

    # Create job_matches table
    op.create_table(
        "job_matches",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("resume_id", sa.UUID(), nullable=False),
        sa.Column("job_description_id", sa.UUID(), nullable=False),
        sa.Column("overall_match", sa.Integer(), nullable=False),
        sa.Column("skill_match", sa.Integer(), nullable=False),
        sa.Column("experience_match", sa.Integer(), nullable=False),
        sa.Column("education_match", sa.Integer(), nullable=False),
        sa.Column("keyword_match", sa.Integer(), nullable=False),
        sa.Column("missing_skills", sa.JSON(), nullable=False),
        sa.Column("matching_skills", sa.JSON(), nullable=False),
        sa.Column("missing_keywords", sa.JSON(), nullable=False),
        sa.Column("recommendations", sa.JSON(), nullable=False),
        sa.Column("score_explanations", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["job_description_id"], ["job_descriptions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_job_matches_job_description_id"),
        "job_matches",
        ["job_description_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_job_matches_resume_id"), "job_matches", ["resume_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_job_matches_resume_id"), table_name="job_matches")
    op.drop_index(op.f("ix_job_matches_job_description_id"), table_name="job_matches")
    op.drop_table("job_matches")
    op.drop_index(op.f("ix_job_descriptions_user_id"), table_name="job_descriptions")
    op.drop_table("job_descriptions")
