"""add device unlock sessions and unlock_fee

Revision ID: c1a2b3d4e5f6
Revises: 893c0ec376a4
Create Date: 2025-11-26 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c1a2b3d4e5f6'
down_revision = '893c0ec376a4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add unlock_fee column to devices table (default $10.00)
    op.add_column(
        'devices',
        sa.Column('unlock_fee', sa.Numeric(precision=10, scale=2), nullable=False, server_default='10.00')
    )

    # Create device_unlock_sessions table
    op.create_table(
        'device_unlock_sessions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('stripe_session_id', sa.String(length=255), nullable=False),
        sa.Column('stripe_payment_intent', sa.String(length=255), nullable=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('unlock_duration_hours', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE'),
    )

    # Create indexes for device_unlock_sessions
    op.create_index(op.f('ix_device_unlock_sessions_device_id'), 'device_unlock_sessions', ['device_id'], unique=False)
    op.create_index(op.f('ix_device_unlock_sessions_stripe_session_id'), 'device_unlock_sessions', ['stripe_session_id'], unique=True)
    op.create_index(op.f('ix_device_unlock_sessions_status'), 'device_unlock_sessions', ['status'], unique=False)
    op.create_index(op.f('ix_device_unlock_sessions_expires_at'), 'device_unlock_sessions', ['expires_at'], unique=False)

    # Create unique constraint for stripe_payment_intent (nullable)
    op.create_index(
        op.f('ix_device_unlock_sessions_stripe_payment_intent'),
        'device_unlock_sessions',
        ['stripe_payment_intent'],
        unique=True,
        postgresql_where=sa.text('stripe_payment_intent IS NOT NULL')
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_device_unlock_sessions_stripe_payment_intent'), table_name='device_unlock_sessions')
    op.drop_index(op.f('ix_device_unlock_sessions_expires_at'), table_name='device_unlock_sessions')
    op.drop_index(op.f('ix_device_unlock_sessions_status'), table_name='device_unlock_sessions')
    op.drop_index(op.f('ix_device_unlock_sessions_stripe_session_id'), table_name='device_unlock_sessions')
    op.drop_index(op.f('ix_device_unlock_sessions_device_id'), table_name='device_unlock_sessions')

    # Drop device_unlock_sessions table
    op.drop_table('device_unlock_sessions')

    # Remove unlock_fee column from devices table
    op.drop_column('devices', 'unlock_fee')
