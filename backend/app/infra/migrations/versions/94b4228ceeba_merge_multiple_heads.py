"""merge multiple heads

Revision ID: 94b4228ceeba
Revises: 56b9d2f1c4a0, d8af2b7983d4, f0c0ffc03adc
Create Date: 2026-02-19 21:54:24.957645

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94b4228ceeba'
down_revision: Union[str, Sequence[str], None] = ('56b9d2f1c4a0', 'd8af2b7983d4', 'f0c0ffc03adc')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
