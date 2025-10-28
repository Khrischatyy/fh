"""add name and role fields to users

Revision ID: add_name_role_001
Revises: 72e16e41bfad
Create Date: 2025-10-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_name_role_001'
down_revision: Union[str, None] = '72e16e41bfad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add name and role fields to users table."""
    # Add name column (nullable, since existing users won't have it)
    op.add_column('users', sa.Column('name', sa.String(length=255), nullable=True))

    # Add role column with default value
    op.add_column('users', sa.Column('role', sa.String(length=15), nullable=False, server_default='user'))


def downgrade() -> None:
    """Remove name and role fields from users table."""
    op.drop_column('users', 'role')
    op.drop_column('users', 'name')
