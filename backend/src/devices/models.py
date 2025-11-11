"""Device models for studio device management and blocking."""

from datetime import datetime as datetime_type
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, Text
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

    # Notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="devices")


class DeviceLog(Base, IDMixin, TimestampMixin):
    """Log of device actions and status changes."""

    __tablename__ = "device_logs"

    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # blocked, unblocked, heartbeat, registered
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # Relationships
    device: Mapped["Device"] = relationship("Device")
