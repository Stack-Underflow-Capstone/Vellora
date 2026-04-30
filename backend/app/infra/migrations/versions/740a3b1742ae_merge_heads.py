"""merge heads

Revision ID: 740a3b1742ae
Revises: 6d5f243e9943, 8026fc2058b9
Create Date: 2025-12-01 14:06:01.835351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '740a3b1742ae'
down_revision: Union[str, Sequence[str], None] = ('6d5f243e9943', '8026fc2058b9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
