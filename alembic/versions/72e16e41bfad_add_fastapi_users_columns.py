"""add_fastapi_users_columns

Revision ID: 72e16e41bfad
Revises: 5ba2b9e2bc80
Create Date: 2025-10-20 22:23:52.554226

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72e16e41bfad'
down_revision = '5ba2b9e2bc80'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add FastAPI Users required columns
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove FastAPI Users columns
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'is_superuser')
    op.drop_column('users', 'is_active')
