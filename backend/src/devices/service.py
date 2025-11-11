"""Service layer for device business logic."""

import secrets
import hashlib
from typing import Optional
from passlib.context import CryptContext

from src.devices.repository import DeviceRepository
from src.devices.models import Device
from src.devices.schemas import (
    DeviceRegisterRequest,
    DeviceUpdateRequest,
    DeviceHeartbeatRequest,
    DeviceStatusResponse,
)
from src.exceptions import NotFoundException, ConflictException, UnauthorizedException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class DeviceService:
    """Service for device management business logic."""

    def __init__(self, repository: DeviceRepository):
        self.repository = repository

    def _generate_device_token(self) -> str:
        """Generate a secure device token."""
        return secrets.token_urlsafe(64)

    def _hash_password(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

    async def register_device(
        self, user_id: int, device_data: DeviceRegisterRequest, ip_address: str
    ) -> tuple[Device, str]:
        """
        Register a new device for a user.

        Args:
            user_id: User ID (studio owner)
            device_data: Device registration data
            ip_address: IP address of the device

        Returns:
            Tuple of (Device, device_token)

        Raises:
            ConflictException: If device already exists
        """
        # Check if device already exists by MAC address or UUID
        existing_device = await self.repository.get_device_by_mac_address(device_data.mac_address)
        if existing_device:
            raise ConflictException(f"Device with MAC address {device_data.mac_address} already registered")

        existing_device = await self.repository.get_device_by_uuid(device_data.device_uuid)
        if existing_device:
            raise ConflictException(f"Device with UUID {device_data.device_uuid} already registered")

        # Generate device token
        device_token = self._generate_device_token()

        # Hash unlock password if provided
        unlock_password_hash = None
        if device_data.unlock_password:
            unlock_password_hash = self._hash_password(device_data.unlock_password)

        # Create device
        device_dict = {
            "name": device_data.name,
            "mac_address": device_data.mac_address,
            "device_uuid": device_data.device_uuid,
            "device_token": device_token,
            "user_id": user_id,
            "os_version": device_data.os_version,
            "app_version": device_data.app_version,
            "unlock_password_hash": unlock_password_hash,
            "last_ip": ip_address,
            "is_blocked": False,
            "is_active": True,
        }

        device = await self.repository.create_device(device_dict)

        # Log registration
        await self.repository.create_device_log({
            "device_id": device.id,
            "action": "registered",
            "details": f"Device registered: {device.name}",
            "ip_address": ip_address,
        })

        return device, device_token

    async def get_user_devices(self, user_id: int) -> list[Device]:
        """Get all devices for a user."""
        return await self.repository.get_devices_by_user(user_id)

    async def get_device(self, device_id: int, user_id: int) -> Device:
        """
        Get a device by ID.

        Args:
            device_id: Device ID
            user_id: User ID (for ownership check)

        Returns:
            Device

        Raises:
            NotFoundException: If device not found
            UnauthorizedException: If user doesn't own the device
        """
        device = await self.repository.get_device_by_id(device_id)
        if not device:
            raise NotFoundException("Device not found")

        if device.user_id != user_id:
            raise UnauthorizedException("You don't have permission to access this device")

        return device

    async def update_device(
        self, device_id: int, user_id: int, update_data: DeviceUpdateRequest
    ) -> Device:
        """Update device information."""
        device = await self.get_device(device_id, user_id)

        update_dict = {}
        if update_data.name is not None:
            update_dict["name"] = update_data.name
        if update_data.notes is not None:
            update_dict["notes"] = update_data.notes
        if update_data.is_active is not None:
            update_dict["is_active"] = update_data.is_active
        if update_data.unlock_password is not None:
            update_dict["unlock_password_hash"] = self._hash_password(update_data.unlock_password)

        if update_dict:
            device = await self.repository.update_device(device_id, update_dict)

        return device

    async def block_device(self, device_id: int, user_id: int, block: bool, reason: Optional[str] = None) -> Device:
        """Block or unblock a device."""
        device = await self.get_device(device_id, user_id)

        device = await self.repository.block_device(device_id, block)

        # Log the action
        action = "blocked" if block else "unblocked"
        details = f"Device {action}"
        if reason:
            details += f": {reason}"

        await self.repository.create_device_log({
            "device_id": device_id,
            "action": action,
            "details": details,
            "ip_address": None,
        })

        return device

    async def delete_device(self, device_id: int, user_id: int) -> bool:
        """Delete a device."""
        device = await self.get_device(device_id, user_id)

        # Log deletion
        await self.repository.create_device_log({
            "device_id": device_id,
            "action": "deleted",
            "details": f"Device deleted: {device.name}",
            "ip_address": None,
        })

        return await self.repository.delete_device(device_id)

    async def check_device_status(
        self, device_uuid: str, device_token: str, ip_address: str
    ) -> DeviceStatusResponse:
        """
        Check device status (called by Mac OS script).

        Args:
            device_uuid: Device UUID
            device_token: Device authentication token
            ip_address: IP address of the device

        Returns:
            DeviceStatusResponse with blocking status

        Raises:
            UnauthorizedException: If device not found or token invalid
        """
        device = await self.repository.get_device_by_uuid(device_uuid)

        if not device:
            raise UnauthorizedException("Device not found")

        if device.device_token != device_token:
            raise UnauthorizedException("Invalid device token")

        if not device.is_active:
            raise UnauthorizedException("Device is deactivated")

        # Update heartbeat
        await self.repository.update_device_heartbeat(device.id, ip_address)

        # Log heartbeat
        await self.repository.create_device_log({
            "device_id": device.id,
            "action": "heartbeat",
            "details": "Device checked status",
            "ip_address": ip_address,
        })

        # Return status
        if device.is_blocked:
            return DeviceStatusResponse(
                is_blocked=True,
                should_lock=True,
                message="Device is blocked by studio owner"
            )
        else:
            return DeviceStatusResponse(
                is_blocked=False,
                should_lock=False,
                message="Device is active"
            )

    async def unlock_device_with_password(self, device_uuid: str, password: str) -> bool:
        """
        Unlock a device using local password.

        Args:
            device_uuid: Device UUID
            password: Unlock password

        Returns:
            True if unlocked successfully

        Raises:
            UnauthorizedException: If password is incorrect or not set
        """
        device = await self.repository.get_device_by_uuid(device_uuid)

        if not device:
            raise UnauthorizedException("Device not found")

        if not device.unlock_password_hash:
            raise UnauthorizedException("No unlock password set for this device")

        if not self._verify_password(password, device.unlock_password_hash):
            raise UnauthorizedException("Incorrect password")

        # Temporarily unblock device (admin can re-block)
        await self.repository.block_device(device.id, False)

        # Log unlock
        await self.repository.create_device_log({
            "device_id": device.id,
            "action": "unlocked_with_password",
            "details": "Device unlocked using local password",
            "ip_address": None,
        })

        return True
