"""make_user_role_nullable

Revision ID: a257eb162ffb
Revises: 9670e70a2625
Create Date: 2025-11-07 20:05:25.060167

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a257eb162ffb'
down_revision = '9670e70a2625'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make role column nullable and remove default value
    # This allows Google OAuth users to sign up without a role and choose it later
    op.alter_column('users', 'role',
               existing_type=sa.VARCHAR(length=15),
               nullable=True,
               server_default=None)


def downgrade() -> None:
    # Restore role to NOT NULL with default value 'user'
    # First set any NULL roles to 'user' before making column NOT NULL
    op.execute("UPDATE users SET role = 'user' WHERE role IS NULL")
    op.alter_column('users', 'role',
               existing_type=sa.VARCHAR(length=15),
               nullable=False,
               server_default='user')
