"""merge multiple heads

Revision ID: 8026fc2058b9
Revises: 27505d66ecb0, 3b448e459963
Create Date: 2025-11-30 12:10:20.022098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8026fc2058b9'
down_revision: Union[str, Sequence[str], None] = ('27505d66ecb0', '3b448e459963')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
