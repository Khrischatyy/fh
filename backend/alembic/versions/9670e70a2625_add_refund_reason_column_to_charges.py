"""add refund_reason column to charges

Revision ID: 9670e70a2625
Revises: 27242f9f9125
Create Date: 2025-11-07 00:55:10.965592

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9670e70a2625'
down_revision = '27242f9f9125'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add refund_reason column to charges table
    op.add_column('charges', sa.Column('refund_reason', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove refund_reason column
    op.drop_column('charges', 'refund_reason')
