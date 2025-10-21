"""
Room schemas - API contracts for rooms, pricing, and photos.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# Room Schemas

class RoomBase(BaseModel):
    """Base room schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class RoomCreate(RoomBase):
    """Schema for creating a room."""
    address_id: int = Field(..., gt=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Room name cannot be empty")
        return v.strip()


class RoomUpdate(BaseModel):
    """Schema for updating a room."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Room name cannot be empty")
        return v.strip() if v else None


class RoomResponse(RoomBase):
    """Room response schema."""
    id: int
    address_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoomWithRelationsResponse(RoomResponse):
    """Room response with nested photos and prices."""
    photos: list["RoomPhotoResponse"] = Field(default_factory=list)
    prices: list["RoomPriceResponse"] = Field(default_factory=list)

    class Config:
        from_attributes = True


# Room Price Schemas

class RoomPriceBase(BaseModel):
    """Base room price schema."""
    hours: int = Field(..., gt=0, description="Duration in hours")
    total_price: Decimal = Field(..., gt=0, decimal_places=2)
    is_enabled: bool = Field(default=True)


class RoomPriceCreate(RoomPriceBase):
    """Schema for creating a room price."""
    pass


class RoomPriceUpdate(BaseModel):
    """Schema for updating a room price."""
    hours: Optional[int] = Field(None, gt=0)
    total_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    is_enabled: Optional[bool] = None


class RoomPriceResponse(RoomPriceBase):
    """Room price response schema."""
    id: int
    room_id: int
    price_per_hour: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Room Photo Schemas

class RoomPhotoBase(BaseModel):
    """Base room photo schema."""
    photo_path: str = Field(..., min_length=1, max_length=500)
    index: int = Field(default=0, ge=0, description="Photo order index")


class RoomPhotoCreate(BaseModel):
    """Schema for creating a room photo."""
    photo_path: str = Field(..., min_length=1, max_length=500)
    index: Optional[int] = Field(None, ge=0)


class RoomPhotoUpdate(BaseModel):
    """Schema for updating a room photo."""
    index: int = Field(..., ge=0, description="New photo order index")


class RoomPhotoResponse(RoomPhotoBase):
    """Room photo response schema."""
    id: int
    room_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
