"""Service layer for device business logic."""

import secrets
import hashlib
from typing import Optional
from datetime import datetime
from passlib.context import CryptContext
from cryptography.fernet import Fernet

from src.devices.repository import DeviceRepository
from src.devices.models import Device
from src.devices.schemas import (
    DeviceRegisterRequest,
    DeviceUpdateRequest,
    DeviceHeartbeatRequest,
    DeviceStatusResponse,
    StorePasswordRequest,
    DevicePasswordResponse,
)
from src.exceptions import NotFoundException, ConflictException, UnauthorizedException
from src.config import settings

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

    def _encrypt_password(self, password: str) -> str:
        """
        Encrypt a password using Fernet symmetric encryption.

        Args:
            password: Plain text password

        Returns:
            Encrypted password (base64 encoded)
        """
        if not settings.password_encryption_key:
            raise ValueError("PASSWORD_ENCRYPTION_KEY is not configured")

        fernet = Fernet(settings.password_encryption_key.encode())
        encrypted = fernet.encrypt(password.encode())
        return encrypted.decode()

    def _decrypt_password(self, encrypted_password: str) -> str:
        """
        Decrypt a password using Fernet symmetric encryption.

        Args:
            encrypted_password: Encrypted password (base64 encoded)

        Returns:
            Decrypted plain text password
        """
        if not settings.password_encryption_key:
            raise ValueError("PASSWORD_ENCRYPTION_KEY is not configured")

        fernet = Fernet(settings.password_encryption_key.encode())
        decrypted = fernet.decrypt(encrypted_password.encode())
        return decrypted.decode()

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
        """Get all devices for a user with decrypted passwords."""
        devices = await self.repository.get_devices_by_user(user_id)

        # Expunge and decrypt passwords for all devices
        for device in devices:
            self.repository.db.expunge(device)
            if device.current_password:
                try:
                    device.current_password = self._decrypt_password(device.current_password)
                except Exception:
                    # If decryption fails, leave as None
                    device.current_password = None

        return devices

    async def get_device(self, device_id: int, user_id: int) -> Device:
        """
        Get a device by ID with decrypted password.

        Args:
            device_id: Device ID
            user_id: User ID (for ownership check)

        Returns:
            Device with decrypted password

        Raises:
            NotFoundException: If device not found
            UnauthorizedException: If user doesn't own the device
        """
        device = await self.repository.get_device_by_id(device_id)
        if not device:
            raise NotFoundException("Device not found")

        if device.user_id != user_id:
            raise UnauthorizedException("You don't have permission to access this device")

        # Expunge from session to prevent tracking changes
        self.repository.db.expunge(device)

        # Decrypt password if present
        if device.current_password:
            try:
                device.current_password = self._decrypt_password(device.current_password)
            except Exception:
                # If decryption fails, leave as None
                device.current_password = None

        return device

    async def update_device(
        self, device_id: int, user_id: int, update_data: DeviceUpdateRequest
    ) -> Device:
        """Update device information."""
        from datetime import datetime, timezone

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
        if update_data.current_password is not None:
            # Encrypt password before storing (will be decrypted by locker app)
            update_dict["current_password"] = self._encrypt_password(update_data.current_password)
            update_dict["password_changed_at"] = datetime.now(timezone.utc)

        if update_dict:
            device = await self.repository.update_device(device_id, update_dict)
            # Expunge from session to prevent SQLAlchemy from tracking changes
            self.repository.db.expunge(device)

        # Decrypt password for response
        if device.current_password:
            try:
                device.current_password = self._decrypt_password(device.current_password)
            except Exception:
                device.current_password = None

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
        # Load device with user relationship to get company name
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from src.companies.models import AdminCompany, Company

        stmt = (
            select(Device)
            .where(Device.device_uuid == device_uuid)
            .options(selectinload(Device.user))
        )
        result = await self.repository.db.execute(stmt)
        device = result.scalar_one_or_none()

        if not device:
            raise UnauthorizedException("Device not found")

        if device.device_token != device_token:
            raise UnauthorizedException("Invalid device token")

        if not device.is_active:
            raise UnauthorizedException("Device is deactivated")

        # Get studio/company name from user's admin companies
        company_name = device.name  # Default to device name
        if device.user:
            stmt_company = (
                select(Company)
                .join(AdminCompany, AdminCompany.company_id == Company.id)
                .where(AdminCompany.admin_id == device.user_id)
            )
            result_company = await self.repository.db.execute(stmt_company)
            company = result_company.scalar_one_or_none()
            if company:
                company_name = company.name

        # Update heartbeat
        await self.repository.update_device_heartbeat(device.id, ip_address)

        # Log heartbeat
        await self.repository.create_device_log({
            "device_id": device.id,
            "action": "heartbeat",
            "details": "Device checked status",
            "ip_address": ip_address,
        })

        # Check if manually blocked by admin
        if device.is_blocked:
            # Build lockout info for locked devices
            lockout_info = {
                "studio_name": company_name,
                "device_uuid": device.device_uuid,
                "hourly_rate": 25.00,  # TODO: Get from device/studio settings
                "booking_url": f"{settings.frontend_url}/device-payment?device_uuid={device.device_uuid}&device_name={device.name}",
                "currency": "USD"
            }

            return DeviceStatusResponse(
                is_blocked=True,
                should_lock=True,
                message="Device is blocked by studio owner",
                lockout_info=lockout_info
            )

        # Check for active bookings
        from datetime import datetime

        now = datetime.utcnow()
        current_date = now.date()
        current_time = now.time()

        # Check if device has an active booking right now
        has_active_booking = await self.repository.has_active_booking(
            device.id,
            current_date,
            current_time
        )

        if has_active_booking:
            # Inside active booking time - don't lock
            return DeviceStatusResponse(
                is_blocked=False,
                should_lock=False,
                message="Device is active - inside booking time"
            )

        # Check if device has any bookings assigned at all
        has_any_bookings = await self.repository.has_any_bookings(device.id)

        if not has_any_bookings:
            # Device has no bookings assigned - don't lock (free device)
            return DeviceStatusResponse(
                is_blocked=False,
                should_lock=False,
                message="Device is active - no bookings assigned"
            )
        else:
            # Device has bookings but outside booking time - should lock
            # Build lockout info for payment page
            lockout_info = {
                "studio_name": company_name,
                "device_uuid": device.device_uuid,
                "hourly_rate": 25.00,  # TODO: Get from device/studio settings
                "booking_url": f"{settings.frontend_url}/device-payment?device_uuid={device.device_uuid}&device_name={device.name}",
                "currency": "USD"
            }

            return DeviceStatusResponse(
                is_blocked=False,
                should_lock=True,
                message="No active booking - device should be locked",
                lockout_info=lockout_info
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

    async def store_device_password(
        self, password_data: StorePasswordRequest
    ) -> bool:
        """
        Store encrypted device password (called by locker app after changing macOS password).

        Args:
            password_data: Password storage request data

        Returns:
            True if password stored successfully

        Raises:
            UnauthorizedException: If device not found or token invalid
        """
        device = await self.repository.get_device_by_uuid(password_data.device_uuid)

        if not device:
            raise UnauthorizedException("Device not found")

        if device.device_token != password_data.device_token:
            raise UnauthorizedException("Invalid device token")

        # Encrypt password before storing
        encrypted_password = self._encrypt_password(password_data.password)

        # Update device with encrypted password
        await self.repository.update_device(device.id, {
            "current_password": encrypted_password,
            "password_changed_at": datetime.utcnow()
        })

        # Log password change
        await self.repository.create_device_log({
            "device_id": device.id,
            "action": "password_changed",
            "details": "macOS password changed automatically",
            "ip_address": None,
        })

        return True

    async def get_device_password(
        self, device_id: int, user_id: int
    ) -> DevicePasswordResponse:
        """
        Get decrypted device password (studio owner only).

        Args:
            device_id: Device ID
            user_id: User ID (for ownership check)

        Returns:
            DevicePasswordResponse with decrypted password

        Raises:
            NotFoundException: If device not found or no password stored
            UnauthorizedException: If user doesn't own the device
        """
        device = await self.get_device(device_id, user_id)

        if not device.current_password:
            raise NotFoundException("No password stored for this device")

        # Decrypt password
        decrypted_password = self._decrypt_password(device.current_password)

        return DevicePasswordResponse(
            password=decrypted_password,
            password_changed_at=device.password_changed_at,
            device_name=device.name
        )

    async def get_device_password_by_token(
        self, device_uuid: str, device_token: str
    ) -> DevicePasswordResponse:
        """
        Get decrypted device password using device token (for locker app).

        Args:
            device_uuid: Device UUID
            device_token: Device authentication token

        Returns:
            DevicePasswordResponse with decrypted password

        Raises:
            UnauthorizedException: If device not found or token invalid
            NotFoundException: If no password stored
        """
        device = await self.repository.get_device_by_uuid(device_uuid)

        if not device:
            raise UnauthorizedException("Device not found")

        if device.device_token != device_token:
            raise UnauthorizedException("Invalid device token")

        if not device.is_active:
            raise UnauthorizedException("Device is deactivated")

        if not device.current_password:
            raise NotFoundException("No password stored for this device")

        # Decrypt password
        decrypted_password = self._decrypt_password(device.current_password)

        return DevicePasswordResponse(
            password=decrypted_password,
            password_changed_at=device.password_changed_at,
            device_name=device.name
        )

    async def create_device_payment_session(
        self,
        device_uuid: str,
        unlock_duration_hours: int
    ) -> dict:
        """
        Create Stripe checkout session for device unlock payment.

        Args:
            device_uuid: Device UUID
            unlock_duration_hours: Number of hours to unlock

        Returns:
            Dict with session_id, payment_url, and amount

        Raises:
            NotFoundException: If device not found
        """
        import stripe
        from datetime import timedelta
        from src.devices.models import DeviceUnlockSession

        device = await self.repository.get_device_by_uuid(device_uuid)

        if not device:
            raise NotFoundException("Device not found")

        # Get device owner (studio owner)
        from src.users.repository import UserRepository
        user_repo = UserRepository(self.repository.db)
        studio_owner = await user_repo.get_user_by_id(device.user_id)

        if not studio_owner or not studio_owner.stripe_account_id:
            raise NotFoundException("Studio owner not found or Stripe account not configured")

        # Calculate amount (hourly rate from studio owner settings or default)
        hourly_rate = 25.00  # Default hourly rate in USD
        # TODO: Get hourly rate from studio/device settings
        total_amount = hourly_rate * unlock_duration_hours
        amount_cents = int(total_amount * 100)

        # Calculate service fee (4%)
        service_fee_cents = int(amount_cents * 0.04)

        # Create Stripe checkout session
        stripe.api_key = settings.stripe_api_key
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Device Time Payment - {device.name}',
                        'description': f'{unlock_duration_hours} hour(s) unlock',
                    },
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{settings.frontend_url}/device-payment-success?session_id={{CHECKOUT_SESSION_ID}}&device_uuid={device_uuid}",
            cancel_url=f"{settings.frontend_url}/device/{device_uuid}",
            payment_intent_data={
                'application_fee_amount': service_fee_cents,
                'transfer_data': {
                    'destination': studio_owner.stripe_account_id,
                },
            },
            metadata={
                'device_uuid': device_uuid,
                'device_id': str(device.id),
                'unlock_duration_hours': str(unlock_duration_hours),
            },
            expires_at=int((datetime.now() + timedelta(minutes=30)).timestamp()),
        )

        # Create unlock session record
        unlock_session = DeviceUnlockSession(
            device_id=device.id,
            stripe_session_id=session.id,
            amount=total_amount,
            currency='USD',
            status='pending',
            unlock_duration_hours=unlock_duration_hours,
        )

        self.repository.db.add(unlock_session)
        await self.repository.db.flush()

        return {
            'session_id': session.id,
            'payment_url': session.url,
            'amount': total_amount,
            'currency': 'USD',
            'unlock_session_id': unlock_session.id
        }

    async def process_device_payment_success(
        self,
        session_id: str,
        device_uuid: str
    ) -> dict:
        """
        Process successful device unlock payment.

        Args:
            session_id: Stripe checkout session ID
            device_uuid: Device UUID

        Returns:
            Dict with success status and expiration time

        Raises:
            NotFoundException: If unlock session not found
        """
        import stripe
        from datetime import timedelta
        from sqlalchemy import select
        from src.devices.models import DeviceUnlockSession

        # Get unlock session
        stmt = select(DeviceUnlockSession).where(
            DeviceUnlockSession.stripe_session_id == session_id
        )
        result = await self.repository.db.execute(stmt)
        unlock_session = result.scalar_one_or_none()

        if not unlock_session:
            raise NotFoundException("Unlock session not found")

        # Verify with Stripe
        stripe.api_key = settings.stripe_api_key
        stripe_session = stripe.checkout.Session.retrieve(session_id)

        if stripe_session.payment_status != 'paid':
            return {
                'success': False,
                'message': 'Payment not completed',
            }

        # Update unlock session
        unlock_session.status = 'paid'
        unlock_session.paid_at = datetime.now()
        unlock_session.expires_at = datetime.now() + timedelta(hours=unlock_session.unlock_duration_hours)
        unlock_session.stripe_payment_intent = stripe_session.payment_intent

        await self.repository.db.flush()

        # Get device to fetch password
        device = await self.repository.get_by_id(unlock_session.device_id)
        if not device:
            raise NotFoundException("Device not found")

        # Decrypt password if available
        decrypted_password = None
        if device.current_password:
            try:
                decrypted_password = self._decrypt_password(device.current_password)
            except Exception as e:
                logger.error(f"Failed to decrypt device password: {e}")

        return {
            'success': True,
            'message': 'Device unlocked successfully',
            'unlock_session_id': unlock_session.id,
            'expires_at': unlock_session.expires_at,
            'device_name': device.name,
            'device_password': decrypted_password
        }
