"""add_scoring_explanations

Revision ID: 48a66451e71b
Revises: 328e7093b517
Create Date: 2026-07-10 20:41:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "48a66451e71b"
down_revision: Union[str, Sequence[str], None] = "328e7093b517"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "analysis_reports",
        sa.Column(
            "scoring_explanations", sa.JSON(), nullable=False, server_default="{}"
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("analysis_reports", "scoring_explanations")
