"""Merge heads

Revision ID: f3351480d39f
Revises: 5744ade4159c, 9686b4688e14
Create Date: 2025-11-19 19:45:05.489249

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3351480d39f'
down_revision: Union[str, Sequence[str], None] = ('5744ade4159c', '9686b4688e14')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
