"""merge conflicting heads

Revision ID: 34ee3d551d83
Revises: 00dfb885906a, 1c857f7ba26f
Create Date: 2026-03-31 02:37:16.334609

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34ee3d551d83'
down_revision: Union[str, Sequence[str], None] = ('00dfb885906a', '1c857f7ba26f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
