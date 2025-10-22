"""
Authentication Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    firstname: str = Field(..., min_length=1, max_length=100)
    lastname: str = Field(..., min_length=1, max_length=100)
    username: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)


class UserRegister(BaseModel):
    """Schema for user registration - Laravel compatible."""
    name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    email: EmailStr = Field(..., max_length=255, description="User's email address")
    password: str = Field(..., min_length=8, max_length=100, description="User's password")
    password_confirmation: str = Field(..., min_length=8, max_length=100, description="Password confirmation")
    role: str = Field(..., max_length=15, pattern="^(user|studio_owner|admin)$", description="User role")

    @field_validator("password_confirmation")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("The password confirmation does not match.")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class RegisterResponse(BaseModel):
    """Schema for registration response - Laravel compatible."""
    message: str
    token: str
    role: str


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    email: str
    firstname: str
    lastname: str
    username: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    profile_photo: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    email_verified_at: Optional[datetime] = None
    payment_gateway: Optional[str] = None
    stripe_account_id: Optional[str] = None
    stripe_onboarding_complete: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    firstname: Optional[str] = Field(None, min_length=1, max_length=100)
    lastname: Optional[str] = Field(None, min_length=1, max_length=100)
    username: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[datetime] = None
    bio: Optional[str] = Field(None, max_length=1000)


class SetRoleRequest(BaseModel):
    """Schema for setting user role."""
    role: str = Field(..., pattern="^(user|studio_owner|admin)$")


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordReset(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    password: str = Field(..., min_length=8, max_length=100)
    password_confirmation: str = Field(..., min_length=8, max_length=100)

    @field_validator("password_confirmation")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class EmailVerificationRequest(BaseModel):
    """Schema for email verification."""
    token: str


class GoogleAuthResponse(BaseModel):
    """Schema for Google OAuth response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
