"""
Payment service - Routes payment operations to appropriate gateway.
Acts as a facade for different payment gateways (Stripe, Square).
"""
from typing import Dict
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.payments.gateways.base import PaymentGateway
from src.payments.gateways.stripe_gateway import StripeGateway
from src.payments.gateways.square_gateway import SquareGateway
from src.bookings.models import Booking
from src.auth.models import User
from src.exceptions import BadRequestException


class PaymentService:
    """
    Payment service that routes to appropriate gateway.

    Similar to Laravel's PaymentService pattern.
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initialize payment service with database session.

        Args:
            db_session: SQLAlchemy async session
        """
        self.db = db_session
        self._stripe_gateway = None
        self._square_gateway = None

    def _get_gateway(self, gateway_name: str) -> PaymentGateway:
        """
        Get payment gateway instance by name.

        Args:
            gateway_name: Gateway name ('stripe' or 'square')

        Returns:
            PaymentGateway instance

        Raises:
            BadRequestException: If gateway is not supported
        """
        if gateway_name == 'stripe':
            if not self._stripe_gateway:
                self._stripe_gateway = StripeGateway(self.db)
            return self._stripe_gateway
        elif gateway_name == 'square':
            if not self._square_gateway:
                self._square_gateway = SquareGateway(self.db)
            return self._square_gateway
        else:
            raise BadRequestException(f"Unsupported payment gateway: {gateway_name}")

    async def create_payment_session(
        self,
        booking: Booking,
        amount: Decimal,
        studio_owner: User
    ) -> Dict[str, str]:
        """
        Create payment session using studio owner's configured gateway.

        Args:
            booking: Booking instance
            amount: Amount to charge
            studio_owner: Studio owner who will receive payment

        Returns:
            Dictionary with session_id and payment_url

        Raises:
            BadRequestException: If studio owner has no payment gateway configured
        """
        if not studio_owner.payment_gateway:
            raise BadRequestException("Studio owner has no payment gateway configured")

        gateway = self._get_gateway(studio_owner.payment_gateway)
        return await gateway.create_payment_session(booking, amount, studio_owner)

    async def verify_payment_session(
        self,
        session_id: str,
        gateway_name: str,
        studio_owner: User
    ):
        """
        Verify payment session.

        Args:
            session_id: Payment session ID
            gateway_name: Gateway name
            studio_owner: Studio owner

        Returns:
            Session data or None
        """
        gateway = self._get_gateway(gateway_name)
        return await gateway.verify_payment_session(session_id, studio_owner)

    async def process_payment_success(
        self,
        session_id: str,
        booking_id: int,
        gateway_name: str,
        studio_owner: User
    ) -> Dict[str, any]:
        """
        Process successful payment.

        Args:
            session_id: Payment session ID
            booking_id: Booking ID
            gateway_name: Gateway name
            studio_owner: Studio owner

        Returns:
            Dictionary with success status
        """
        gateway = self._get_gateway(gateway_name)
        return await gateway.process_payment_success(session_id, booking_id, studio_owner)

    async def refund_payment(
        self,
        booking: Booking,
        studio_owner: User
    ) -> Dict[str, any]:
        """
        Refund payment for a booking.

        Args:
            booking: Booking to refund
            studio_owner: Studio owner

        Returns:
            Dictionary with success status
        """
        if not studio_owner.payment_gateway:
            raise BadRequestException("Studio owner has no payment gateway configured")

        gateway = self._get_gateway(studio_owner.payment_gateway)
        return await gateway.refund_payment(booking, studio_owner)

    async def retrieve_account(self, user: User):
        """
        Retrieve payment account for user.

        Args:
            user: User to retrieve account for

        Returns:
            Account information
        """
        if not user.payment_gateway:
            raise BadRequestException("User has no payment gateway configured")

        gateway = self._get_gateway(user.payment_gateway)
        return await gateway.retrieve_account(user)

    async def retrieve_balance(self, user: User):
        """
        Retrieve account balance for user.

        Args:
            user: User to retrieve balance for

        Returns:
            Balance information
        """
        if not user.payment_gateway:
            raise BadRequestException("User has no payment gateway configured")

        gateway = self._get_gateway(user.payment_gateway)
        return await gateway.retrieve_balance(user)
