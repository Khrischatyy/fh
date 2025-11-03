"""add name description cover_photo is_active is_published to addresses

Revision ID: eacb67ee0634
Revises: 3ffe7c7ab5aa
Create Date: 2025-10-31 16:23:52.895040

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eacb67ee0634'
down_revision = '3ffe7c7ab5aa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to addresses table
    op.add_column('addresses', sa.Column('name', sa.String(length=255), nullable=True))
    op.add_column('addresses', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('addresses', sa.Column('cover_photo', sa.String(length=500), nullable=True))
    op.add_column('addresses', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('addresses', sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'))

    # Update existing rows to use slug as name temporarily
    op.execute("UPDATE addresses SET name = slug WHERE name IS NULL")

    # Make name NOT NULL after populating
    op.alter_column('addresses', 'name', nullable=False)


def downgrade() -> None:
    # Remove columns in reverse order
    op.drop_column('addresses', 'is_published')
    op.drop_column('addresses', 'is_active')
    op.drop_column('addresses', 'cover_photo')
    op.drop_column('addresses', 'description')
    op.drop_column('addresses', 'name')
