"""add device password rotation fields

Revision ID: joo25m3rkhhl
Revises: 893c0ec376a4
Create Date: 2025-11-17 13:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'joo25m3rkhhl'
down_revision = '893c0ec376a4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add password rotation fields to devices table
    op.add_column('devices', sa.Column('current_password', sa.String(length=500), nullable=True))
    op.add_column('devices', sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove password rotation fields from devices table
    op.drop_column('devices', 'password_changed_at')
    op.drop_column('devices', 'current_password')
