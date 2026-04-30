"""merge_migration_conflict

Revision ID: b5aee7aa574b
Revises: 56b9d2f1c4a0, f0c0ffc03adc
Create Date: 2026-02-11 00:00:39.616037

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5aee7aa574b'
down_revision: Union[str, Sequence[str], None] = ('56b9d2f1c4a0', 'f0c0ffc03adc')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
