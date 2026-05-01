"""add scheduled optional addresses and calendar fields

Revision ID: 56b9d2f1c4a0
Revises: 9b4d2c1f8a2d
Create Date: 2026-02-10 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "56b9d2f1c4a0"
down_revision: Union[str, Sequence[str], None] = "9b4d2c1f8a2d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("trips", "start_address_encrypted", nullable=True)
    op.add_column("trips", sa.Column("calendar_provider", sa.String(length=50), nullable=True))
    op.add_column("trips", sa.Column("calendar_event_id", sa.String(length=255), nullable=True))
    op.add_column("trips", sa.Column("calendar_event_url", sa.String(length=1024), nullable=True))


def downgrade() -> None:
    op.drop_column("trips", "calendar_event_url")
    op.drop_column("trips", "calendar_event_id")
    op.drop_column("trips", "calendar_provider")
    op.alter_column("trips", "start_address_encrypted", nullable=False)
