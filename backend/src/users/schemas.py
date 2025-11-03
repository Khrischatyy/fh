"""
User-specific Pydantic schemas for request/response validation.
Laravel-compatible schemas for user management endpoints.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class UserUpdateRequest(BaseModel):
    """Schema for PUT /api/user/update - Laravel compatible."""
    firstname: Optional[str] = Field(None, max_length=255)
    lastname: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[datetime] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format (Laravel regex: ^\+?[1-9]\d{1,14}$)."""
        if v is None:
            return v
        if not re.match(r"^\+?[1-9]\d{1,14}$", v):
            raise ValueError("The phone must be a valid phone number.")
        return v


class PhotoUploadResponse(BaseModel):
    """Schema for photo upload response."""
    photo_url: str


class RoleRequest(BaseModel):
    """Schema for POST /api/user/set-role - Laravel compatible."""
    role: str = Field(..., pattern="^(user|studio_owner)$", description="User role (user or studio_owner only)")
