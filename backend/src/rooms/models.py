"""
Room models.
Defines Room, RoomPhoto, and RoomPrice models for studio room management.
"""
from typing import Optional, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import String, ForeignKey, Integer, Numeric, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models import IDMixin, TimestampMixin

if TYPE_CHECKING:
    from src.addresses.models import Address
    from src.bookings.models import Booking


class Room(Base, IDMixin, TimestampMixin):
    """Room model representing a bookable space within a studio - matches Laravel schema."""

    __tablename__ = "rooms"

    # Basic info
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Foreign keys
    address_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("addresses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    address: Mapped["Address"] = relationship(
        "Address",
        back_populates="rooms",
    )
    photos: Mapped[list["RoomPhoto"]] = relationship(
        "RoomPhoto",
        back_populates="room",
        cascade="all, delete-orphan",
        order_by="RoomPhoto.index",
    )
    prices: Mapped[list["RoomPrice"]] = relationship(
        "RoomPrice",
        back_populates="room",
        cascade="all, delete-orphan",
    )
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="room",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Room(id={self.id}, name={self.name}, address_id={self.address_id})>"


class RoomPhoto(Base, IDMixin):
    """Room photo with ordering support - matches Laravel schema."""

    __tablename__ = "room_photos"

    # Foreign keys
    room_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Photo info
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    index: Mapped[int] = mapped_column("index", Integer, default=0, nullable=False)  # For ordering

    # Relationships
    room: Mapped["Room"] = relationship(
        "Room",
        back_populates="photos",
    )

    def __repr__(self) -> str:
        return f"<RoomPhoto(id={self.id}, room_id={self.room_id}, index={self.index})>"


class RoomPrice(Base, IDMixin, TimestampMixin):
    """Pricing tiers for room bookings based on duration - matches Laravel schema."""

    __tablename__ = "room_prices"

    # Foreign keys
    room_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Duration (in hours)
    hours: Mapped[int] = mapped_column(Integer, nullable=False)

    # Pricing
    total_price: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    price_per_hour: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)

    # Status
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    room: Mapped["Room"] = relationship(
        "Room",
        back_populates="prices",
    )

    def __repr__(self) -> str:
        return f"<RoomPrice(id={self.id}, room_id={self.room_id}, hours={self.hours}, total_price={self.total_price})>"
