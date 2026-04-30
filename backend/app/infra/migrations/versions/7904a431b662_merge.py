"""merge

Revision ID: 7904a431b662
Revises: 1615f69a7de8
Create Date: 2026-04-04 12:35:45.507294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7904a431b662'
down_revision: Union[str, Sequence[str], None] = '1615f69a7de8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
