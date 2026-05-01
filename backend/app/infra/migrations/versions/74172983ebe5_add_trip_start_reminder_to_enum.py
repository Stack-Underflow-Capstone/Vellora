"""add trip start reminder to enum

Revision ID: 74172983ebe5
Revises: 175a872a62ca
Create Date: 2026-01-28 12:19:31.490650

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74172983ebe5'
down_revision: Union[str, Sequence[str], None] = '175a872a62ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE notification_type ADD VALUE 'trip_start_reminder'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
