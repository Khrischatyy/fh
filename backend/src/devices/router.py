"""Router for device management endpoints."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.devices.repository import DeviceRepository
from src.devices.service import DeviceService
from src.devices.schemas import (
    DeviceRegisterRequest,
    DeviceRegisterResponse,
    DeviceListResponse,
    DeviceResponse,
    DeviceUpdateRequest,
    DeviceBlockRequest,
    DeviceStatusResponse,
    DeviceHeartbeatRequest,
    DeviceUnlockRequest,
)
from src.exceptions import BadRequestException

router = APIRouter(prefix="/devices", tags=["devices"])


def get_device_service(db: AsyncSession = Depends(get_db)) -> DeviceService:
    """Dependency to get device service."""
    repository = DeviceRepository(db)
    return DeviceService(repository)


def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/register-from-app", response_model=DeviceRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_device_from_app(
    device_data: DeviceRegisterRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    Auto-register a device when user signs in via Mac OS app.

    This endpoint is called by the Mac OS app during first-time authentication.
    The app collects device info automatically and registers it.
    """
    ip_address = get_client_ip(request)
    device, device_token = await service.register_device(current_user.id, device_data, ip_address)

    return DeviceRegisterResponse(
        device_token=device_token,
        device_uuid=device.device_uuid,
        message="Device registered successfully. Save this token securely!",
    )


@router.get("", response_model=DeviceListResponse)
async def list_devices(
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    List all devices for the current user.

    Returns all devices registered by the studio owner.
    """
    devices = await service.get_user_devices(current_user.id)

    return DeviceListResponse(
        data=[DeviceResponse.model_validate(device) for device in devices]
    )


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """Get a specific device by ID."""
    device = await service.get_device(device_id, current_user.id)
    return DeviceResponse.model_validate(device)


@router.patch("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: int,
    update_data: DeviceUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """Update device information."""
    device = await service.update_device(device_id, current_user.id, update_data)
    return DeviceResponse.model_validate(device)


@router.post("/block", response_model=DeviceResponse)
async def block_device(
    block_data: DeviceBlockRequest,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    Block or unblock a device.

    When blocked, the device will lock its screen on the next status check.
    """
    device = await service.block_device(
        block_data.device_id,
        current_user.id,
        block_data.block,
        block_data.reason
    )
    return DeviceResponse.model_validate(device)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """Delete a device."""
    await service.delete_device(device_id, current_user.id)
    return None


# Public endpoint for device status checks (no user auth, uses device token)
@router.post("/check-status", response_model=DeviceStatusResponse)
async def check_device_status(
    heartbeat_data: DeviceHeartbeatRequest,
    request: Request,
    service: DeviceService = Depends(get_device_service),
):
    """
    Check if device should be blocked (called by Mac OS script).

    This endpoint is called periodically by the Mac OS monitoring script.
    It uses device_uuid and device_token for authentication instead of user JWT.
    """
    ip_address = get_client_ip(request)

    status_response = await service.check_device_status(
        heartbeat_data.device_uuid,
        heartbeat_data.device_token,
        ip_address
    )

    return status_response


@router.post("/unlock", response_model=dict)
async def unlock_device_with_password(
    unlock_data: DeviceUnlockRequest,
    service: DeviceService = Depends(get_device_service),
):
    """
    Unlock a device using local password.

    This endpoint allows unlocking a blocked device using the password
    set during registration, without admin panel access.
    """
    success = await service.unlock_device_with_password(
        unlock_data.device_uuid,
        unlock_data.password
    )

    return {
        "success": True,
        "message": "Device unlocked successfully",
        "code": 200
    }
