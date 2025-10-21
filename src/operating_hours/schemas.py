"""
Operating Hours schemas - API contracts for operating hours and studio closures.
"""
from datetime import datetime, time, date
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from src.addresses.models import OperationMode


# Operating Hours Schemas

class OperatingHourBase(BaseModel):
    """Base operating hour schema."""
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    start_time: Optional[time] = Field(None, description="Opening time")
    end_time: Optional[time] = Field(None, description="Closing time")
    operation_mode: OperationMode = Field(default=OperationMode.OPEN)


class OperatingHourCreate(OperatingHourBase):
    """Schema for creating an operating hour."""

    @field_validator("operation_mode")
    @classmethod
    def validate_operation_mode(cls, v: OperationMode, info) -> OperationMode:
        """Validate operation mode constraints."""
        data = info.data

        # If mode is OPEN, both start_time and end_time are required
        if v == OperationMode.OPEN:
            if not data.get("start_time") or not data.get("end_time"):
                raise ValueError("start_time and end_time are required when operation_mode is 'open'")

        # If mode is CLOSED, times should be None
        if v == OperationMode.CLOSED:
            if data.get("start_time") or data.get("end_time"):
                raise ValueError("start_time and end_time must be null when operation_mode is 'closed'")

        return v


class OperatingHourUpdate(BaseModel):
    """Schema for updating an operating hour."""
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    operation_mode: Optional[OperationMode] = None


class OperatingHourResponse(OperatingHourBase):
    """Operating hour response schema."""
    id: int
    address_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BulkOperatingHoursCreate(BaseModel):
    """Schema for bulk creating operating hours for all days."""
    hours: list[OperatingHourCreate] = Field(..., min_length=1, max_length=7)

    @field_validator("hours")
    @classmethod
    def validate_unique_days(cls, v: list[OperatingHourCreate]) -> list[OperatingHourCreate]:
        """Ensure each day of week appears only once."""
        days = [hour.day_of_week for hour in v]
        if len(days) != len(set(days)):
            raise ValueError("Each day of week can only be specified once")
        return v


# Studio Closure Schemas

class StudioClosureBase(BaseModel):
    """Base studio closure schema."""
    start_date: date = Field(..., description="Closure start date")
    end_date: date = Field(..., description="Closure end date")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for closure")


class StudioClosureCreate(StudioClosureBase):
    """Schema for creating a studio closure."""

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: date, info) -> date:
        """Validate that end_date is not before start_date."""
        data = info.data
        start_date = data.get("start_date")
        if start_date and v < start_date:
            raise ValueError("end_date cannot be before start_date")
        return v


class StudioClosureUpdate(BaseModel):
    """Schema for updating a studio closure."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = Field(None, max_length=500)

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: Optional[date], info) -> Optional[date]:
        """Validate that end_date is not before start_date if both are provided."""
        if v is None:
            return v
        data = info.data
        start_date = data.get("start_date")
        if start_date and v < start_date:
            raise ValueError("end_date cannot be before start_date")
        return v


class StudioClosureResponse(StudioClosureBase):
    """Studio closure response schema."""
    id: int
    address_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
