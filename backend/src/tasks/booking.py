"""
Booking tasks for Celery.
Handles periodic booking management operations.
"""
from celery import shared_task
from datetime import datetime
import logging
import pytz

from src.database import AsyncSessionLocal
from src.bookings.repository import BookingRepository
from src.tasks.email import send_booking_expired_notification

# Import all models at module level to ensure they're registered before queries
# This prevents SQLAlchemy circular dependency errors
from src.bookings.models import Booking, BookingStatus  # noqa: F401
from src.auth.models import User  # noqa: F401
from src.payments.models import Charge  # noqa: F401
from src.devices.models import Device  # noqa: F401
from src.rooms.models import Room, RoomPrice, RoomPhoto  # noqa: F401
from src.addresses.models import Address, OperatingHour, Badge  # noqa: F401
from src.companies.models import Company, AdminCompany  # noqa: F401
from src.geographic.models import City, Country  # noqa: F401
from src.messages.models import Message  # noqa: F401

# Force SQLAlchemy to configure all mappers immediately
# This resolves circular dependencies and relationship references
from sqlalchemy.orm import configure_mappers
configure_mappers()

logger = logging.getLogger(__name__)


@shared_task(name="expire_unpaid_bookings", bind=True, max_retries=3)
def expire_unpaid_bookings(self):
    """
    Periodic task to expire pending bookings with expired payment links.

    Business rules:
    - Runs every 15 minutes via Celery Beat
    - Updates bookings from status_id=1 (pending) to status_id=4 (expired)
    - Only affects bookings where temporary_payment_link_expires_at < NOW
    - Keeps payment link data for audit history (no cleanup)
    - Sends email notification to users
    - Idempotent: safe to run multiple times

    Returns:
        dict: Summary with count of expired bookings
    """
    import asyncio

    try:
        logger.info("Starting booking expiry task...")

        # Run async logic
        result = asyncio.run(expire_bookings_logic())

        logger.info(
            f"Booking expiry task completed successfully. "
            f"Expired {result['expired_count']} bookings."
        )

        return result

    except Exception as e:
        logger.error(
            f"Booking expiry task failed: {e.__class__.__name__}: {str(e)}",
            exc_info=True
        )
        # Retry with exponential backoff
        retry_countdown = 60 * (2 ** self.request.retries)  # 60s, 120s, 240s
        raise self.retry(exc=e, countdown=retry_countdown)


async def expire_bookings_logic() -> dict:
    """
    Core logic for expiring unpaid bookings.

    Returns:
        dict: Summary with expired_count and errors
    """
    from sqlalchemy import select

    expired_count = 0
    errors = []

    async with AsyncSessionLocal() as session:
        repository = BookingRepository(session)

        try:
            # Get all pending bookings with expired payment links
            expired_bookings = await repository.get_expired_pending_bookings()

            logger.info(f"Found {len(expired_bookings)} bookings to expire")

            if not expired_bookings:
                return {"expired_count": 0, "errors": []}

            # Update bookings to expired status
            booking_ids = [booking.id for booking in expired_bookings]
            await repository.bulk_update_booking_status(
                booking_ids=booking_ids,
                new_status_id=4  # expired
            )

            await session.commit()
            expired_count = len(expired_bookings)

            # Send email notifications (don't fail task if email fails)
            for booking in expired_bookings:
                try:
                    # Load user data
                    from src.auth.models import User
                    user_stmt = select(User).where(User.id == booking.user_id)
                    user_result = await session.execute(user_stmt)
                    user = user_result.scalar_one_or_none()

                    if user and user.email:
                        # Load room and address data for studio name
                        from src.rooms.models import Room
                        from src.addresses.models import Address
                        from src.companies.models import Company

                        room_stmt = (
                            select(Room)
                            .where(Room.id == booking.room_id)
                        )
                        room_result = await session.execute(room_stmt)
                        room = room_result.scalar_one_or_none()

                        studio_name = "Unknown Studio"
                        if room:
                            address_stmt = select(Address).where(Address.id == room.address_id)
                            address_result = await session.execute(address_stmt)
                            address = address_result.scalar_one_or_none()

                            if address:
                                if address.company_id:
                                    company_stmt = select(Company).where(Company.id == address.company_id)
                                    company_result = await session.execute(company_stmt)
                                    company = company_result.scalar_one_or_none()
                                    if company:
                                        studio_name = company.name
                                else:
                                    studio_name = address.street

                        booking_data = {
                            "booking_id": booking.id,
                            "studio_name": studio_name,
                            "date": booking.date.strftime("%Y-%m-%d"),
                            "start_time": booking.start_time.strftime("%H:%M"),
                            "end_time": booking.end_time.strftime("%H:%M"),
                            "user_name": user.name or user.email,
                        }

                        # Queue email notification (async task)
                        send_booking_expired_notification.delay(
                            email=user.email,
                            booking_data=booking_data
                        )

                        logger.info(
                            f"Queued expiry notification for booking {booking.id} "
                            f"to {user.email}"
                        )

                except Exception as email_error:
                    error_msg = f"Failed to send email for booking {booking.id}: {email_error}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                    # Continue processing other bookings

            return {
                "expired_count": expired_count,
                "errors": errors
            }

        except Exception as e:
            await session.rollback()
            logger.error(f"Database error during booking expiry: {e}", exc_info=True)
            raise
