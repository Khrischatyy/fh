"""
Booking router - API endpoints for room reservations.
"""
from typing import Annotated
from datetime import date as date_type, time as time_type
from fastapi import APIRouter, Depends, Query, status

from src.bookings.dependencies import get_booking_service
from src.bookings.service import BookingService
from src.bookings.schemas import AvailableTimesResponse


router = APIRouter(tags=["Bookings"])


@router.get(
    "/address/reservation/start-time",
    response_model=AvailableTimesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get available start times for booking",
    description="Returns available time slots for starting a booking on a specific date and room."
)
async def get_available_start_times(
    room_id: Annotated[int, Query(description="Room ID", gt=0)],
    date: Annotated[date_type, Query(description="Booking date (YYYY-MM-DD)")],
    service: Annotated[BookingService, Depends(get_booking_service)],
) -> AvailableTimesResponse:
    """
    Get available start times for a room on a specific date.

    **Query Parameters:**
    - **room_id**: ID of the room to book
    - **date**: Date for the booking (format: YYYY-MM-DD)

    **Returns:**
    - List of available time slots with:
        - time: Time in HH:MM format
        - iso_string: ISO 8601 datetime string with timezone

    **Business Rules:**
    - Only returns times within operating hours
    - Excludes time slots with existing bookings
    - If date is today, returns only future times
    - Respects studio operating mode (24/7, fixed hours, or day-specific)
    """
    available_times = await service.get_available_start_times(room_id, date)

    return AvailableTimesResponse(available_times=available_times)


@router.get(
    "/address/reservation/end-time",
    response_model=AvailableTimesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get available end times for booking",
    description="Returns available end times from a given start time."
)
async def get_available_end_times(
    room_id: Annotated[int, Query(description="Room ID", gt=0)],
    date: Annotated[date_type, Query(description="Booking date (YYYY-MM-DD)")],
    start_time: Annotated[time_type, Query(description="Start time (HH:MM)")],
    service: Annotated[BookingService, Depends(get_booking_service)],
) -> AvailableTimesResponse:
    """
    Get available end times for a booking from a given start time.

    **Query Parameters:**
    - **room_id**: ID of the room to book
    - **date**: Date for the booking (format: YYYY-MM-DD)
    - **start_time**: Start time for the booking (format: HH:MM)

    **Returns:**
    - List of available end time slots starting from start_time + 1 hour

    **Business Rules:**
    - Returns slots in 1-hour increments
    - For regular hours: limited to close time
    - For 24/7 mode: allows up to 72 hours (3 days)
    - Stops at first booking conflict
    """
    available_times = await service.get_available_end_times(
        room_id,
        date,
        start_time
    )

    return AvailableTimesResponse(available_times=available_times)
