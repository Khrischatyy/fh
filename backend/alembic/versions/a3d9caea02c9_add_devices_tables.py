"""add devices tables

Revision ID: a3d9caea02c9
Revises: a257eb162ffb
Create Date: 2025-11-10 17:56:09.128897

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3d9caea02c9'
down_revision = 'a257eb162ffb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create devices table
    op.create_table(
        'devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('mac_address', sa.String(length=255), nullable=False),
        sa.Column('device_uuid', sa.String(length=255), nullable=False),
        sa.Column('device_token', sa.String(length=500), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('is_blocked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_heartbeat', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_ip', sa.String(length=45), nullable=True),
        sa.Column('os_version', sa.String(length=100), nullable=True),
        sa.Column('app_version', sa.String(length=50), nullable=True),
        sa.Column('unlock_password_hash', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('mac_address'),
        sa.UniqueConstraint('device_uuid'),
        sa.UniqueConstraint('device_token'),
    )
    op.create_index(op.f('ix_devices_id'), 'devices', ['id'], unique=False)
    op.create_index(op.f('ix_devices_mac_address'), 'devices', ['mac_address'], unique=True)
    op.create_index(op.f('ix_devices_device_uuid'), 'devices', ['device_uuid'], unique=True)

    # Create device_logs table
    op.create_table(
        'device_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_device_logs_id'), 'device_logs', ['id'], unique=False)
    op.create_index(op.f('ix_device_logs_device_id'), 'device_logs', ['device_id'], unique=False)


def downgrade() -> None:
    # Drop device_logs table
    op.drop_index(op.f('ix_device_logs_device_id'), table_name='device_logs')
    op.drop_index(op.f('ix_device_logs_id'), table_name='device_logs')
    op.drop_table('device_logs')

    # Drop devices table
    op.drop_index(op.f('ix_devices_device_uuid'), table_name='devices')
    op.drop_index(op.f('ix_devices_mac_address'), table_name='devices')
    op.drop_index(op.f('ix_devices_id'), table_name='devices')
    op.drop_table('devices')
