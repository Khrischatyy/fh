"""add description to booking_statuses

Revision ID: 6ff3e5484e81
Revises: a3d9caea02c9
Create Date: 2025-11-10 23:54:04.073037

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ff3e5484e81'
down_revision = 'a3d9caea02c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add description column to booking_statuses table
    op.add_column('booking_statuses', sa.Column('description', sa.String(length=255), nullable=True))


def downgrade() -> None:
    # Remove description column from booking_statuses table
    op.drop_column('booking_statuses', 'description')
