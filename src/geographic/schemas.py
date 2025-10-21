"""
Geographic schemas - API contracts.
"""
from datetime import datetime
from pydantic import BaseModel, Field


class CountryBase(BaseModel):
    """Base country schema."""
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=2, max_length=10)


class CountryResponse(CountryBase):
    """Country response schema."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CityBase(BaseModel):
    """Base city schema."""
    name: str = Field(..., min_length=1, max_length=255)
    country_id: int = Field(..., gt=0)


class CityResponse(CityBase):
    """City response schema."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
