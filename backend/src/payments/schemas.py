"""
Payment schemas - Pydantic models for payment requests/responses.
"""
from pydantic import BaseModel, Field
from typing import Optional


class PaymentSuccessRequest(BaseModel):
    """Payment success confirmation request."""
    session_id: str = Field(..., description="Payment session ID from Stripe")
    booking_id: int = Field(..., gt=0, description="Booking ID")


class PaymentSuccessResponse(BaseModel):
    """Payment success confirmation response."""
    success: bool = Field(..., description="Whether payment was successful")
    message: str = Field(..., description="Success/error message")
    booking_id: Optional[int] = Field(None, description="Booking ID")


class CreateAccountResponse(BaseModel):
    """Create payment account response."""
    url: str = Field(..., description="Account onboarding URL")
    message: str = Field(default="Account link created successfully", description="Success message")


class RefreshAccountLinkResponse(BaseModel):
    """Refresh account link response."""
    url: str = Field(..., description="Refreshed account onboarding URL")
    message: str = Field(default="Account link refreshed successfully", description="Success message")


class BalanceResponse(BaseModel):
    """Balance response."""
    available: list = Field(default_factory=list, description="Available balance")
    pending: list = Field(default_factory=list, description="Pending balance")
    message: str = Field(default="Balance retrieved successfully", description="Success message")
