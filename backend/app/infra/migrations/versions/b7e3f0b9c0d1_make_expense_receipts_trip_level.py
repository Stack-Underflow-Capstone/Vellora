"""make expense receipts trip-level

Revision ID: b7e3f0b9c0d1
Revises: c3c9c5d5c5b2
Create Date: 2026-01-05 10:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7e3f0b9c0d1"
down_revision: Union[str, Sequence[str], None] = "c3c9c5d5c5b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("expense_receipts_expense_id_fkey", "expense_receipts", type_="foreignkey")
    op.alter_column("expense_receipts", "expense_id", nullable=True)
    op.create_foreign_key(
        "expense_receipts_expense_id_fkey",
        "expense_receipts",
        "expenses",
        ["expense_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("expense_receipts_expense_id_fkey", "expense_receipts", type_="foreignkey")
    op.alter_column("expense_receipts", "expense_id", nullable=False)
    op.create_foreign_key(
        "expense_receipts_expense_id_fkey",
        "expense_receipts",
        "expenses",
        ["expense_id"],
        ["id"],
        ondelete="CASCADE",
    )
