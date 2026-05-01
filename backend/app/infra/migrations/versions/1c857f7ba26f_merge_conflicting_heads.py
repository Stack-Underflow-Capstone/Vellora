"""merge conflicting heads

Revision ID: 1c857f7ba26f
Revises: 04a9499173cb, 856f8f86be63
Create Date: 2026-03-10 23:35:32.589753

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c857f7ba26f'
down_revision: Union[str, Sequence[str], None] = ('04a9499173cb', '856f8f86be63')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
