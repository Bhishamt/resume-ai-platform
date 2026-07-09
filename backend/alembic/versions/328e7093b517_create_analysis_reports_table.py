"""create_analysis_reports_table

Revision ID: 328e7093b517
Revises: ce9cdad6538e
Create Date: 2026-07-09 21:05:54.833826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '328e7093b517'
down_revision: Union[str, Sequence[str], None] = 'ce9cdad6538e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'analysis_reports',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('resume_id', sa.UUID(), nullable=False),
        sa.Column('ats_score', sa.Integer(), nullable=False),
        sa.Column('resume_score', sa.Integer(), nullable=False),
        sa.Column('keyword_score', sa.Integer(), nullable=False),
        sa.Column('formatting_score', sa.Integer(), nullable=False),
        sa.Column('experience_score', sa.Integer(), nullable=False),
        sa.Column('education_score', sa.Integer(), nullable=False),
        sa.Column('projects_score', sa.Integer(), nullable=False),
        sa.Column('grammar_score', sa.Integer(), nullable=False),
        sa.Column('strengths', sa.JSON(), nullable=False),
        sa.Column('weaknesses', sa.JSON(), nullable=False),
        sa.Column('missing_keywords', sa.JSON(), nullable=False),
        sa.Column('suggestions', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analysis_reports_resume_id'), 'analysis_reports', ['resume_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_analysis_reports_resume_id'), table_name='analysis_reports')
    op.drop_table('analysis_reports')

