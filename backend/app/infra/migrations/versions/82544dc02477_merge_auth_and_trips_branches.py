"""merge auth and trips branches

Revision ID: 82544dc02477
Revises: 20240913_02, 9e1d0d1b78c5
Create Date: 2025-11-13 23:35:45.946544

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82544dc02477'
down_revision: Union[str, Sequence[str], None] = ('20240913_02', '9e1d0d1b78c5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
