"""Merge migration heads before adding notifications

Revision ID: 4edfc05b1584
Revises: 00774d8860df, c3c9c5d5c5b2
Create Date: 2026-01-28 11:57:30.744717

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4edfc05b1584'
down_revision: Union[str, Sequence[str], None] = ('00774d8860df', 'c3c9c5d5c5b2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
