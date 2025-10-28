"""
Address schemas - API contract definitions.
Defines request and response models for the Address domain.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class AddressBase(BaseModel):
    """Base schema with common address fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Studio name")
    description: Optional[str] = Field(None, description="Studio description")
    street: str = Field(..., min_length=1, max_length=500, description="Street address")
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, description="Latitude coordinate")
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, description="Longitude coordinate")
    timezone: Optional[str] = Field(None, max_length=100, description="Timezone (e.g., America/New_York)")
    cover_photo: Optional[str] = Field(None, max_length=500, description="Cover photo URL")


class AddressCreate(AddressBase):
    """Schema for creating a new address."""

    city_id: int = Field(..., gt=0, description="City ID where the studio is located")
    company_id: int = Field(..., gt=0, description="Company ID that owns the studio")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not just whitespace."""
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace only")
        return v.strip()

    @field_validator("street")
    @classmethod
    def validate_street(cls, v: str) -> str:
        """Ensure street is not just whitespace."""
        if not v.strip():
            raise ValueError("Street address cannot be empty or whitespace only")
        return v.strip()


class AddressUpdate(BaseModel):
    """Schema for updating an existing address."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    street: Optional[str] = Field(None, min_length=1, max_length=500)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    timezone: Optional[str] = Field(None, max_length=100)
    city_id: Optional[int] = Field(None, gt=0)
    cover_photo: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    is_published: Optional[bool] = None


class AddressResponse(AddressBase):
    """Schema for address responses."""

    id: int
    slug: str
    city_id: int
    company_id: int
    available_balance: Decimal
    is_active: bool
    is_published: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Equipment Schemas

class EquipmentTypeResponse(BaseModel):
    """Equipment type response schema."""
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EquipmentResponse(BaseModel):
    """Equipment response schema."""
    id: int
    name: str
    equipment_type_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EquipmentWithTypeResponse(EquipmentResponse):
    """Equipment with type information."""
    equipment_type: EquipmentTypeResponse

    class Config:
        from_attributes = True


class AddEquipmentRequest(BaseModel):
    """Request to add equipment to an address."""
    equipment_ids: list[int] = Field(..., min_length=1, description="List of equipment IDs to add")


# Badge Schemas

class BadgeResponse(BaseModel):
    """Badge/amenity response schema."""
    id: int
    name: str
    icon: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AddBadgeRequest(BaseModel):
    """Request to add badges to an address."""
    badge_ids: list[int] = Field(..., min_length=1, description="List of badge IDs to add")
