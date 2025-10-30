"""
Square payment gateway implementation.
TODO: Implement Square payment methods.
"""
from typing import Dict, Optional
from decimal import Decimal

from src.payments.gateways.base import PaymentGateway
from src.bookings.models import Booking
from src.auth.models import User
from src.exceptions import NotImplementedException


class SquareGateway(PaymentGateway):
    """Square payment gateway implementation (placeholder for future)."""

    def __init__(self, db_session):
        """Initialize Square gateway with database session."""
        self.db = db_session

    async def create_payment_session(
        self,
        booking: Booking,
        amount: Decimal,
        studio_owner: User
    ) -> Dict[str, str]:
        """Create Square payment session."""
        raise NotImplementedException("Square payment gateway not yet implemented")

    async def verify_payment_session(
        self,
        session_id: str,
        studio_owner: User
    ) -> Optional[Dict]:
        """Verify Square payment session."""
        raise NotImplementedException("Square payment gateway not yet implemented")

    async def process_payment_success(
        self,
        session_id: str,
        booking_id: int,
        studio_owner: User
    ) -> Dict[str, any]:
        """Process successful Square payment."""
        raise NotImplementedException("Square payment gateway not yet implemented")

    async def refund_payment(
        self,
        booking: Booking,
        studio_owner: User
    ) -> Dict[str, any]:
        """Refund Square payment."""
        raise NotImplementedException("Square payment gateway not yet implemented")

    async def retrieve_account(self, user: User) -> Dict:
        """Retrieve Square account."""
        raise NotImplementedException("Square payment gateway not yet implemented")

    async def retrieve_balance(self, user: User) -> Dict:
        """Retrieve Square balance."""
        raise NotImplementedException("Square payment gateway not yet implemented")
