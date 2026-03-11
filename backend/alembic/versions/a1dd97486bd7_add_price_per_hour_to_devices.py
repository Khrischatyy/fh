"""add price_per_hour to devices

Revision ID: a1dd97486bd7
Revises: 6d9b10f1af55
Create Date: 2026-03-10 19:47:19.557651

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1dd97486bd7'
down_revision = '6d9b10f1af55'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('devices', sa.Column('price_per_hour', sa.Numeric(precision=10, scale=2), server_default='25.00', nullable=True))


def downgrade() -> None:
    op.drop_column('devices', 'price_per_hour')
