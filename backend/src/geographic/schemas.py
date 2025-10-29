"""
Geographic schemas - API contracts.
"""
from datetime import datetime
from typing import Generic, TypeVar
from pydantic import BaseModel, Field


class CountryBase(BaseModel):
    """Base country schema."""
    name: str = Field(..., min_length=1, max_length=255)


class CountryResponse(CountryBase):
    """Country response schema matching Laravel format."""
    id: int

    class Config:
        from_attributes = True


class CityBase(BaseModel):
    """Base city schema."""
    name: str = Field(..., min_length=1, max_length=255)
    country_id: int = Field(..., gt=0)


class CityResponse(CityBase):
    """City response schema matching Laravel format."""
    id: int

    class Config:
        from_attributes = True


# Laravel-style response wrapper
T = TypeVar('T')


class LaravelResponse(BaseModel, Generic[T]):
    """Laravel-style API response wrapper."""
    success: bool = True
    data: T
    message: str
    code: int = 200
