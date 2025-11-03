"""
Database configuration and session management.
Provides SQLAlchemy engine, session factory, and base model.
"""
from typing import AsyncGenerator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from redis.asyncio import Redis

from src.config import settings


# Naming convention for constraints (for easier Alembic migrations)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """Base class for all database models."""
    metadata = metadata


# Convert postgres:// to postgresql:// for SQLAlchemy compatibility
database_url = settings.database_url.replace("postgres://", "postgresql://", 1)

# Sync engine for migrations and non-async operations
engine = create_engine(
    database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Sync session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)

# Async engine for FastAPI endpoints
async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

async_engine = create_async_engine(
    async_database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async session dependency for FastAPI Users.
    This is an alias for get_db() but without auto-commit behavior
    as FastAPI Users manages its own transactions.

    Usage:
        Used internally by FastAPI Users for database operations.
    """
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_db() -> Session:
    """
    Get synchronous database session for migrations and scripts.

    Usage:
        with get_sync_db() as db:
            ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def init_db():
    """Initialize database by creating all tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """Drop all database tables. Use with caution!"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Redis client instance
_redis_client: Redis | None = None


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    Dependency for getting async Redis client.

    Usage:
        @router.post("/send-code")
        async def send_code(redis: Redis = Depends(get_redis)):
            ...
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = Redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    try:
        yield _redis_client
    finally:
        # Don't close the connection here as it's reused
        pass


async def close_redis():
    """Close Redis connection. Call on app shutdown."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
