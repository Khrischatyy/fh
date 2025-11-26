"""Pydantic schemas for device management."""

from datetime import datetime as datetime_type
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, validator


class DeviceRegisterRequest(BaseModel):
    """Request schema for device registration."""

    name: str = Field(..., min_length=1, max_length=255)
    mac_address: str = Field(..., min_length=1, max_length=255)
    device_uuid: str = Field(..., min_length=1, max_length=255)
    os_version: Optional[str] = Field(None, max_length=100)
    app_version: Optional[str] = Field(None, max_length=50)
    unlock_password: Optional[str] = Field(None, min_length=6, description="Optional password to unlock device locally")


class DeviceUpdateRequest(BaseModel):
    """Request schema for updating device info."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    notes: Optional[str] = None
    unlock_password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None
    unlock_fee: Optional[Decimal] = Field(None, ge=1.00, le=1000.00, description="Unlock fee in USD")


class DeviceHeartbeatRequest(BaseModel):
    """Request schema for device heartbeat."""

    device_uuid: str
    device_token: str
    os_version: Optional[str] = None
    app_version: Optional[str] = None


class DeviceStatusResponse(BaseModel):
    """Response schema for device status check."""

    is_blocked: bool
    message: str
    should_lock: bool


class DeviceResponse(BaseModel):
    """Response schema for device info."""

    id: int
    name: str
    mac_address: str
    device_uuid: str
    is_blocked: bool
    is_active: bool
    last_heartbeat: Optional[datetime_type]
    last_ip: Optional[str]
    os_version: Optional[str]
    app_version: Optional[str]
    notes: Optional[str]
    unlock_fee: Decimal = Decimal("10.00")
    created_at: datetime_type

    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    """Response schema for device list."""

    success: bool = True
    data: list[DeviceResponse]
    message: str = "Devices retrieved successfully"
    code: int = 200


class DeviceRegisterResponse(BaseModel):
    """Response schema for device registration."""

    success: bool = True
    device_token: str
    device_uuid: str
    message: str = "Device registered successfully"
    code: int = 201


class DeviceBlockRequest(BaseModel):
    """Request schema for blocking/unblocking device."""

    device_id: int
    block: bool = True
    reason: Optional[str] = None


class DeviceUnlockRequest(BaseModel):
    """Request schema for unlocking device with password."""

    device_uuid: str
    password: str


# Payment Link Schemas
class DevicePaymentLinkRequest(BaseModel):
    """Request schema for generating a Cash App payment link."""

    device_uuid: str = Field(..., description="Device UUID")
    device_token: str = Field(..., description="Device authentication token")


class DevicePaymentLinkResponse(BaseModel):
    """Response schema for payment link generation."""

    success: bool = True
    payment_url: str = Field(..., description="Stripe Checkout URL for Cash App payment")
    session_id: str = Field(..., description="Stripe session ID")
    amount: Decimal = Field(..., description="Payment amount in USD")
    expires_in_minutes: int = Field(30, description="Minutes until link expires")
    message: str = "Payment link generated successfully"
    code: int = 200


class DeviceUnlockSessionResponse(BaseModel):
    """Response schema for unlock session info."""

    id: int
    device_id: int
    stripe_session_id: str
    amount: Decimal
    status: str
    unlock_duration_hours: int
    paid_at: Optional[datetime_type]
    expires_at: Optional[datetime_type]
    created_at: datetime_type

    class Config:
        from_attributes = True
