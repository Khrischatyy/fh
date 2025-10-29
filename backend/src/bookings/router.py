"""
Booking router - API endpoints for room reservations.
"""
from typing import Annotated
from datetime import date as date_type, time as time_type
from fastapi import APIRouter, Depends, Query, Body, status

from src.bookings.dependencies import get_booking_service
from src.bookings.service import BookingService
from src.bookings.schemas import (
    AvailableTimesResponse,
    CalculatePriceRequest,
    CalculatePriceResponse
)


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


@router.post(
    "/address/calculate-price",
    response_model=CalculatePriceResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate total booking price",
    description="Calculate the total price for a booking based on duration and optional engineer."
)
async def calculate_booking_price(
    request: Annotated[CalculatePriceRequest, Body()],
    service: Annotated[BookingService, Depends(get_booking_service)],
) -> CalculatePriceResponse:
    """
    Calculate total booking price based on room, time range, and optional engineer.

    **Request Body:**
    - **room_id**: ID of the room to book
    - **start_time**: Start time in ISO format (YYYY-MM-DDTHH:MM)
    - **end_time**: End time in ISO format (YYYY-MM-DDTHH:MM)
    - **engineer_id** (optional): Engineer ID to include engineer rate

    **Returns:**
    - **total_price**: Total cost for the booking
    - **explanation**: Detailed breakdown of price calculation

    **Business Rules:**
    - Calculates hours between start and end time
    - Finds applicable pricing tier based on duration
    - If no exact tier matches, uses highest tier available
    - Adds engineer hourly rate if engineer is selected
    - Price = (hours × room_rate) + (hours × engineer_rate)
    """
    result = await service.calculate_total_cost(
        start_time_str=request.start_time,
        end_time_str=request.end_time,
        room_id=request.room_id,
        engineer_id=request.engineer_id
    )

    return CalculatePriceResponse(
        total_price=result["total_price"],
        explanation=result["explanation"]
    )
