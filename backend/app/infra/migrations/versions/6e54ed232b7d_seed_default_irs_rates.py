"""seed_default_irs_rates

Revision ID: 6e54ed232b7d
Revises: 1eb993c8e081
Create Date: 2025-11-10 14:02:56.683318

"""
from typing import Sequence, Union
import uuid
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '6e54ed232b7d'
down_revision: Union[str, Sequence[str], None] = '1eb993c8e081'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Seeding moved to separate migration
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
