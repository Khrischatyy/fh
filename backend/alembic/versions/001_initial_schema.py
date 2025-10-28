"""Initial schema migration - recreate all Laravel tables

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all database tables from Laravel migrations."""

    # ==============================================================================
    # STEP 1: Create tables without foreign keys (base tables)
    # ==============================================================================

    # users table
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('google_id', sa.String(255), nullable=True),
        sa.Column('firstname', sa.String(100), nullable=True),
        sa.Column('lastname', sa.String(100), nullable=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('profile_photo', sa.String(500), nullable=True),
        sa.Column('username', sa.String(100), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('stripe_account_id', sa.String(255), nullable=True),
        sa.Column('password', sa.String(255), nullable=True),
        sa.Column('remember_token', sa.String(100), nullable=True),
        sa.Column('two_factor_secret', sa.Text(), nullable=True),
        sa.Column('two_factor_recovery_codes', sa.Text(), nullable=True),
        sa.Column('two_factor_confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('stripe_id', sa.String(255), nullable=True),
        sa.Column('pm_type', sa.String(255), nullable=True),
        sa.Column('pm_last_four', sa.String(4), nullable=True),
        sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('payment_gateway', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username'),
    )
    op.create_index('idx_users_stripe_id', 'users', ['stripe_id'])
    op.create_index('idx_users_google_id', 'users', ['google_id'])

    # password_resets table
    op.create_table(
        'password_resets',
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('token', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_password_resets_email', 'password_resets', ['email'])

    # failed_jobs table
    op.create_table(
        'failed_jobs',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('uuid', sa.String(255), nullable=False),
        sa.Column('connection', sa.Text(), nullable=False),
        sa.Column('queue', sa.Text(), nullable=False),
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('exception', sa.Text(), nullable=False),
        sa.Column('failed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
    )

    # personal_access_tokens table
    op.create_table(
        'personal_access_tokens',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('tokenable_type', sa.String(255), nullable=False),
        sa.Column('tokenable_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('token', sa.String(64), nullable=False),
        sa.Column('abilities', sa.Text(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token'),
    )
    op.create_index('idx_personal_access_tokens_tokenable', 'personal_access_tokens', ['tokenable_type', 'tokenable_id'])

    # countries table
    op.create_table(
        'countries',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    # cities table
    op.create_table(
        'cities',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('country_id', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['country_id'], ['countries.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_cities_name_country', 'cities', ['name', 'country_id'], unique=True)

    # companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('logo', sa.String(500), nullable=True),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('founding_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
    )

    # equipment_type table
    op.create_table(
        'equipment_types',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('icon', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # badges table
    op.create_table(
        'badges',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('image', sa.String(500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # fields table
    op.create_table(
        'fields',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('value', sa.String(255), nullable=True),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # booking_statuses table
    op.create_table(
        'booking_statuses',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # Seed booking statuses
    op.execute("""
        INSERT INTO booking_statuses (id, name) VALUES
        (1, 'pending'),
        (2, 'paid'),
        (3, 'cancelled'),
        (4, 'expired')
    """)

    # operating_modes table
    op.create_table(
        'operating_modes',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('mode', sa.String(100), nullable=False),
        sa.Column('label', sa.String(255), nullable=True),
        sa.Column('description_registration', sa.String(500), nullable=True),
        sa.Column('description_customer', sa.String(500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('mode'),
    )

    # jobs table (Laravel job queue)
    op.create_table(
        'jobs',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('queue', sa.String(255), nullable=False),
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('attempts', sa.SmallInteger(), nullable=False),
        sa.Column('reserved_at', sa.Integer(), nullable=True),
        sa.Column('available_at', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_jobs_queue', 'jobs', ['queue'])

    # permissions table (Spatie)
    op.create_table(
        'permissions',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('guard_name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_permissions_name_guard', 'permissions', ['name', 'guard_name'], unique=True)

    # roles table (Spatie)
    op.create_table(
        'roles',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('guard_name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_roles_name_guard', 'roles', ['name', 'guard_name'], unique=True)

    # ==============================================================================
    # STEP 2: Create dependent tables (with foreign keys)
    # ==============================================================================

    # addresses table
    op.create_table(
        'addresses',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('latitude', sa.Numeric(8, 6), nullable=True),
        sa.Column('longitude', sa.Numeric(8, 6), nullable=True),
        sa.Column('street', sa.String(500), nullable=True),
        sa.Column('available_balance', sa.Numeric(10, 2), server_default='0', nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('timezone', sa.String(100), nullable=True),
        sa.Column('city_id', sa.BigInteger(), nullable=True),
        sa.Column('company_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
    )

    # admin_company table
    op.create_table(
        'admin_company',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('admin_id', sa.BigInteger(), nullable=False),
        sa.Column('company_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
    )

    # company_city table
    op.create_table(
        'company_city',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('company_id', sa.BigInteger(), nullable=False),
        sa.Column('city_id', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ondelete='CASCADE'),
    )

    # equipments table
    op.create_table(
        'equipments',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('equipment_type_id', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['equipment_type_id'], ['equipment_types.id'], ondelete='CASCADE'),
    )

    # rooms table
    op.create_table(
        'rooms',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('address_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ondelete='CASCADE'),
    )

    # room_prices table
    op.create_table(
        'room_prices',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('room_id', sa.BigInteger(), nullable=False),
        sa.Column('hours', sa.Integer(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('total_price', sa.Numeric(8, 2), nullable=False),
        sa.Column('price_per_hour', sa.Numeric(8, 2), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
    )

    # room_photos table
    op.create_table(
        'room_photos',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('room_id', sa.BigInteger(), nullable=False),
        sa.Column('path', sa.String(500), nullable=False),
        sa.Column('index', sa.Integer(), server_default='0', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_room_photos_room_index', 'room_photos', ['room_id', 'index'], unique=True)

    # address_equipment table
    op.create_table(
        'address_equipment',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('address_id', sa.BigInteger(), nullable=False),
        sa.Column('equipment_id', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipments.id'], ondelete='CASCADE'),
    )

    # address_badge table
    op.create_table(
        'address_badge',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('address_id', sa.BigInteger(), nullable=False),
        sa.Column('badge_id', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['badge_id'], ['badges.id'], ondelete='CASCADE'),
    )

    # document_field table
    op.create_table(
        'document_field',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('document_id', sa.BigInteger(), nullable=False),
        sa.Column('field_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['field_id'], ['fields.id'], ondelete='CASCADE'),
    )

    # user_document table
    op.create_table(
        'user_document',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('document_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    )

    # bookings table
    op.create_table(
        'bookings',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('temporary_payment_link', sa.Text(), nullable=True),
        sa.Column('temporary_payment_link_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('room_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('status_id', sa.BigInteger(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['status_id'], ['booking_statuses.id']),
    )

    # charges table
    op.create_table(
        'charges',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('booking_id', sa.BigInteger(), nullable=False),
        sa.Column('stripe_session_id', sa.String(255), nullable=True),
        sa.Column('stripe_payment_intent', sa.String(255), nullable=True),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('refund_id', sa.String(255), nullable=True),
        sa.Column('refund_status', sa.String(50), nullable=True),
        sa.Column('square_payment_id', sa.String(255), nullable=True),
        sa.Column('order_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
    )

    # messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('sender_id', sa.BigInteger(), nullable=False),
        sa.Column('recipient_id', sa.BigInteger(), nullable=False),
        sa.Column('address_id', sa.BigInteger(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_messages_sender_recipient_address', 'messages', ['sender_id', 'recipient_id', 'address_id'])
    op.create_index('idx_messages_created_at', 'messages', ['created_at'])

    # operating_hours table
    op.create_table(
        'operating_hours',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('address_id', sa.BigInteger(), nullable=False),
        sa.Column('mode_id', sa.BigInteger(), nullable=True),
        sa.Column('day_of_week', sa.Integer(), nullable=True),
        sa.Column('open_time', sa.Time(), nullable=True),
        sa.Column('close_time', sa.Time(), nullable=True),
        sa.Column('is_closed', sa.Boolean(), server_default='false', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['address_id'], ['addresses.id']),
        sa.ForeignKeyConstraint(['mode_id'], ['operating_modes.id']),
    )

    # studio_closures table
    op.create_table(
        'studio_closures',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('address_id', sa.BigInteger(), nullable=False),
        sa.Column('closure_date', sa.Date(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['address_id'], ['addresses.id']),
    )

    # subscriptions table (Laravel Cashier)
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('stripe_id', sa.String(255), nullable=False),
        sa.Column('stripe_status', sa.String(255), nullable=False),
        sa.Column('stripe_price', sa.String(255), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    op.create_index('idx_subscriptions_user_status', 'subscriptions', ['user_id', 'stripe_status'])

    # subscription_items table (Laravel Cashier)
    op.create_table(
        'subscription_items',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('subscription_id', sa.BigInteger(), nullable=False),
        sa.Column('stripe_id', sa.String(255), nullable=False),
        sa.Column('stripe_product', sa.String(255), nullable=False),
        sa.Column('stripe_price', sa.String(255), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_id'),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id']),
    )
    op.create_index('idx_subscription_items_subscription_price', 'subscription_items', ['subscription_id', 'stripe_price'])

    # favorite_studios table
    op.create_table(
        'favorite_studios',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('address_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_favorite_studios_user_address', 'favorite_studios', ['user_id', 'address_id'], unique=True)

    # payouts table
    op.create_table(
        'payouts',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('payout_id', sa.String(255), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),  # Amount in cents
        sa.Column('currency', sa.String(3), server_default='usd', nullable=False),
        sa.Column('status', sa.String(50), server_default='pending', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payout_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # square_locations table
    op.create_table(
        'square_locations',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('address_id', sa.BigInteger(), nullable=False),
        sa.Column('location_id', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('location_id'),
        sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ondelete='CASCADE'),
    )

    # square_tokens table
    op.create_table(
        'square_tokens',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('access_token', sa.String(500), nullable=False),
        sa.Column('square_location_id', sa.BigInteger(), nullable=True),
        sa.Column('refresh_token', sa.String(500), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['square_location_id'], ['square_locations.id'], ondelete='CASCADE'),
    )

    # engineer_rates table
    op.create_table(
        'engineer_rates',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('rate_per_hour', sa.Numeric(8, 2), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # engineer_addresses table
    op.create_table(
        'engineer_addresses',
        sa.Column('id', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('address_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['address_id'], ['addresses.id'], ondelete='CASCADE'),
    )

    # model_has_permissions table (Spatie)
    op.create_table(
        'model_has_permissions',
        sa.Column('permission_id', sa.BigInteger(), nullable=False),
        sa.Column('model_type', sa.String(255), nullable=False),
        sa.Column('model_id', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('permission_id', 'model_id', 'model_type'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_model_has_permissions_model', 'model_has_permissions', ['model_id', 'model_type'])

    # model_has_roles table (Spatie)
    op.create_table(
        'model_has_roles',
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.Column('model_type', sa.String(255), nullable=False),
        sa.Column('model_id', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('role_id', 'model_id', 'model_type'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_model_has_roles_model', 'model_has_roles', ['model_id', 'model_type'])

    # role_has_permissions table (Spatie)
    op.create_table(
        'role_has_permissions',
        sa.Column('permission_id', sa.BigInteger(), nullable=False),
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('permission_id', 'role_id'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    """Drop all tables in reverse order."""

    # Drop tables with foreign keys first
    op.drop_table('role_has_permissions')
    op.drop_table('model_has_roles')
    op.drop_table('model_has_permissions')
    op.drop_table('engineer_addresses')
    op.drop_table('engineer_rates')
    op.drop_table('square_tokens')
    op.drop_table('square_locations')
    op.drop_table('payouts')
    op.drop_table('favorite_studios')
    op.drop_table('subscription_items')
    op.drop_table('subscriptions')
    op.drop_table('studio_closures')
    op.drop_table('operating_hours')
    op.drop_table('messages')
    op.drop_table('charges')
    op.drop_table('bookings')
    op.drop_table('user_document')
    op.drop_table('document_field')
    op.drop_table('address_badge')
    op.drop_table('address_equipment')
    op.drop_table('room_photos')
    op.drop_table('room_prices')
    op.drop_table('rooms')
    op.drop_table('equipments')
    op.drop_table('company_city')
    op.drop_table('admin_company')
    op.drop_table('addresses')

    # Drop base tables
    op.drop_table('roles')
    op.drop_table('permissions')
    op.drop_table('jobs')
    op.drop_table('operating_modes')
    op.drop_table('booking_statuses')
    op.drop_table('documents')
    op.drop_table('fields')
    op.drop_table('badges')
    op.drop_table('equipment_types')
    op.drop_table('companies')
    op.drop_table('cities')
    op.drop_table('countries')
    op.drop_table('personal_access_tokens')
    op.drop_table('failed_jobs')
    op.drop_table('password_resets')
    op.drop_table('users')
