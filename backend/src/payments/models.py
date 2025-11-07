"""
Payment models.
Defines Charge, Payout, SquareLocation, and SquareToken models for payment processing.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import String, ForeignKey, Integer, Numeric, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models import IDMixin, TimestampMixin

if TYPE_CHECKING:
    from src.bookings.models import Booking
    from src.auth.models import User


class Charge(Base, IDMixin, TimestampMixin):
    """Charge model representing a payment transaction."""

    __tablename__ = "charges"

    # Foreign keys
    booking_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Stripe fields
    stripe_session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    stripe_payment_intent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)

    # Square fields
    square_payment_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)
    order_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Payment details
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # pending, succeeded, failed, etc.

    # Refund fields
    refund_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    refund_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    refund_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    booking: Mapped["Booking"] = relationship(
        "Booking",
        back_populates="charges",
    )

    def __repr__(self) -> str:
        return f"<Charge(id={self.id}, booking_id={self.booking_id}, amount={self.amount}, status={self.status})>"


class Payout(Base, IDMixin, TimestampMixin):
    """Payout model representing payouts to studio owners."""

    __tablename__ = "payouts"

    # Foreign keys
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Payout details
    payout_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)  # From Stripe/Square
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)  # pending, paid, failed, etc.

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="payouts",
    )

    def __repr__(self) -> str:
        return f"<Payout(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.status})>"


class SquareLocation(Base, IDMixin, TimestampMixin):
    """Square location associated with a user/studio owner."""

    __tablename__ = "square_locations"

    # Foreign keys
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Square info
    square_location_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<SquareLocation(id={self.id}, user_id={self.user_id}, name={self.name})>"


class SquareToken(Base, IDMixin, TimestampMixin):
    """Square OAuth tokens for user authentication."""

    __tablename__ = "square_tokens"

    # Foreign keys
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    square_location_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("square_locations.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Token info
    access_token: Mapped[str] = mapped_column(String(500), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(500), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="square_tokens",
    )

    def __repr__(self) -> str:
        return f"<SquareToken(id={self.id}, user_id={self.user_id})>"
