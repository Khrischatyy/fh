"""
Company schemas - API contracts for companies.
"""
from datetime import datetime
from typing import Optional
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


class CompanyWithAddressesResponse(CompanyResponse):
    """Company response with nested addresses."""
    addresses: list = Field(default_factory=list)

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
