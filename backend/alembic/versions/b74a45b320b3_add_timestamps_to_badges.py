"""add_timestamps_to_badges

Revision ID: b74a45b320b3
Revises: 9ec267fcf27f
Create Date: 2025-10-30 21:02:47.189347

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b74a45b320b3'
down_revision = '9ec267fcf27f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add created_at and updated_at columns to badges table
    op.execute("""
        ALTER TABLE badges
        ADD COLUMN created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
        ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
    """)

    # Update existing rows with current timestamp
    op.execute("UPDATE badges SET created_at = NOW(), updated_at = NOW()")


def downgrade() -> None:
    # Remove timestamp columns
    op.execute("ALTER TABLE badges DROP COLUMN created_at, DROP COLUMN updated_at")
