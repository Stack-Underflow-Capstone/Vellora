"""merge_heads

Revision ID: 00774d8860df
Revises: 9323bd43ca49, aa160682f88e
Create Date: 2026-01-06 13:42:56.503600

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00774d8860df'
down_revision: Union[str, Sequence[str], None] = ('9323bd43ca49', 'aa160682f88e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
