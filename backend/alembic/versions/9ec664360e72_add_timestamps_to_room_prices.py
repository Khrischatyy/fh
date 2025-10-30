"""add_timestamps_to_room_prices

Revision ID: 9ec664360e72
Revises: b74a45b320b3
Create Date: 2025-10-30 21:09:52.534677

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ec664360e72'
down_revision = 'b74a45b320b3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add created_at and updated_at columns to room_prices table
    op.execute("""
        ALTER TABLE room_prices
        ADD COLUMN created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
        ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
    """)

    # Update existing rows with current timestamp
    op.execute("UPDATE room_prices SET created_at = NOW(), updated_at = NOW()")


def downgrade() -> None:
    # Remove timestamp columns
    op.execute("ALTER TABLE room_prices DROP COLUMN created_at, DROP COLUMN updated_at")
