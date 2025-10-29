"""
Booking repository - Database access layer for bookings.
"""
from datetime import date as date_type, time as time_type
from typing import Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.bookings.models import Booking, BookingStatus
from src.rooms.models import Room
from src.addresses.models import Address, OperatingHour


class BookingRepository:
    """Repository for booking database operations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_room_with_address(self, room_id: int) -> Optional[Room]:
        """Get room with address and operating hours."""
        stmt = (
            select(Room)
            .where(Room.id == room_id)
            .options(
                selectinload(Room.address).selectinload(Address.operating_hours),
                selectinload(Room.prices),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_bookings_for_date(
        self,
        room_id: int,
        booking_date: date_type,
        excluded_statuses: Optional[list[str]] = None
    ) -> list[Booking]:
        """
        Get all bookings for a room on a specific date.

        Args:
            room_id: Room ID
            booking_date: Date to check
            excluded_statuses: List of status names to exclude (e.g., ['cancelled', 'expired'])
        """
        if excluded_statuses is None:
            excluded_statuses = ['cancelled', 'expired']

        # Subquery to get status IDs to exclude
        status_stmt = select(BookingStatus.id).where(
            BookingStatus.name.in_(excluded_statuses)
        )
        status_result = await self._session.execute(status_stmt)
        excluded_status_ids = [row[0] for row in status_result.fetchall()]

        # Main query for bookings
        stmt = (
            select(Booking)
            .where(
                and_(
                    Booking.room_id == room_id,
                    or_(
                        Booking.date == booking_date,
                        and_(
                            Booking.date <= booking_date,
                            Booking.end_date >= booking_date
                        )
                    ),
                    ~Booking.status_id.in_(excluded_status_ids) if excluded_status_ids else True
                )
            )
            .order_by(Booking.start_time)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_bookings_from_datetime(
        self,
        room_id: int,
        booking_date: date_type,
        start_time: time_type,
        excluded_statuses: Optional[list[str]] = None
    ) -> list[Booking]:
        """
        Get all bookings for a room from a specific date/time forward.

        Useful for finding available end times - checks bookings that start
        on or after the given date/time.
        """
        if excluded_statuses is None:
            excluded_statuses = ['cancelled', 'expired']

        # Subquery to get status IDs to exclude
        status_stmt = select(BookingStatus.id).where(
            BookingStatus.name.in_(excluded_statuses)
        )
        status_result = await self._session.execute(status_stmt)
        excluded_status_ids = [row[0] for row in status_result.fetchall()]

        # Get bookings on or after this date/time
        stmt = (
            select(Booking)
            .where(
                and_(
                    Booking.room_id == room_id,
                    or_(
                        Booking.date > booking_date,
                        and_(
                            Booking.date == booking_date,
                            Booking.start_time >= start_time
                        )
                    ),
                    ~Booking.status_id.in_(excluded_status_ids) if excluded_status_ids else True
                )
            )
            .order_by(Booking.date, Booking.start_time)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_booking(self, booking_data: dict) -> Booking:
        """Create a new booking."""
        booking = Booking(**booking_data)
        self._session.add(booking)
        await self._session.flush()
        await self._session.refresh(booking)
        return booking

    async def get_booking_by_id(self, booking_id: int) -> Optional[Booking]:
        """Get booking by ID."""
        stmt = select(Booking).where(Booking.id == booking_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_booking(self, booking: Booking, update_data: dict) -> Booking:
        """Update existing booking."""
        for key, value in update_data.items():
            setattr(booking, key, value)
        await self._session.flush()
        await self._session.refresh(booking)
        return booking

    async def delete_booking(self, booking: Booking) -> None:
        """Delete a booking."""
        await self._session.delete(booking)
        await self._session.flush()
