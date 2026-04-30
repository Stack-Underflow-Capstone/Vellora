"""merge

Revision ID: 1615f69a7de8
Revises: 00dfb885906a, 1c857f7ba26f
Create Date: 2026-04-04 12:33:17.367910

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1615f69a7de8'
down_revision: Union[str, Sequence[str], None] = ('00dfb885906a', '1c857f7ba26f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
