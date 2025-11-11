"""
Booking models.
Defines Booking and BookingStatus models for room reservations.
"""
from datetime import datetime, date, time
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer, DateTime, Date, Time, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models import IDMixin, TimestampMixin

if TYPE_CHECKING:
    from src.rooms.models import Room
    from src.auth.models import User
    from src.addresses.models import Address
    from src.payments.models import Charge


class BookingStatus(Base, IDMixin, TimestampMixin):
    """Booking status lookup table."""

    __tablename__ = "booking_statuses"

    # Basic info
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="status",
    )

    def __repr__(self) -> str:
        return f"<BookingStatus(id={self.id}, name={self.name})>"


class Booking(Base, IDMixin, TimestampMixin):
    """Booking model representing a room reservation."""

    __tablename__ = "bookings"

    # Foreign keys
    room_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("booking_statuses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        default=1,
    )

    # Booking time details
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)  # For multi-day bookings

    # Temporary payment link (for pending payments)
    temporary_payment_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    temporary_payment_link_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    room: Mapped["Room"] = relationship(
        "Room",
        back_populates="bookings",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="bookings",
    )
    status: Mapped["BookingStatus"] = relationship(
        "BookingStatus",
        back_populates="bookings",
    )
    charges: Mapped[list["Charge"]] = relationship(
        "Charge",
        back_populates="booking",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Booking(id={self.id}, room_id={self.room_id}, user_id={self.user_id}, date={self.date})>"
