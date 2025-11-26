"""Service layer for device business logic."""

import secrets
import hashlib
import logging
import stripe
from typing import Optional, Dict
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

from src.devices.repository import DeviceRepository
from src.devices.models import Device, DeviceUnlockSession
from src.devices.schemas import (
    DeviceRegisterRequest,
    DeviceUpdateRequest,
    DeviceHeartbeatRequest,
    DeviceStatusResponse,
)
from src.exceptions import NotFoundException, ConflictException, UnauthorizedException, BadRequestException
from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


class DeviceService:
    """Service for device management business logic."""

    SERVICE_FEE_PERCENTAGE = Decimal("0.04")  # 4% service fee
    UNLOCK_DURATION_HOURS = 1  # Device unlocked for 1 hour after payment
    PAYMENT_LINK_EXPIRY_MINUTES = 30  # Payment link expires in 30 minutes

    def __init__(self, repository: DeviceRepository):
        self.repository = repository
        stripe.api_key = settings.stripe_api_key

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
        if update_data.unlock_fee is not None:
            update_dict["unlock_fee"] = update_data.unlock_fee

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

        # Check if manually blocked by admin
        if device.is_blocked:
            return DeviceStatusResponse(
                is_blocked=True,
                should_lock=True,
                message="Device is blocked by studio owner"
            )

        # Check for active bookings
        now = datetime.now(timezone.utc)
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

        # Check if device has an active paid unlock session
        active_unlock = await self.repository.get_active_unlock_session(device.id)
        if active_unlock:
            # Calculate remaining time
            remaining = active_unlock.expires_at - now
            remaining_minutes = int(remaining.total_seconds() / 60)
            return DeviceStatusResponse(
                is_blocked=False,
                should_lock=False,
                message=f"Device unlocked via payment ({remaining_minutes} min remaining)"
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
            return DeviceStatusResponse(
                is_blocked=False,
                should_lock=True,
                message="No active booking - device should be locked"
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

    # ============================================
    # Payment Link Methods
    # ============================================

    async def generate_payment_link(
        self, device_uuid: str, device_token: str
    ) -> Dict[str, any]:
        """
        Generate a Stripe Checkout payment link for device unlock via Cash App.

        Args:
            device_uuid: Device UUID
            device_token: Device authentication token

        Returns:
            Dict with payment_url, session_id, amount, expires_in_minutes

        Raises:
            UnauthorizedException: If device not found or token invalid
            BadRequestException: If device owner has no Stripe account
        """
        # Get device with user (owner) loaded
        device = await self.repository.get_device_with_user(device_uuid)

        if not device:
            raise UnauthorizedException("Device not found")

        if device.device_token != device_token:
            raise UnauthorizedException("Invalid device token")

        if not device.is_active:
            raise UnauthorizedException("Device is deactivated")

        # Get device owner (studio owner)
        owner = device.user
        if not owner.stripe_account_id:
            raise BadRequestException(
                "Device owner does not have a Stripe account configured. "
                "Payment cannot be processed."
            )

        # Calculate amounts
        amount = device.unlock_fee
        amount_cents = int(amount * 100)
        service_fee_cents = int(amount_cents * float(self.SERVICE_FEE_PERCENTAGE))

        try:
            # Create Stripe Checkout session with Cash App ONLY
            session = stripe.checkout.Session.create(
                mode='payment',
                payment_method_types=['cashapp'],  # Cash App ONLY
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Device Unlock',
                            'description': f'Unlock {device.name} for {self.UNLOCK_DURATION_HOURS} hour(s)',
                        },
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                }],
                payment_intent_data={
                    'application_fee_amount': service_fee_cents,  # 4% to platform
                    'transfer_data': {
                        'destination': owner.stripe_account_id,  # Rest to device owner
                    },
                },
                metadata={
                    'type': 'device_unlock',
                    'device_id': str(device.id),
                    'device_uuid': device_uuid,
                    'unlock_hours': str(self.UNLOCK_DURATION_HOURS),
                },
                success_url=f"{settings.frontend_url}/unlock-success",
                cancel_url=f"{settings.frontend_url}/unlock-cancel",
                expires_at=int((datetime.now(timezone.utc) + timedelta(minutes=self.PAYMENT_LINK_EXPIRY_MINUTES)).timestamp()),
            )

            # Create unlock session record in database
            await self.repository.create_unlock_session({
                'device_id': device.id,
                'stripe_session_id': session.id,
                'amount': amount,
                'currency': 'USD',
                'status': 'pending',
                'unlock_duration_hours': self.UNLOCK_DURATION_HOURS,
            })

            # Log payment link generation
            await self.repository.create_device_log({
                "device_id": device.id,
                "action": "payment_link_generated",
                "details": f"Payment link generated for ${amount} unlock",
                "ip_address": None,
            })

            logger.info(f"Stripe Cash App checkout session created: {session.id} for device {device.id}")

            return {
                'payment_url': session.url,
                'session_id': session.id,
                'amount': amount,
                'expires_in_minutes': self.PAYMENT_LINK_EXPIRY_MINUTES,
            }

        except stripe.StripeError as e:
            logger.error(f"Stripe error creating payment link: {str(e)}")
            raise BadRequestException(f"Payment link creation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating payment link: {str(e)}")
            raise BadRequestException(f"Payment link creation failed: {str(e)}")

    async def process_unlock_payment(
        self, stripe_session_id: str, payment_intent_id: str
    ) -> bool:
        """
        Process a successful unlock payment from Stripe webhook.

        Args:
            stripe_session_id: Stripe Checkout session ID
            payment_intent_id: Stripe PaymentIntent ID

        Returns:
            True if processed successfully

        Raises:
            NotFoundException: If unlock session not found
        """
        # Get unlock session
        unlock_session = await self.repository.get_unlock_session_by_stripe_id(stripe_session_id)

        if not unlock_session:
            logger.warning(f"Unlock session not found for Stripe session: {stripe_session_id}")
            raise NotFoundException("Unlock session not found")

        if unlock_session.status == 'paid':
            logger.info(f"Unlock session {stripe_session_id} already processed")
            return True

        # Calculate expiration time
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=unlock_session.unlock_duration_hours)

        # Update session to paid
        await self.repository.update_unlock_session(unlock_session.id, {
            'status': 'paid',
            'stripe_payment_intent': payment_intent_id,
            'paid_at': now,
            'expires_at': expires_at,
        })

        # Log the unlock
        await self.repository.create_device_log({
            "device_id": unlock_session.device_id,
            "action": "unlocked_via_payment",
            "details": f"Device unlocked via Cash App payment. Expires at {expires_at.isoformat()}",
            "ip_address": None,
        })

        logger.info(f"Device {unlock_session.device_id} unlocked via payment. Expires at {expires_at}")

        return True
