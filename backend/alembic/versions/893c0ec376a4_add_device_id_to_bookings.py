"""add device_id to bookings

Revision ID: 893c0ec376a4
Revises: 5573f32dcfec
Create Date: 2025-01-11 21:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '893c0ec376a4'
down_revision = '5573f32dcfec'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add device_id column to bookings table
    op.add_column('bookings', sa.Column('device_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_bookings_device_id'), 'bookings', ['device_id'], unique=False)
    op.create_foreign_key(
        op.f('fk_bookings_device_id_devices'),
        'bookings',
        'devices',
        ['device_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Remove device_id column from bookings table
    op.drop_constraint(op.f('fk_bookings_device_id_devices'), 'bookings', type_='foreignkey')
    op.drop_index(op.f('ix_bookings_device_id'), table_name='bookings')
    op.drop_column('bookings', 'device_id')
