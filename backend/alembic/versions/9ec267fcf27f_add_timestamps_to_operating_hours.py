"""add_timestamps_to_operating_hours

Revision ID: 9ec267fcf27f
Revises: 4b664026d623
Create Date: 2025-10-30 20:38:02.471026

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ec267fcf27f'
down_revision = '4b664026d623'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add created_at and updated_at columns to operating_hours table
    op.execute("""
        ALTER TABLE operating_hours
        ADD COLUMN created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
        ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
    """)

    # Update existing rows with current timestamp
    op.execute("UPDATE operating_hours SET created_at = NOW(), updated_at = NOW()")


def downgrade() -> None:
    # Remove timestamp columns
    op.execute("ALTER TABLE operating_hours DROP COLUMN created_at, DROP COLUMN updated_at")
