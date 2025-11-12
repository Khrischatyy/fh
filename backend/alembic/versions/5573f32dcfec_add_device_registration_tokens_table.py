"""add device registration tokens table

Revision ID: 5573f32dcfec
Revises: 6ff3e5484e81
Create Date: 2025-11-11 19:22:29.844131

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5573f32dcfec'
down_revision = '6ff3e5484e81'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create device_registration_tokens table
    op.create_table(
        'device_registration_tokens',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('device_name', sa.String(length=255), nullable=True),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_device_registration_tokens_id', 'device_registration_tokens', ['id'], unique=False)
    op.create_index('ix_device_registration_tokens_token', 'device_registration_tokens', ['token'], unique=True)
    op.create_index('ix_device_registration_tokens_user_id', 'device_registration_tokens', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop device_registration_tokens table
    op.drop_index('ix_device_registration_tokens_user_id', 'device_registration_tokens')
    op.drop_index('ix_device_registration_tokens_token', 'device_registration_tokens')
    op.drop_index('ix_device_registration_tokens_id', 'device_registration_tokens')
    op.drop_table('device_registration_tokens')
