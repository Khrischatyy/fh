"""Booking statuses seeder."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.bookings.models import BookingStatus


async def seed_booking_statuses(session: AsyncSession):
    """Seed booking statuses reference data."""

    # Check if already seeded
    result = await session.execute(select(BookingStatus))
    if result.scalars().first():
        print("   ⏭️  Booking statuses already seeded, skipping...")
        return

    booking_statuses = [
        {"name": "pending"},
        {"name": "confirmed"},
        {"name": "cancelled"},
        {"name": "expired"},
        {"name": "completed"}
    ]

    for status_data in booking_statuses:
        status = BookingStatus(**status_data)
        session.add(status)

    await session.commit()
    print(f"   ✅ Seeded {len(booking_statuses)} booking statuses")
