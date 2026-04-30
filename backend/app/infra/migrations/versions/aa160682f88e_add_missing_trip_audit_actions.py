"""add_missing_trip_audit_actions

Revision ID: aa160682f88e
Revises: a3b87d9a3a04
Create Date: 2026-01-06 13:22:02.153956

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa160682f88e'
down_revision: Union[str, Sequence[str], None] = 'a3b87d9a3a04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add missing trip audit action values
    op.execute("ALTER TYPE audit_action ADD VALUE IF NOT EXISTS 'TRIP_MANUAL_CREATED'")
    op.execute("ALTER TYPE audit_action ADD VALUE IF NOT EXISTS 'TRIP_UPDATED'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
