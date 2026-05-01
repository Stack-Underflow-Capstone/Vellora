"""seed irs rates with system user

Revision ID: 8a14f3e7fef4
Revises: 944064892c74
Create Date: 2025-11-13 23:42:23.831390

"""
from typing import Sequence, Union
import uuid
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


#revision identifiers, used by Alembic.
revision: str = '8a14f3e7fef4'
down_revision: Union[str, Sequence[str], None] = '944064892c74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create system user and seed IRS rates."""

#Define table structures
    users = sa.table(
        'users',
        sa.column('id', UUID),
        sa.column('email', sa.String),
        sa.column('password_hash', sa.String),
        sa.column('full_name', sa.String),
        sa.column('role', sa.String),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime)
    )

    rate_customizations = sa.table(
        'rate_customizations',
        sa.column('id', UUID),
        sa.column('user_id', UUID),
        sa.column('name', sa.String),
        sa.column('description', sa.Text),
        sa.column('year', sa.Integer),
        sa.column('created_at', sa.DateTime)
    )

    rate_categories = sa.table(
        'rate_categories',
        sa.column('id', UUID),
        sa.column('name', sa.String),
        sa.column('cost_per_mile', sa.DOUBLE_PRECISION),
        sa.column('rate_customization_id', UUID),
        sa.column('created_at', sa.DateTime)
    )

#Generate IDs
    system_user_id = uuid.uuid4()
    irs_customization_id = uuid.uuid4()
    current_time = datetime.utcnow()

#Create system user for IRS rates
    op.bulk_insert(users, [
        {
            'id': system_user_id,
            'email': 'system@irs.gov',
            'password_hash': None,
            'full_name': 'IRS System User',
            'role': 'employee',
            'is_active': False,
            'created_at': current_time,
            'updated_at': current_time
        }
    ])
#Create IRS rate customization
    op.bulk_insert(rate_customizations, [
        {
            'id': irs_customization_id,
            'user_id': system_user_id,
            'name': 'IRS Standard Rates',
            'description': 'Official IRS standard mileage rates for business use',
            'year': 2025,
            'created_at': current_time
        }
    ])

#Create IRS rate categories
    op.bulk_insert(rate_categories, [
        {
            'id': uuid.uuid4(),
            'name': 'Business use',
            'cost_per_mile': 0.70,
            'rate_customization_id': irs_customization_id,
            'created_at': current_time
        },
        {
            'id': uuid.uuid4(),
            'name': 'Medical or military moving',
            'cost_per_mile': 0.21,
            'rate_customization_id': irs_customization_id,
            'created_at': current_time
        },
        {
            'id': uuid.uuid4(),
            'name': 'Charity use',
            'cost_per_mile': 0.14,
            'rate_customization_id': irs_customization_id,
            'created_at': current_time
        }
    ])


def downgrade() -> None:
    """Remove system user and IRS rates."""
    op.execute("DELETE FROM users WHERE email = 'system@irs.gov'")