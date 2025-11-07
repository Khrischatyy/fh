"""
Stripe payment gateway implementation.
Handles all Stripe-specific payment operations.
"""
import stripe
from typing import Dict, Optional
from decimal import Decimal
from datetime import datetime, timedelta
import logging

from src.payments.gateways.base import PaymentGateway
from src.bookings.models import Booking
from src.auth.models import User
from src.payments.models import Charge
from src.addresses.models import Address
from src.config import settings
from src.exceptions import BadRequestException, NotFoundException

logger = logging.getLogger(__name__)


class StripeGateway(PaymentGateway):
    """Stripe payment gateway implementation."""

    SERVICE_FEE_PERCENTAGE = 0.04  # 4% service fee

    def __init__(self, db_session):
        """Initialize Stripe gateway with database session."""
        self.db = db_session
        stripe.api_key = settings.stripe_api_key

    async def create_payment_session(
        self,
        booking: Booking,
        amount: Decimal,
        studio_owner: User
    ) -> Dict[str, str]:
        """
        Create a Stripe Checkout session for booking payment.

        Creates a session with:
        - Line items for the booking
        - Application fee (4% service fee)
        - Transfer to studio owner's connected account
        - Success/cancel redirect URLs
        """
        try:
            if not studio_owner.stripe_account_id:
                raise BadRequestException("Studio owner does not have a Stripe account configured.")

            # Convert amount to cents for Stripe
            amount_cents = int(amount * 100)

            # Calculate service fee
            service_fee_cents = int(amount_cents * self.SERVICE_FEE_PERCENTAGE)

            # Create checkout session
            session = stripe.checkout.Session.create(
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Studio Reservation Payment',
                            'description': f'Booking #{booking.id} - Studio Room',
                        },
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{settings.frontend_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}&booking_id={booking.id}",
                cancel_url=f"{settings.frontend_url}/cancel-booking",
                payment_intent_data={
                    'application_fee_amount': service_fee_cents,
                    'transfer_data': {
                        'destination': studio_owner.stripe_account_id,
                    },
                },
                metadata={
                    'booking_id': str(booking.id),
                    'studio_owner_id': str(studio_owner.id),
                },
                expires_at=int((datetime.now() + timedelta(minutes=settings.temporary_payment_link_expiry_minutes)).timestamp()),
            )

            # Create charge record in database
            await self._create_charge(
                booking=booking,
                session_id=session.id,
                amount=amount,
                currency='usd'
            )

            logger.info(f"Stripe checkout session created: {session.id} for booking {booking.id}")

            return {
                'session_id': session.id,
                'payment_url': session.url,
            }

        except stripe.StripeError as e:
            logger.error(f"Stripe error creating payment session: {str(e)}")
            raise BadRequestException(f"Payment session creation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating payment session: {str(e)}")
            raise BadRequestException(f"Payment session creation failed: {str(e)}")

    async def verify_payment_session(
        self,
        session_id: str,
        studio_owner: User
    ) -> Optional[Dict]:
        """Verify and retrieve Stripe checkout session."""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            logger.info(f"Stripe session retrieved: {session_id}")
            return session
        except stripe.StripeError as e:
            logger.error(f"Stripe error verifying session: {str(e)}")
            return None

    async def process_payment_success(
        self,
        session_id: str,
        booking_id: int,
        studio_owner: User
    ) -> Dict[str, any]:
        """
        Process successful payment.

        Steps:
        1. Verify the session
        2. Validate payment status
        3. Update booking status to confirmed
        4. Update charge with payment intent
        5. Update studio balance
        6. Send confirmation emails (via Celery task)
        """
        # Verify session
        session = await self.verify_payment_session(session_id, studio_owner)

        if not session:
            logger.error('Payment verification failed: Session is null.')
            return {
                'success': False,
                'code': 400,
                'error': 'Payment verification failed.',
            }

        # Validate session
        validation = self._validate_session(session)
        if not validation['success']:
            return validation

        # Get booking
        from src.bookings.repository import BookingRepository
        booking_repo = BookingRepository(self.db)
        booking = await booking_repo.get_booking_by_id(booking_id)

        if not booking:
            return {
                'success': False,
                'code': 404,
                'error': 'Booking not found.',
            }

        # Update booking status to confirmed (status_id=2)
        await booking_repo.update_booking(booking, {'status_id': 2})

        # Update charge with payment intent
        await self._update_charge(session_id, session.payment_intent)

        # Calculate amounts
        total_amount_cents = session.amount_total
        service_fee_cents = int(total_amount_cents * self.SERVICE_FEE_PERCENTAGE)
        amount_to_studio_cents = total_amount_cents - service_fee_cents

        # Update studio balance
        await self._update_balance(
            booking.room.address_id,
            Decimal(amount_to_studio_cents) / 100  # Convert cents to dollars
        )

        # TODO: Send confirmation emails via Celery
        # dispatch(BookingConfirmationJob(booking, user_email, total_amount))
        # dispatch(BookingConfirmationOwnerJob(booking, studio_owner, total_amount))

        logger.info(f"Payment processed successfully for booking {booking_id}")

        return {
            'success': True,
            'code': 200,
            'message': 'Payment successful and booking confirmed.',
        }

    async def refund_payment(
        self,
        booking: Booking,
        studio_owner: User
    ) -> Dict[str, any]:
        """
        Refund a payment for a booking.

        Steps:
        1. Find the charge
        2. Create refund via Stripe API
        3. Update charge with refund info
        4. Update studio balance (subtract amount)
        5. Update booking status to cancelled
        """
        try:
            # Get charge
            from sqlalchemy import select
            from src.payments.models import Charge

            stmt = select(Charge).where(Charge.booking_id == booking.id)
            result = await self.db.execute(stmt)
            charge = result.scalar_one_or_none()

            if not charge or not charge.stripe_payment_intent:
                raise NotFoundException("Charge not found or payment intent missing")

            # Create refund
            refund = stripe.Refund.create(
                payment_intent=charge.stripe_payment_intent
            )

            # Update charge
            charge.refund_id = refund.id
            charge.refund_status = refund.status
            await self.db.flush()

            # Update studio balance (subtract)
            await self._update_balance(
                booking.room.address_id,
                -charge.amount
            )

            # Update booking status to cancelled (status_id=3)
            from src.bookings.repository import BookingRepository
            booking_repo = BookingRepository(self.db)
            await booking_repo.update_booking(booking, {'status_id': 3})

            logger.info(f"Refund processed for booking {booking.id}")

            return {
                'success': True,
                'code': 200,
                'message': 'Refund processed successfully.',
            }

        except stripe.StripeError as e:
            logger.error(f"Stripe refund error: {str(e)}")
            return {
                'success': False,
                'code': 500,
                'error': f'Failed to process refund: {str(e)}',
            }

    async def retrieve_account(self, user: User) -> Dict:
        """Retrieve Stripe account information."""
        try:
            if not user.stripe_account_id:
                raise NotFoundException('Stripe account not found.')

            account = stripe.Account.retrieve(user.stripe_account_id)
            return account

        except stripe.StripeError as e:
            logger.error(f"Error retrieving Stripe account: {str(e)}")
            raise BadRequestException(f"Failed to retrieve Stripe account: {str(e)}")

    async def retrieve_balance(self, user: User) -> Dict:
        """Retrieve Stripe account balance."""
        try:
            if not user.stripe_account_id:
                raise NotFoundException('Stripe account ID not found.')

            balance = stripe.Balance.retrieve(
                stripe_account=user.stripe_account_id
            )
            return balance

        except stripe.StripeError as e:
            logger.error(f"Error retrieving balance: {str(e)}")
            raise BadRequestException(f"Failed to retrieve balance: {str(e)}")

    async def create_account(self, user: User) -> Dict[str, str]:
        """
        Create a Stripe Connect Express account for studio owner.

        Returns account onboarding link.
        """
        try:
            # Create account if doesn't exist
            if not user.stripe_account_id:
                account = stripe.Account.create(
                    type='express',
                    country='US',
                    email=user.email,
                    capabilities={
                        'card_payments': {'requested': True},
                        'transfers': {'requested': True},
                    },
                    business_type='individual',
                )

                user.stripe_account_id = account.id
                user.payment_gateway = 'stripe'
                await self.db.flush()

            # Create account link
            account_link = await self._create_account_link(user.stripe_account_id)

            return {
                'url': account_link.url,
            }

        except stripe.StripeError as e:
            logger.error(f"Error creating Stripe account: {str(e)}")
            raise BadRequestException(f"Failed to create Stripe account: {str(e)}")

    async def refresh_account_link(self, user: User) -> Dict[str, str]:
        """Refresh Stripe account onboarding link."""
        try:
            if not user.stripe_account_id:
                raise NotFoundException('No Stripe account found.')

            account_link = await self._create_account_link(user.stripe_account_id)

            return {
                'url': account_link.url,
            }

        except stripe.StripeError as e:
            logger.error(f"Error refreshing account link: {str(e)}")
            raise BadRequestException(f"Failed to refresh account link: {str(e)}")

    async def _create_account_link(self, stripe_account_id: str):
        """Create Stripe AccountLink for onboarding."""
        # Use HTTPS for live mode
        base_url = settings.frontend_url

        return stripe.AccountLink.create(
            account=stripe_account_id,
            refresh_url=f"{base_url}/stripe/refresh",
            return_url=f"{base_url}/stripe/complete",
            type='account_onboarding',
        )

    async def _create_charge(
        self,
        booking: Booking,
        session_id: str,
        amount: Decimal,
        currency: str
    ) -> None:
        """Create charge record in database."""
        charge = Charge(
            booking_id=booking.id,
            stripe_session_id=session_id,
            amount=amount,
            currency=currency,
            status='pending',
        )
        self.db.add(charge)
        await self.db.flush()

    def _validate_session(self, session) -> Dict[str, any]:
        """Validate Stripe session."""
        if session.expires_at < int(datetime.now().timestamp()):
            logger.error('Payment session has expired.')
            return {
                'success': False,
                'code': 400,
                'error': 'Payment session has expired.',
            }

        if session.payment_status != 'paid':
            logger.error('Payment not completed.')
            return {
                'success': False,
                'code': 400,
                'error': 'Payment not completed.',
            }

        return {'success': True}

    async def _update_charge(self, session_id: str, payment_intent: str) -> None:
        """Update charge with payment intent."""
        from sqlalchemy import select, update
        from src.payments.models import Charge

        stmt = (
            update(Charge)
            .where(Charge.stripe_session_id == session_id)
            .values(
                stripe_payment_intent=payment_intent,
                status='succeeded'
            )
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def _update_balance(self, address_id: int, amount: Decimal) -> None:
        """Update studio address balance."""
        from sqlalchemy import select

        stmt = select(Address).where(Address.id == address_id)
        result = await self.db.execute(stmt)
        address = result.scalar_one_or_none()

        if address:
            # Initialize available_balance if None
            if address.available_balance is None:
                address.available_balance = Decimal('0')

            address.available_balance += amount
            await self.db.flush()
