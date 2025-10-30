"""
Company schemas - API contracts for companies.
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class CompanyBase(BaseModel):
    """Base company schema."""
    name: str = Field(..., min_length=1, max_length=255)
    logo: Optional[str] = Field(None, max_length=500)


class CompanyCreate(CompanyBase):
    """Schema for creating a company."""

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Company name cannot be empty")
        return v.strip()


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    logo: Optional[str] = Field(None, max_length=500)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Company name cannot be empty")
        return v.strip() if v else None


class CompanyResponse(CompanyBase):
    """Company response schema."""
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SimpleAddressResponse(BaseModel):
    """Simplified address response for company endpoint."""
    id: int
    slug: str
    street: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    timezone: Optional[str] = None
    city_id: Optional[int] = None
    available_balance: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyWithAddressesResponse(CompanyResponse):
    """Company response with nested addresses."""
    addresses: list[SimpleAddressResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class AdminCompanyCreate(BaseModel):
    """Schema for adding a user as company admin."""
    user_id: int = Field(..., gt=0)
    company_id: int = Field(..., gt=0)


class AdminCompanyResponse(BaseModel):
    """Admin company relationship response."""
    id: int
    user_id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BrandCreateRequest(BaseModel):
    """
    Brand creation request - creates company + address + default room + default operating hours.
    Matches Laravel's BrandRequest.
    """
    company: str = Field(..., min_length=1, max_length=255, description="Company name (unique)")
    street: str = Field(..., min_length=1, description="Street address")
    city: str = Field(..., min_length=1, description="City name")
    country: str = Field(..., min_length=1, description="Country name")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    zip: str = Field(..., min_length=1, max_length=10, description="ZIP/Postal code")
    timezone: str = Field("UTC", description="Timezone (e.g., America/Los_Angeles)")
    address: Optional[str] = Field(None, description="Full address (optional)")
    about: Optional[str] = Field(None, description="About the studio (optional)")

    @field_validator("company")
    @classmethod
    def validate_company_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Company name cannot be empty")
        return v.strip()


class BrandCreateResponse(BaseModel):
    """Brand creation response."""
    slug: str = Field(..., description="Company slug")
    address_id: int = Field(..., description="Created address ID")
    room_id: int = Field(..., description="Created room ID")
    message: str = Field(default="Company and address added", description="Success message")
