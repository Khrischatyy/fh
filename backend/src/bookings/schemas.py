"""
Booking schemas - Pydantic models for request/response validation.
"""
from datetime import date as date_type, time as time_type, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class AvailableStartTimeRequest(BaseModel):
    """Request schema for available start times."""
    room_id: int = Field(..., description="Room ID", gt=0)
    date: date_type = Field(..., description="Booking date in YYYY-MM-DD format")

    @field_validator('date')
    @classmethod
    def validate_date(cls, v: date_type) -> date_type:
        """Validate date is not in the past."""
        if v < datetime.now().date():
            raise ValueError("Date cannot be in the past")
        return v


class AvailableEndTimeRequest(BaseModel):
    """Request schema for available end times."""
    room_id: int = Field(..., description="Room ID", gt=0)
    date: date_type = Field(..., description="Booking date in YYYY-MM-DD format")
    start_time: time_type = Field(..., description="Start time in HH:MM format")

    @field_validator('date')
    @classmethod
    def validate_date(cls, v: date_type) -> date_type:
        """Validate date is not in the past."""
        if v < datetime.now().date():
            raise ValueError("Date cannot be in the past")
        return v


class TimeSlot(BaseModel):
    """Time slot response."""
    time: str = Field(..., description="Time in HH:MM format")
    iso_string: str = Field(..., description="ISO 8601 datetime string")


class AvailableTimesResponse(BaseModel):
    """Response schema for available time slots."""
    available_times: list[TimeSlot] = Field(default_factory=list)


class BookingCreate(BaseModel):
    """Create booking request."""
    room_id: int = Field(..., gt=0)
    date: date_type
    start_time: time_type
    end_time: time_type
    end_date: Optional[date_type] = None


class BookingResponse(BaseModel):
    """Booking response."""
    id: int
    room_id: int
    user_id: int
    status_id: int
    date: date_type
    start_time: time_type
    end_time: time_type
    end_date: Optional[date_type]
    temporary_payment_link: Optional[str]
    temporary_payment_link_expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CalculatePriceRequest(BaseModel):
    """Calculate price request."""
    room_id: int = Field(..., gt=0, description="Room ID")
    start_time: str = Field(..., description="Start time in ISO format (YYYY-MM-DDTHH:MM)")
    end_time: str = Field(..., description="End time in ISO format (YYYY-MM-DDTHH:MM)")
    engineer_id: Optional[int] = Field(None, gt=0, description="Engineer ID (optional)")


class CalculatePriceResponse(BaseModel):
    """Calculate price response."""
    total_price: float = Field(..., description="Total price for the booking")
    explanation: str = Field(..., description="Explanation of price calculation")


class CreateReservationRequest(BaseModel):
    """Create reservation request."""
    addressSlug: str = Field(..., description="Address slug for validation")
    room_id: int = Field(..., gt=0, description="Room ID")
    engineer_id: Optional[int] = Field(None, gt=0, description="Engineer ID (optional)")
    date: date_type = Field(..., description="Booking start date (YYYY-MM-DD)")
    start_time: str = Field(..., description="Start time (HH:MM)")
    end_time: str = Field(..., description="End time (HH:MM)")
    end_date: date_type = Field(..., description="Booking end date (YYYY-MM-DD)")

    @field_validator('engineer_id', mode='before')
    @classmethod
    def validate_engineer_id(cls, v):
        """Convert empty string to None."""
        if v == "" or v is None:
            return None
        return int(v)

    @field_validator('date', 'end_date')
    @classmethod
    def validate_dates(cls, v: date_type) -> date_type:
        """Validate dates are not in the past."""
        if v < datetime.now().date():
            raise ValueError("Date cannot be in the past")
        return v


class CreateReservationResponse(BaseModel):
    """Create reservation response."""
    message: str = Field(..., description="Success message")
    booking_id: int = Field(..., description="Created booking ID")
    status: str = Field(..., description="Booking status")
    payment_url: str = Field(..., description="Stripe payment URL")
    session_id: str = Field(..., description="Payment session ID")
    total_price: float = Field(..., description="Total booking price")
    expires_at: str = Field(..., description="Payment link expiration time")


# Laravel-compatible booking management schemas

class CancelBookingRequest(BaseModel):
    """Cancel booking request (Laravel-compatible)."""
    booking_id: int = Field(..., gt=0, description="Booking ID to cancel")


class FilterBookingHistoryRequest(BaseModel):
    """Filter bookings request (Laravel-compatible)."""
    status: Optional[str] = Field(None, description="Filter by status name")
    date: Optional[date_type] = Field(None, description="Filter by specific date")
    time: Optional[time_type] = Field(None, description="Filter by time (bookings active at this time)")
    search: Optional[str] = Field(None, description="Search by company name or address street")


class BookingWithRelations(BaseModel):
    """Booking with related data for list views."""
    id: int
    start_time: str  # HH:MM:SS format
    end_time: str
    date: str  # YYYY-MM-DD format
    room_id: int
    user_id: int
    status_id: int
    room: dict  # Room with address and company
    status: dict  # Status with id and name
    user: Optional[dict] = None  # User info (for studio owners)
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class PaginatedBookingsResponse(BaseModel):
    """Paginated bookings response (Laravel-compatible)."""
    current_page: int
    data: list[dict]  # Use dict to allow flexible structure
    per_page: int
    total: int
