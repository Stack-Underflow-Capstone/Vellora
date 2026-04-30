"""merge heads

Revision ID: 00dfb885906a
Revises: 04a9499173cb, ea469b5379aa
Create Date: 2026-03-10 15:42:33.038829

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00dfb885906a'
down_revision: Union[str, Sequence[str], None] = ('04a9499173cb', 'ea469b5379aa')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
