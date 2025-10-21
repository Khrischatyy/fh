"""
Address and Studio models.
Defines Address (studio), OperatingHour, StudioClosure, Equipment, EquipmentType, and Badge models.
"""
from datetime import datetime, time, date
from typing import Optional, TYPE_CHECKING
from decimal import Decimal
import enum
from sqlalchemy import (
    String, ForeignKey, Integer, Numeric, DateTime, Time, Date,
    Boolean, Text, Table, Column, Enum as SQLEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models import IDMixin, TimestampMixin

if TYPE_CHECKING:
    from src.companies.models import Company
    from src.geographic.models import City
    from src.rooms.models import Room
    from src.bookings.models import Booking
    from src.messages.models import Message
    from src.auth.models import User


class OperationMode(str, enum.Enum):
    """Operation mode enumeration."""
    OPEN = "open"
    CLOSED = "closed"
    BY_APPOINTMENT = "by_appointment"


# Association table for address equipment
address_equipment = Table(
    "address_equipment",
    Base.metadata,
    Column("address_id", Integer, ForeignKey("addresses.id", ondelete="CASCADE"), primary_key=True),
    Column("equipment_id", Integer, ForeignKey("equipment.id", ondelete="CASCADE"), primary_key=True),
)

# Association table for address badges (amenities)
address_badge = Table(
    "address_badge",
    Base.metadata,
    Column("address_id", Integer, ForeignKey("addresses.id", ondelete="CASCADE"), primary_key=True),
    Column("badge_id", Integer, ForeignKey("badges.id", ondelete="CASCADE"), primary_key=True),
)


class Address(Base, IDMixin, TimestampMixin):
    """Address model representing a studio location."""

    __tablename__ = "addresses"

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Location
    street: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(11, 8), nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Foreign keys
    city_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Financial
    available_balance: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
        nullable=False,
    )

    # Media
    cover_photo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    city: Mapped["City"] = relationship(
        "City",
        back_populates="addresses",
    )
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="addresses",
    )
    rooms: Mapped[list["Room"]] = relationship(
        "Room",
        back_populates="address",
        cascade="all, delete-orphan",
    )
    operating_hours: Mapped[list["OperatingHour"]] = relationship(
        "OperatingHour",
        back_populates="address",
        cascade="all, delete-orphan",
    )
    studio_closures: Mapped[list["StudioClosure"]] = relationship(
        "StudioClosure",
        back_populates="address",
        cascade="all, delete-orphan",
    )
    equipment: Mapped[list["Equipment"]] = relationship(
        "Equipment",
        secondary=address_equipment,
        back_populates="addresses",
    )
    badges: Mapped[list["Badge"]] = relationship(
        "Badge",
        secondary=address_badge,
        back_populates="addresses",
    )
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="address",
        cascade="all, delete-orphan",
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="address",
    )
    # Temporarily disabled User relationships until association tables are configured
    # favorited_by_users: Mapped[list["User"]] = relationship(
    #     "User",
    #     secondary="favorite_studios",
    #     back_populates="favorite_addresses",
    # )
    # engineers: Mapped[list["User"]] = relationship(
    #     "User",
    #     secondary="engineer_addresses",
    #     back_populates="engineer_addresses",
    # )

    def __repr__(self) -> str:
        return f"<Address(id={self.id}, name={self.name}, slug={self.slug})>"


class OperatingHour(Base, IDMixin, TimestampMixin):
    """Operating hours for a studio."""

    __tablename__ = "operating_hours"

    # Foreign keys
    address_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("addresses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Schedule
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    operation_mode: Mapped[OperationMode] = mapped_column(
        SQLEnum(OperationMode, name="operation_mode_enum"),
        default=OperationMode.OPEN,
        nullable=False,
    )

    # Relationships
    address: Mapped["Address"] = relationship(
        "Address",
        back_populates="operating_hours",
    )

    def __repr__(self) -> str:
        return f"<OperatingHour(id={self.id}, address_id={self.address_id}, day={self.day_of_week})>"


class StudioClosure(Base, IDMixin, TimestampMixin):
    """Studio closure periods (holidays, maintenance, etc.)."""

    __tablename__ = "studio_closures"

    # Foreign keys
    address_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("addresses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Closure period
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    address: Mapped["Address"] = relationship(
        "Address",
        back_populates="studio_closures",
    )

    def __repr__(self) -> str:
        return f"<StudioClosure(id={self.id}, address_id={self.address_id}, start={self.start_date})>"


class EquipmentType(Base, IDMixin, TimestampMixin):
    """Equipment type/category."""

    __tablename__ = "equipment_types"

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # Relationships
    equipment: Mapped[list["Equipment"]] = relationship(
        "Equipment",
        back_populates="equipment_type",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<EquipmentType(id={self.id}, name={self.name})>"


class Equipment(Base, IDMixin, TimestampMixin):
    """Equipment available at studios."""

    __tablename__ = "equipment"

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Foreign keys
    equipment_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("equipment_types.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    equipment_type: Mapped["EquipmentType"] = relationship(
        "EquipmentType",
        back_populates="equipment",
    )
    addresses: Mapped[list["Address"]] = relationship(
        "Address",
        secondary=address_equipment,
        back_populates="equipment",
    )

    def __repr__(self) -> str:
        return f"<Equipment(id={self.id}, name={self.name})>"


class Badge(Base, IDMixin, TimestampMixin):
    """Badge/amenity tags for studios (e.g., WiFi, Parking, etc.)."""

    __tablename__ = "badges"

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Icon name or path

    # Relationships
    addresses: Mapped[list["Address"]] = relationship(
        "Address",
        secondary=address_badge,
        back_populates="badges",
    )

    def __repr__(self) -> str:
        return f"<Badge(id={self.id}, name={self.name})>"
