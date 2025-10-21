"""rename_password_to_hashed_password

Revision ID: 5ba2b9e2bc80
Revises: 001_initial_schema
Create Date: 2025-10-20 22:22:36.878665

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ba2b9e2bc80'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename password column to hashed_password for FastAPI Users compatibility
    op.alter_column('users', 'password', new_column_name='hashed_password')


def downgrade() -> None:
    # Rename back to password
    op.alter_column('users', 'hashed_password', new_column_name='password')
