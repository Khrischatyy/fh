"""add_equipment_table_simple

Revision ID: 3ffe7c7ab5aa
Revises: 9ec664360e72
Create Date: 2025-10-30 22:04:35.230180

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ffe7c7ab5aa'
down_revision = '9ec664360e72'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add timestamps to equipment_types table
    op.execute("""
        ALTER TABLE equipment_types
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
    """)

    # Update existing rows with current timestamp
    op.execute("UPDATE equipment_types SET created_at = NOW(), updated_at = NOW() WHERE created_at IS NULL")

    # Create equipment table
    op.execute("""
        CREATE TABLE IF NOT EXISTS equipment (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            equipment_type_id INTEGER NOT NULL REFERENCES equipment_types(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        )
    """)

    # Create indexes
    op.execute("CREATE INDEX IF NOT EXISTS ix_equipment_id ON equipment(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_equipment_equipment_type_id ON equipment(equipment_type_id)")


def downgrade() -> None:
    # Drop equipment table
    op.execute("DROP TABLE IF EXISTS equipment")

    # Remove timestamps from equipment_types
    op.execute("""
        ALTER TABLE equipment_types
        DROP COLUMN IF EXISTS created_at,
        DROP COLUMN IF EXISTS updated_at
    """)
