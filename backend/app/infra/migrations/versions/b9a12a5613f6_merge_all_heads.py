"""merge_all_heads

Revision ID: b9a12a5613f6
Revises: 561b5e2c8f2b, cf8d70cf7d30
Create Date: 2026-02-23 22:01:33.774111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9a12a5613f6'
down_revision: Union[str, Sequence[str], None] = ('561b5e2c8f2b', 'cf8d70cf7d30')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
