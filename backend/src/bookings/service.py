"""
Booking service - Business logic for booking operations.
"""
from datetime import date as date_type, time as time_type, datetime, timedelta
from typing import Optional
import pytz

from src.bookings.repository import BookingRepository
from src.bookings.schemas import TimeSlot
from src.exceptions import NotFoundException, BadRequestException


class BookingService:
    """Service for booking-related business logic."""

    def __init__(self, repository: BookingRepository):
        self._repository = repository

    async def get_available_start_times(
        self,
        room_id: int,
        booking_date: date_type
    ) -> list[TimeSlot]:
        """
        Calculate available start times for a room on a given date.

        Returns list of available time slots in 1-hour increments.
        """
        # Fetch room with address and operating hours
        room = await self._repository.get_room_with_address(room_id)
        if not room:
            raise NotFoundException(f"Room with id {room_id} not found")

        if not room.address:
            raise BadRequestException("Room has no associated address")

        # Get operating hours for this date
        operating_hours = self._get_operating_hours_for_date(
            room.address.operating_hours,
            booking_date
        )

        if not operating_hours:
            return []

        # Get timezone
        tz = pytz.timezone(room.address.timezone) if room.address.timezone else pytz.UTC
        now = datetime.now(tz)

        # Determine open and close times
        open_time = operating_hours.open_time
        close_time = operating_hours.close_time
        is_24_7 = operating_hours.mode_id == 1 if operating_hours.mode_id else False

        # If booking is for today, adjust open time to current time rounded up
        if booking_date == now.date():
            current_hour = now.hour
            current_minute = now.minute

            # Round up to next hour
            if current_minute > 0:
                current_hour += 1

            # Create time object for current hour
            current_time = time_type(hour=current_hour if current_hour < 24 else 23, minute=0)

            # Use the later of open_time or current_time
            if current_time > open_time:
                open_time = current_time

        # Get existing bookings for this date
        bookings = await self._repository.get_bookings_for_date(
            room_id,
            booking_date,
            excluded_statuses=['cancelled', 'expired']
        )

        # Calculate available start times
        available_times = self._calculate_available_start_times(
            open_time,
            close_time,
            bookings,
            booking_date,
            tz,
            is_24_7
        )

        return available_times

    async def get_available_end_times(
        self,
        room_id: int,
        booking_date: date_type,
        start_time: time_type
    ) -> list[TimeSlot]:
        """
        Calculate available end times from a given start time.

        Returns list of available end time slots starting from start_time + 1 hour.
        """
        # Fetch room with address and operating hours
        room = await self._repository.get_room_with_address(room_id)
        if not room:
            raise NotFoundException(f"Room with id {room_id} not found")

        if not room.address:
            raise BadRequestException("Room has no associated address")

        # Get operating hours for this date
        operating_hours = self._get_operating_hours_for_date(
            room.address.operating_hours,
            booking_date
        )

        if not operating_hours:
            return []

        # Validate start_time is within operating hours
        if not operating_hours.mode_id == 1:  # Not 24/7
            if start_time < operating_hours.open_time or start_time >= operating_hours.close_time:
                raise BadRequestException("Start time is outside operating hours")

        # Get timezone
        tz = pytz.timezone(room.address.timezone) if room.address.timezone else pytz.UTC

        # Get bookings from this datetime forward
        bookings = await self._repository.get_bookings_from_datetime(
            room_id,
            booking_date,
            start_time,
            excluded_statuses=['cancelled', 'expired']
        )

        # Calculate available end times
        is_24_7 = operating_hours.mode_id == 1 if operating_hours.mode_id else False
        max_hours = 72 if is_24_7 else None  # 3 days for 24/7

        available_times = self._calculate_available_end_times(
            booking_date,
            start_time,
            operating_hours.close_time if not is_24_7 else None,
            bookings,
            tz,
            max_hours
        )

        return available_times

    def _get_operating_hours_for_date(self, operating_hours_list, booking_date: date_type):
        """
        Get operating hours for a specific date.

        Handles different modes:
        - Mode 1: 24/7 (always open)
        - Mode 2: Fixed hours (same every day)
        - Mode 3: Variable hours by day of week
        """
        if not operating_hours_list:
            return None

        day_of_week = booking_date.weekday()  # Monday = 0, Sunday = 6

        # Mode 1: 24/7
        mode_1 = next((oh for oh in operating_hours_list if oh.mode_id == 1), None)
        if mode_1:
            return mode_1

        # Mode 3: Day-specific hours
        day_specific = next(
            (oh for oh in operating_hours_list if oh.mode_id == 3 and oh.day_of_week == day_of_week),
            None
        )
        if day_specific:
            if day_specific.is_closed:
                return None
            return day_specific

        # Mode 2: Fixed hours
        fixed = next((oh for oh in operating_hours_list if oh.mode_id == 2), None)
        if fixed:
            return fixed

        return None

    def _calculate_available_start_times(
        self,
        open_time: time_type,
        close_time: time_type,
        bookings: list,
        booking_date: date_type,
        tz: pytz.timezone,
        is_24_7: bool = False
    ) -> list[TimeSlot]:
        """
        Calculate available start time slots.

        Iterates through each hour from open to close, checking against existing bookings.
        """
        available_times = []

        # Create datetime for iteration
        current_dt = datetime.combine(booking_date, open_time)
        end_dt = datetime.combine(booking_date, close_time)

        # For 24/7, allow full day
        if is_24_7:
            end_dt = current_dt + timedelta(hours=24)

        while current_dt < end_dt:
            current_time = current_dt.time()

            # Check if this time slot is available
            is_available = True
            for booking in bookings:
                # Check if current time conflicts with this booking
                booking_start = booking.start_time
                booking_end = booking.end_time

                # Handle case where booking spans multiple days
                if booking.date == booking_date:
                    if booking_start <= current_time < booking_end:
                        is_available = False
                        break
                    # Also check if starting here would conflict
                    if current_time < booking_start < (datetime.combine(booking_date, current_time) + timedelta(hours=1)).time():
                        is_available = False
                        break

            if is_available:
                # Create ISO string
                dt_localized = tz.localize(datetime.combine(booking_date, current_time))
                iso_string = dt_localized.isoformat()

                available_times.append(TimeSlot(
                    time=current_time.strftime("%H:%M"),
                    iso_string=iso_string
                ))

            # Move to next hour
            current_dt += timedelta(hours=1)

        return available_times

    def _calculate_available_end_times(
        self,
        booking_date: date_type,
        start_time: time_type,
        close_time: Optional[time_type],
        bookings: list,
        tz: pytz.timezone,
        max_hours: Optional[int] = None
    ) -> list[TimeSlot]:
        """
        Calculate available end time slots from start time.

        Starts from start_time + 1 hour and goes until:
        - Close time (regular mode)
        - Max hours limit (24/7 mode)
        - Next booking conflict
        """
        available_times = []

        # Start from start_time + 1 hour
        current_dt = datetime.combine(booking_date, start_time) + timedelta(hours=1)

        # Determine end boundary
        if max_hours:
            max_dt = datetime.combine(booking_date, start_time) + timedelta(hours=max_hours)
        elif close_time:
            max_dt = datetime.combine(booking_date, close_time)
        else:
            max_dt = current_dt + timedelta(hours=24)

        while current_dt <= max_dt:
            current_date = current_dt.date()
            current_time = current_dt.time()

            # Check if this end time conflicts with any booking
            is_available = True
            for booking in bookings:
                # Check if the period from start_time to current_time overlaps with this booking
                booking_start_dt = datetime.combine(booking.date, booking.start_time)
                booking_end_date = booking.end_date if booking.end_date else booking.date
                booking_end_dt = datetime.combine(booking_end_date, booking.end_time)

                start_dt = datetime.combine(booking_date, start_time)
                end_dt = current_dt

                # Check for overlap
                if start_dt < booking_end_dt and end_dt > booking_start_dt:
                    is_available = False
                    break

            if is_available:
                # Create ISO string
                dt_localized = tz.localize(current_dt)
                iso_string = dt_localized.isoformat()

                available_times.append(TimeSlot(
                    time=current_time.strftime("%H:%M"),
                    iso_string=iso_string
                ))
            else:
                # If we hit a conflict, stop here (can't go past it)
                break

            # Move to next hour
            current_dt += timedelta(hours=1)

        return available_times
