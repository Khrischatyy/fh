"""
SMS Authentication Schemas.
Pydantic models for SMS-based authentication requests and responses.
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import phonenumbers


class SMSSendRequest(BaseModel):
    """Request to send SMS verification code."""

    phone: str = Field(..., description="Phone number in international format (e.g., +1234567890)")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate and normalize phone number."""
        try:
            # Parse and validate phone number
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            # Return in E164 format (+1234567890)
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format. Use international format: +1234567890")


class SMSSendResponse(BaseModel):
    """Response after sending SMS verification code."""

    message: str = Field(..., description="Success message")
    phone: str = Field(..., description="Phone number where code was sent")
    expires_in: int = Field(300, description="Time in seconds until code expires")


class SMSVerifyRequest(BaseModel):
    """Request to verify SMS code and authenticate."""

    phone: str = Field(..., description="Phone number in international format")
    code: str = Field(..., description="6-digit verification code", min_length=6, max_length=6)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate and normalize phone number."""
        try:
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format. Use international format: +1234567890")

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate code is numeric."""
        if not v.isdigit():
            raise ValueError("Verification code must be numeric")
        return v


class SMSVerifyResponse(BaseModel):
    """Response after successful SMS verification."""

    message: str = Field(..., description="Success message")
    token: str = Field(..., description="JWT authentication token")
    role: str = Field(..., description="User role")
    user_id: int = Field(..., description="User ID")
    is_new_user: bool = Field(False, description="Whether this is a newly registered user")


class SMSVerificationError(BaseModel):
    """Error response for SMS verification."""

    message: str = Field(..., description="Error message")
    errors: Optional[dict[str, list[str]]] = Field(None, description="Field-specific errors")
