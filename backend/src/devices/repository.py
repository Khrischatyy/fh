"""Repository layer for device data access."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.devices.models import Device, DeviceLog


class DeviceRepository:
    """Repository for device database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_device(self, device_data: dict) -> Device:
        """Create a new device."""
        device = Device(**device_data)
        self.db.add(device)
        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def get_device_by_id(self, device_id: int) -> Optional[Device]:
        """Get device by ID."""
        result = await self.db.execute(
            select(Device).where(Device.id == device_id)
        )
        return result.scalar_one_or_none()

    async def get_device_by_uuid(self, device_uuid: str) -> Optional[Device]:
        """Get device by UUID."""
        result = await self.db.execute(
            select(Device).where(Device.device_uuid == device_uuid)
        )
        return result.scalar_one_or_none()

    async def get_device_by_token(self, device_token: str) -> Optional[Device]:
        """Get device by token."""
        result = await self.db.execute(
            select(Device).where(Device.device_token == device_token)
        )
        return result.scalar_one_or_none()

    async def get_device_by_mac_address(self, mac_address: str) -> Optional[Device]:
        """Get device by MAC address."""
        result = await self.db.execute(
            select(Device).where(Device.mac_address == mac_address)
        )
        return result.scalar_one_or_none()

    async def get_devices_by_user(self, user_id: int) -> list[Device]:
        """Get all devices for a user."""
        result = await self.db.execute(
            select(Device)
            .where(Device.user_id == user_id)
            .order_by(Device.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_device(self, device_id: int, update_data: dict) -> Optional[Device]:
        """Update device information."""
        await self.db.execute(
            update(Device)
            .where(Device.id == device_id)
            .values(**update_data)
        )
        await self.db.commit()
        return await self.get_device_by_id(device_id)

    async def update_device_heartbeat(self, device_id: int, ip_address: str) -> None:
        """Update device last heartbeat timestamp."""
        await self.db.execute(
            update(Device)
            .where(Device.id == device_id)
            .values(
                last_heartbeat=datetime.now(timezone.utc),
                last_ip=ip_address
            )
        )
        await self.db.commit()

    async def block_device(self, device_id: int, is_blocked: bool) -> Optional[Device]:
        """Block or unblock a device."""
        await self.db.execute(
            update(Device)
            .where(Device.id == device_id)
            .values(is_blocked=is_blocked)
        )
        await self.db.commit()
        return await self.get_device_by_id(device_id)

    async def delete_device(self, device_id: int) -> bool:
        """Delete a device."""
        device = await self.get_device_by_id(device_id)
        if device:
            await self.db.delete(device)
            await self.db.commit()
            return True
        return False

    async def create_device_log(self, log_data: dict) -> DeviceLog:
        """Create a device log entry."""
        log = DeviceLog(**log_data)
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_device_logs(self, device_id: int, limit: int = 50) -> list[DeviceLog]:
        """Get recent logs for a device."""
        result = await self.db.execute(
            select(DeviceLog)
            .where(DeviceLog.device_id == device_id)
            .order_by(DeviceLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def has_active_booking(self, device_id: int, current_date, current_time) -> bool:
        """Check if device has an active booking at the given date/time."""
        from src.bookings.models import Booking
        from sqlalchemy import and_

        stmt = (
            select(Booking)
            .where(
                and_(
                    Booking.device_id == device_id,
                    Booking.status_id == 2,  # Confirmed status
                    Booking.date == current_date,
                    Booking.start_time <= current_time,
                    Booking.end_time >= current_time
                )
            )
        )
        result = await self.db.execute(stmt)
        active_booking = result.scalar_one_or_none()
        return active_booking is not None

    async def has_any_bookings(self, device_id: int) -> bool:
        """Check if device has any bookings assigned (past, present, or future)."""
        from src.bookings.models import Booking

        stmt = (
            select(Booking)
            .where(Booking.device_id == device_id)
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
