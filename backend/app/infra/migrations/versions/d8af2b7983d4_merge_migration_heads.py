"""merge migration heads

Revision ID: d8af2b7983d4
Revises: 00774d8860df, b7e3f0b9c0d1
Create Date: 2026-02-03 17:57:35.580651

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8af2b7983d4'
down_revision: Union[str, Sequence[str], None] = ('00774d8860df', 'b7e3f0b9c0d1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
