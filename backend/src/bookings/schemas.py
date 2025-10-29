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
