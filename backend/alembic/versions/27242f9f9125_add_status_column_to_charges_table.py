"""add status column to charges table

Revision ID: 27242f9f9125
Revises: eacb67ee0634
Create Date: 2025-11-07 00:49:22.801400

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27242f9f9125'
down_revision = 'eacb67ee0634'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add status column to charges table
    op.add_column('charges', sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'))
    # Remove default after adding so future inserts must specify status
    op.alter_column('charges', 'status', server_default=None)


def downgrade() -> None:
    # Remove status column
    op.drop_column('charges', 'status')
