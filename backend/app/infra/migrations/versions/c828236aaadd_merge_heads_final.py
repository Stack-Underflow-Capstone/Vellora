"""merge_heads_final

Revision ID: c828236aaadd
Revises: 34ee3d551d83, 7904a431b662
Create Date: 2026-04-21 00:35:40.000127

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c828236aaadd'
down_revision: Union[str, Sequence[str], None] = ('34ee3d551d83', '7904a431b662')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
