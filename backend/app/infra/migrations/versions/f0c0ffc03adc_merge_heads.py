"""merge_heads

Revision ID: f0c0ffc03adc
Revises: 74172983ebe5, b7e3f0b9c0d1
Create Date: 2026-02-06 12:39:14.333484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0c0ffc03adc'
down_revision: Union[str, Sequence[str], None] = ('74172983ebe5', 'b7e3f0b9c0d1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
