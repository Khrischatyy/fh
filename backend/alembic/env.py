"""
Alembic environment configuration.
Handles database migrations with async support.
"""
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import asyncio

# Import all models to ensure they're registered with Base.metadata
from src.database import Base, database_url
from src.auth.models import User, favorite_studios, engineer_addresses
from src.companies.models import Company, AdminCompany
from src.geographic.models import Country, City
from src.addresses.models import (
    Address,
    OperatingHour,
    StudioClosure,
    Equipment,
    EquipmentType,
    Badge,
    address_equipment,
    address_badge,
)
from src.rooms.models import Room, RoomPhoto, RoomPrice
from src.bookings.models import Booking, BookingStatus
from src.payments.models import Charge, Payout, SquareLocation, SquareToken
from src.messages.models import Message
from src.devices.models import Device, DeviceLog

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = Base.metadata

# Override sqlalchemy.url from config
config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the provided connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in 'online' mode using async engine.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Convert postgres:// to postgresql:// and add asyncpg
    url = database_url.replace("postgres://", "postgresql://", 1)
    url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = url

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
