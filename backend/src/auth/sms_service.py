"""
SMS Authentication Service.
Handles SMS verification code generation, storage, and validation.
"""
import random
import secrets
import logging
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from redis.asyncio import Redis
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioRestException

from src.auth.models import User
from src.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """Service for SMS-based authentication."""

    def __init__(
        self,
        db: AsyncSession,
        redis: Redis,
        twilio_account_sid: str,
        twilio_auth_token: str,
        twilio_phone_number: str,
    ):
        """Initialize SMS service.

        Args:
            db: Database session
            redis: Redis client for storing verification codes
            twilio_account_sid: Twilio account SID
            twilio_auth_token: Twilio auth token
            twilio_phone_number: Twilio phone number to send from
        """
        self.db = db
        self.redis = redis
        self.twilio_client = TwilioClient(twilio_account_sid, twilio_auth_token)
        self.twilio_phone_number = twilio_phone_number
        self.code_expiry = 300  # 5 minutes in seconds

    @staticmethod
    def generate_code(length: int = 6) -> str:
        """Generate a random numeric verification code.

        Args:
            length: Length of the code (default: 6)

        Returns:
            Numeric verification code as string
        """
        return "".join([str(random.randint(0, 9)) for _ in range(length)])

    async def send_verification_code(self, phone: str) -> Tuple[str, int]:
        """Send SMS verification code to phone number.

        Args:
            phone: Phone number in E164 format (+1234567890)

        Returns:
            Tuple of (code, expires_in_seconds)

        Raises:
            TwilioRestException: If SMS sending fails
        """
        # Generate 6-digit code
        code = self.generate_code()

        # Store in Redis with expiry
        redis_key = f"sms_code:{phone}"
        await self.redis.setex(redis_key, self.code_expiry, code)

        logger.info(f"Stored SMS code for {phone}: {code} (expires in {self.code_expiry}s)")

        # Send SMS via Twilio
        try:
            message = self.twilio_client.messages.create(
                body=f"Your verification code is: {code}\n\nThis code expires in 5 minutes.",
                from_=self.twilio_phone_number,
                to=phone,
            )
            logger.info(f"SMS sent to {phone}, message SID: {message.sid}")
        except TwilioRestException as e:
            logger.error(f"Failed to send SMS to {phone}: {e}")
            # Clean up Redis if SMS fails
            await self.redis.delete(redis_key)
            raise

        return code, self.code_expiry

    async def verify_code(self, phone: str, code: str) -> bool:
        """Verify SMS code for phone number.

        Args:
            phone: Phone number in E164 format
            code: 6-digit verification code

        Returns:
            True if code is valid, False otherwise
        """
        redis_key = f"sms_code:{phone}"

        # Get stored code from Redis
        stored_code = await self.redis.get(redis_key)

        if not stored_code:
            logger.warning(f"No code found for {phone} (expired or never sent)")
            return False

        # Compare codes (constant-time comparison for security)
        if not secrets.compare_digest(stored_code, code):
            logger.warning(f"Invalid code for {phone}")
            return False

        # Delete code after successful verification (single-use)
        await self.redis.delete(redis_key)
        logger.info(f"Successfully verified code for {phone}")

        return True

    async def get_or_create_user(self, phone: str) -> Tuple[User, bool]:
        """Get existing user by phone or create new one.

        Args:
            phone: Phone number in E164 format

        Returns:
            Tuple of (User, is_new_user)
        """
        # Try to find existing user by phone
        stmt = select(User).where(User.phone == phone)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            logger.info(f"Found existing user for phone {phone}: {user.id}")
            return user, False

        # Create new user
        user = User(
            phone=phone,
            email=f"{phone}@sms.temp",  # Temporary email (required field)
            firstname="",
            lastname="",
            role="user",
            email_verified_at=datetime.utcnow(),  # Auto-verify SMS users
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"Created new user for phone {phone}: {user.id}")
        return user, True

    async def authenticate_with_sms(self, phone: str, code: str) -> Optional[Tuple[User, bool]]:
        """Authenticate user via SMS code verification.

        Args:
            phone: Phone number in E164 format
            code: 6-digit verification code

        Returns:
            Tuple of (User, is_new_user) if successful, None if verification fails
        """
        # Verify the code
        is_valid = await self.verify_code(phone, code)
        if not is_valid:
            return None

        # Get or create user
        user, is_new_user = await self.get_or_create_user(phone)
        return user, is_new_user
