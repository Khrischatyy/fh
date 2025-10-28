"""
Pydantic schemas for FastAPI Users.
"""
from datetime import datetime
from typing import Optional
from fastapi_users import schemas
from pydantic import EmailStr, Field


class UserRead(schemas.BaseUser[int]):
    """Schema for reading user data."""
    id: int
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    # Additional fields
    google_id: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    profile_photo: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    stripe_account_id: Optional[str] = None
    payment_gateway: Optional[str] = None
    stripe_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a user."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    firstname: str = Field(..., min_length=1, max_length=100)
    lastname: str = Field(..., min_length=1, max_length=100)
    username: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating a user."""
    password: Optional[str] = Field(None, min_length=8, max_length=72)
    email: Optional[EmailStr] = None
    firstname: Optional[str] = Field(None, min_length=1, max_length=100)
    lastname: Optional[str] = Field(None, min_length=1, max_length=100)
    username: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    profile_photo: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
