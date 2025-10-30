"""
Base payment gateway interface.
Defines the contract that all payment gateways must implement.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from decimal import Decimal

from src.bookings.models import Booking
from src.auth.models import User


class PaymentGateway(ABC):
    """Abstract base class for payment gateways."""

    @abstractmethod
    async def create_payment_session(
        self,
        booking: Booking,
        amount: Decimal,
        studio_owner: User
    ) -> Dict[str, str]:
        """
        Create a payment checkout session.

        Args:
            booking: Booking instance
            amount: Amount to charge (in dollars, not cents)
            studio_owner: User who owns the studio (receives payment)

        Returns:
            Dictionary with session_id and payment_url

        Raises:
            Exception: If payment session creation fails
        """
        pass

    @abstractmethod
    async def verify_payment_session(
        self,
        session_id: str,
        studio_owner: User
    ) -> Optional[Dict]:
        """
        Verify a payment session exists and retrieve its data.

        Args:
            session_id: Payment session ID
            studio_owner: Studio owner

        Returns:
            Session data dictionary or None if not found
        """
        pass

    @abstractmethod
    async def process_payment_success(
        self,
        session_id: str,
        booking_id: int,
        studio_owner: User
    ) -> Dict[str, any]:
        """
        Process successful payment and update records.

        Args:
            session_id: Payment session ID
            booking_id: Booking ID
            studio_owner: Studio owner

        Returns:
            Dictionary with success status and message
        """
        pass

    @abstractmethod
    async def refund_payment(
        self,
        booking: Booking,
        studio_owner: User
    ) -> Dict[str, any]:
        """
        Refund a payment for a booking.

        Args:
            booking: Booking to refund
            studio_owner: Studio owner

        Returns:
            Dictionary with success status and message
        """
        pass

    @abstractmethod
    async def retrieve_account(self, user: User) -> Dict:
        """
        Retrieve payment account information for a user.

        Args:
            user: User to retrieve account for

        Returns:
            Account information dictionary
        """
        pass

    @abstractmethod
    async def retrieve_balance(self, user: User) -> Dict:
        """
        Retrieve account balance for a user.

        Args:
            user: User to retrieve balance for

        Returns:
            Balance information dictionary
        """
        pass
