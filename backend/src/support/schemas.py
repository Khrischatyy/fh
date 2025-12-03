"""
Support ticket schemas for request/response validation.
Laravel-compatible Pydantic models for support system.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator

from src.support.models import TicketStatus, TicketPriority


class SupportTicketCreateRequest(BaseModel):
    """
    Schema for creating a new support ticket.
    Can be used by both authenticated and anonymous users.
    """
    name: str = Field(..., min_length=1, max_length=255, description="User's name")
    email: EmailStr = Field(..., description="Contact email")
    subject: str = Field(..., min_length=1, max_length=255, description="Ticket subject")
    message: str = Field(..., min_length=10, max_length=5000, description="Support message")

    @field_validator("subject", "name")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate fields are not just whitespace."""
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message content."""
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class SupportTicketResponse(BaseModel):
    """Schema for support ticket response."""
    id: int
    user_id: Optional[int] = None
    email: str
    name: str
    subject: str
    message: str
    status: TicketStatus
    priority: TicketPriority
    assigned_to_id: Optional[int] = None
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SupportTicketListItem(BaseModel):
    """Schema for support ticket list item (summary view)."""
    id: int
    email: str
    name: str
    subject: str
    status: TicketStatus
    priority: TicketPriority
    created_at: datetime

    class Config:
        from_attributes = True


class SupportTicketUpdateRequest(BaseModel):
    """Schema for updating a support ticket (admin only)."""
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to_id: Optional[int] = None
    admin_notes: Optional[str] = None


class LaravelSupportTicketResponse(BaseModel):
    """Laravel-style wrapper for support ticket response."""
    success: bool = True
    data: SupportTicketResponse
    message: str = "Support ticket created successfully"
    code: int = 200


class LaravelSupportTicketsResponse(BaseModel):
    """Laravel-style wrapper for multiple support tickets."""
    success: bool = True
    data: List[SupportTicketListItem]
    message: str = "Support tickets retrieved successfully"
    code: int = 200
