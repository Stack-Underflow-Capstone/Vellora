"""add scheduled trips fields

Revision ID: 9b4d2c1f8a2d
Revises: 00774d8860df, b7e3f0b9c0d1
Create Date: 2026-02-10 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b4d2c1f8a2d"
down_revision: Union[str, Sequence[str], None] = ("00774d8860df", "b7e3f0b9c0d1")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE trip_status ADD VALUE IF NOT EXISTS 'scheduled'")
    op.add_column("trips", sa.Column("scheduled_start_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("trips", sa.Column("scheduled_end_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("trips", "scheduled_end_at")
    op.drop_column("trips", "scheduled_start_at")
    
