"""Device models for studio device management and blocking."""

from datetime import datetime as datetime_type
from decimal import Decimal
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from src.models import IDMixin, TimestampMixin


class Device(Base, IDMixin, TimestampMixin):
    """Device model for Mac OS computers connected to studios."""

    __tablename__ = "devices"

    # Device identification
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    mac_address: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    device_uuid: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    # Authentication
    device_token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)

    # Ownership - link to user (studio owner)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Device status
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Activity tracking
    last_heartbeat: Mapped[datetime_type | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # Device info
    os_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    app_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Unlock password (hashed)
    unlock_password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Unlock fee for Cash App payments (default $10)
    unlock_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("10.00"), nullable=False)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="devices")
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="device")
    unlock_sessions: Mapped[list["DeviceUnlockSession"]] = relationship(
        "DeviceUnlockSession", back_populates="device", cascade="all, delete-orphan"
    )


class DeviceLog(Base, IDMixin, TimestampMixin):
    """Log of device actions and status changes."""

    __tablename__ = "device_logs"

    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # blocked, unblocked, heartbeat, registered
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # Relationships
    device: Mapped["Device"] = relationship("Device")


class DeviceUnlockSession(Base, IDMixin, TimestampMixin):
    """Tracks paid unlock sessions for devices via Cash App."""

    __tablename__ = "device_unlock_sessions"

    # Link to device
    device_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Stripe payment info
    stripe_session_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    stripe_payment_intent: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    # Payment details
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)

    # Status: pending, paid, expired, failed
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)

    # Unlock duration
    unlock_duration_hours: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Timing
    paid_at: Mapped[datetime_type | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime_type | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    device: Mapped["Device"] = relationship("Device", back_populates="unlock_sessions")
