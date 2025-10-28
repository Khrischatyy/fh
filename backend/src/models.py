"""
Base SQLAlchemy models shared across modules.
This file contains common mixins and base model classes.
"""
from datetime import datetime
from typing import Any
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, declarative_mixin
from sqlalchemy.sql import func


@declarative_mixin
class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


@declarative_mixin
class IDMixin:
    """Mixin for integer primary key ID."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)


def to_dict(model: Any) -> dict:
    """Convert SQLAlchemy model to dictionary."""
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}
