"""add_trip_audit_actions_to_enum

Revision ID: a3b87d9a3a04
Revises: 6e2780455889
Create Date: 2026-01-06 13:05:59.589971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3b87d9a3a04'
down_revision: Union[str, Sequence[str], None] = '6e2780455889'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new values to the audit_action enum
    op.execute("ALTER TYPE audit_action ADD VALUE IF NOT EXISTS 'TRIP_STARTED'")
    op.execute("ALTER TYPE audit_action ADD VALUE IF NOT EXISTS 'TRIP_COMPLETED'")
    op.execute("ALTER TYPE audit_action ADD VALUE IF NOT EXISTS 'TRIP_CANCELLED'")
    op.execute("ALTER TYPE audit_action ADD VALUE IF NOT EXISTS 'TRIP_MANUAL_CREATED'")
    op.execute("ALTER TYPE audit_action ADD VALUE IF NOT EXISTS 'TRIP_UPDATED'")


def downgrade() -> None:
    """Downgrade schema."""
    # Note: PostgreSQL doesn't support removing enum values directly
    # You would need to recreate the enum if you want to remove values
    pass
