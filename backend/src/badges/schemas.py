"""Badge Pydantic schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class BadgeBase(BaseModel):
    """Base badge schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class BadgeCreate(BadgeBase):
    """Schema for creating a badge."""

    image: str = Field(..., min_length=1, max_length=500)


class BadgeUpdate(BaseModel):
    """Schema for updating a badge."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    image: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None


class BadgeResponse(BadgeBase):
    """Badge response schema."""

    id: int
    image: str
    image_url: str  # Computed full URL for frontend

    class Config:
        from_attributes = True


class BadgeListResponse(BaseModel):
    """Response schema for badge list."""

    badges: list[BadgeResponse]
    total: int
