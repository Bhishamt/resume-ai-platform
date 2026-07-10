"""create_dashboard_preferences_table

Revision ID: a7b6c51e8a20
Revises: a75e3c88b901
Create Date: 2026-07-10 21:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7b6c51e8a20'
down_revision: Union[str, Sequence[str], None] = 'a75e3c88b901'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'dashboard_preferences',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('layout', sa.JSON(), nullable=False),
        sa.Column('widgets', sa.JSON(), nullable=False),
        sa.Column('theme', sa.String(length=50), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dashboard_preferences_user_id'), 'dashboard_preferences', ['user_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_dashboard_preferences_user_id'), table_name='dashboard_preferences')
    op.drop_table('dashboard_preferences')
