"""merge multiple heads

Revision ID: ea469b5379aa
Revises: b5aee7aa574b, b9a12a5613f6
Create Date: 2026-03-02 00:03:55.386161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea469b5379aa'
down_revision: Union[str, Sequence[str], None] = ('b5aee7aa574b', 'b9a12a5613f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
