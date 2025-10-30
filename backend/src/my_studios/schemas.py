"""
My Studios schemas - API contracts for my-studios endpoints.
"""
from datetime import datetime, time as time_type
from decimal import Decimal
from typing import Optional, Any
from pydantic import BaseModel, computed_field, field_serializer

from src.geographic.schemas import CityResponse


class CompanyResponse(BaseModel):
    """Company response schema for my-studios endpoints."""

    id: int
    name: str
    logo: Optional[str] = None
    slug: str
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def logo_url(self) -> Optional[str]:
        """Return the logo URL if logo exists."""
        # If logo is already a full URL, return it
        # Otherwise, construct the URL (adjust based on your file storage)
        if self.logo:
            if self.logo.startswith(('http://', 'https://')):
                return self.logo
            # Assuming logos are stored in /storage/logos/
            return f"/storage/logos/{self.logo}"
        return None

    class Config:
        from_attributes = True


class BadgeResponse(BaseModel):
    """Badge response schema."""
    id: int
    name: str
    image: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class OperatingHourResponse(BaseModel):
    """Operating hour response schema."""
    id: int
    address_id: int
    mode_id: Optional[int] = None
    day_of_week: Optional[int] = None
    open_time: Optional[Any] = None  # Accept time objects
    close_time: Optional[Any] = None  # Accept time objects
    is_closed: bool

    @field_serializer('open_time', 'close_time')
    def serialize_time(self, value: Optional[time_type]) -> Optional[str]:
        """Convert time to string format HH:MM:SS"""
        if value is None:
            return None
        if isinstance(value, time_type):
            return value.strftime('%H:%M:%S')
        return str(value)

    class Config:
        from_attributes = True


class RoomPhotoResponse(BaseModel):
    """Room photo response schema."""
    id: int
    room_id: int
    path: str
    index: int

    class Config:
        from_attributes = True


class RoomPriceResponse(BaseModel):
    """Room price response schema."""
    id: int
    room_id: int
    hours: int
    total_price: Decimal
    price_per_hour: Decimal
    is_enabled: bool

    class Config:
        from_attributes = True


class StudioResponse(BaseModel):
    """Studio/Address response schema for my-studios endpoints."""

    id: int
    slug: str
    street: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    timezone: Optional[str] = None
    rating: Optional[float] = None
    city_id: Optional[int] = None
    company_id: Optional[int] = None
    available_balance: Decimal
    created_at: datetime
    updated_at: datetime

    # Nested relationships
    city: Optional[CityResponse] = None
    company: Optional[CompanyResponse] = None
    badges: list[BadgeResponse] = []
    operating_hours: list[OperatingHourResponse] = []

    # Note: photos and prices are on Room, but frontend expects them on Address
    # We'll need to aggregate them from all rooms
    photos: list[RoomPhotoResponse] = []
    prices: list[RoomPriceResponse] = []

    class Config:
        from_attributes = True
