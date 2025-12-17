"""Pydantic schemas for device management."""

from datetime import datetime as datetime_type
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
    current_password: Optional[str] = Field(None, min_length=6, max_length=255, description="Current macOS password for device")
    is_active: Optional[bool] = None


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
    lockout_info: Optional[dict] = Field(None, description="Lockout screen info (studio name, payment URL, etc.)")


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
    current_password: Optional[str]
    password_changed_at: Optional[datetime_type]
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


class StorePasswordRequest(BaseModel):
    """Request schema for storing device password."""

    device_uuid: str = Field(..., description="Device UUID")
    device_token: str = Field(..., description="Device authentication token")
    password: str = Field(..., min_length=1, description="Current macOS user password (will be encrypted)")


class DevicePasswordResponse(BaseModel):
    """Response schema for device password retrieval."""

    password: str = Field(..., description="Current macOS user password (decrypted)")
    password_changed_at: Optional[datetime_type] = Field(None, description="When password was last changed")
    device_name: str = Field(..., description="Device name for reference")

    class Config:
        from_attributes = True


class CreateDevicePaymentSessionRequest(BaseModel):
    """Request schema for creating device payment session."""

    device_uuid: str = Field(..., description="Device UUID")
    unlock_duration_hours: int = Field(..., ge=1, le=168, description="Number of hours to unlock device (1-168)")


class CreateDevicePaymentSessionResponse(BaseModel):
    """Response schema for device payment session creation."""

    success: bool = True
    session_id: str = Field(..., description="Stripe checkout session ID")
    payment_url: str = Field(..., description="Stripe checkout URL")
    amount: float = Field(..., description="Payment amount")
    currency: str = Field(default="USD", description="Payment currency")
    message: str = "Payment session created successfully"
    code: int = 200


class DevicePaymentSuccessResponse(BaseModel):
    """Response schema for device payment success."""

    success: bool
    message: str
    unlock_session_id: int
    expires_at: datetime_type
    code: int = 200
