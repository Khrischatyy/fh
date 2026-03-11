"""drop unused unlock_fee from devices

Revision ID: e24f83cd82aa
Revises: a1dd97486bd7
Create Date: 2026-03-11 11:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e24f83cd82aa'
down_revision = 'a1dd97486bd7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('devices', 'unlock_fee')


def downgrade() -> None:
    op.add_column('devices', sa.Column('unlock_fee', sa.Numeric(precision=10, scale=2), nullable=False, server_default='10.00'))
