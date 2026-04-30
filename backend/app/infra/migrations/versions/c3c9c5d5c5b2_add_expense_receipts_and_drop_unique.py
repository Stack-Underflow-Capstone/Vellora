"""add expense receipts and drop duplicate constraint

Revision ID: c3c9c5d5c5b2
Revises: 5744ade4159c
Create Date: 2025-11-17 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c3c9c5d5c5b2'
down_revision: Union[str, Sequence[str], None] = '5744ade4159c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("uq_expenses_trip_id_type", "expenses", type_="unique")
    op.create_table(
        "expense_receipts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("expense_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trip_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bucket", sa.String(length=255), nullable=False),
        sa.Column("object_key", sa.String(length=512), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["expense_id"], ["expenses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("object_key"),
    )
    op.create_index(op.f("ix_expense_receipts_expense_id"), "expense_receipts", ["expense_id"], unique=False)
    op.create_index(op.f("ix_expense_receipts_trip_id"), "expense_receipts", ["trip_id"], unique=False)
    op.create_index(op.f("ix_expense_receipts_user_id"), "expense_receipts", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_expense_receipts_user_id"), table_name="expense_receipts")
    op.drop_index(op.f("ix_expense_receipts_trip_id"), table_name="expense_receipts")
    op.drop_index(op.f("ix_expense_receipts_expense_id"), table_name="expense_receipts")
    op.drop_table("expense_receipts")
    op.create_unique_constraint("uq_expenses_trip_id_type", "expenses", ["trip_id", "type"])
