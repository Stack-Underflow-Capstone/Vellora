"""merge multiple heads - resolve conflict

Revision ID: 856f8f86be63
Revises: 94b4228ceeba, ea469b5379aa
Create Date: 2026-03-02 22:27:52.504409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '856f8f86be63'
down_revision: Union[str, Sequence[str], None] = ('94b4228ceeba', 'ea469b5379aa')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
