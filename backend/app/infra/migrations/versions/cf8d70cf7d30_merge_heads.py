"""merge_heads

Revision ID: cf8d70cf7d30
Revises: 00774d8860df, b7e3f0b9c0d1
Create Date: 2026-02-02 21:36:19.272602

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf8d70cf7d30'
down_revision: Union[str, Sequence[str], None] = ('00774d8860df', 'b7e3f0b9c0d1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
