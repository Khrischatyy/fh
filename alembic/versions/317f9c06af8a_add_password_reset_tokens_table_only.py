"""add password_reset_tokens table only

Revision ID: 317f9c06af8a
Revises: add_name_role_001
Create Date: 2025-10-22 22:25:32.003538

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '317f9c06af8a'
down_revision = 'add_name_role_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create password_reset_tokens table (Laravel-compatible)
    op.create_table('password_reset_tokens',
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('email', name=op.f('pk_password_reset_tokens'))
    )


def downgrade() -> None:
    # Drop password_reset_tokens table
    op.drop_table('password_reset_tokens')
