"""
Team schemas for request/response validation.
Laravel-compatible team member management.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class AddMemberRequest(BaseModel):
    """Request for adding team member (Laravel-compatible)."""
    name: str = Field(..., max_length=255, description="Member name")
    email: EmailStr = Field(..., description="Member email (must be unique)")
    address_id: int = Field(..., gt=0, description="Studio address ID")
    role: str = Field(..., pattern="^(studio_engineer|studio_manager)$", description="Member role")
    rate_per_hour: float = Field(..., ge=0, description="Hourly rate for engineer")


class DeleteTeamMemberRequest(BaseModel):
    """Request for deleting team member (Laravel-compatible)."""
    address_id: int = Field(..., gt=0, description="Studio address ID")
    member_id: int = Field(..., gt=0, description="Team member user ID")
