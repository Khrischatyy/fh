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
    StorePasswordRequest,
    DevicePasswordResponse,
    CreateDevicePaymentSessionRequest,
    CreateDevicePaymentSessionResponse,
    DevicePaymentSuccessResponse,
)
from src.auth.schemas import DeviceRegisterWithTokenRequest
from src.auth.service import auth_service
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


@router.post("/register-with-token", response_model=DeviceRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_device_with_token(
    device_data: DeviceRegisterWithTokenRequest,
    request: Request,
    service: DeviceService = Depends(get_device_service),
    db: AsyncSession = Depends(get_db),
):
    """
    Register a device using a registration token from web app.

    This is the NEW simplified flow:
    1. User logs into web app
    2. Web app shows a registration token
    3. User copies token and pastes it into locker app
    4. Locker app calls this endpoint with the token

    No email/password needed in the locker app!
    """
    # Validate the registration token
    registration_token = await auth_service.validate_device_registration_token(
        db,
        device_data.registration_token
    )

    # Register the device
    ip_address = get_client_ip(request)

    # Create device data for registration
    device_request = DeviceRegisterRequest(
        name=device_data.device_name or "Mac Device",
        mac_address=device_data.mac_address or "unknown",
        device_uuid=device_data.device_uuid,
        os_version=device_data.os_version,
        app_version=device_data.app_version,
        unlock_password=device_data.unlock_password
    )

    device, device_token = await service.register_device(
        registration_token.user_id,
        device_request,
        ip_address
    )

    # Mark token as used
    await auth_service.mark_token_as_used(db, registration_token, device_data.device_name)

    return DeviceRegisterResponse(
        device_token=device_token,
        device_uuid=device.device_uuid,
        message="Device registered successfully. Save this token securely!",
    )


@router.post("/register-from-app", response_model=DeviceRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_device_from_app(
    device_data: DeviceRegisterRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    LEGACY: Auto-register a device when user signs in via Mac OS app with email/password.

    This is the old flow that requires email/password in the locker app.
    Consider using /register-with-token instead for better security.
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


@router.post("/store-password", response_model=dict, status_code=status.HTTP_200_OK)
async def store_device_password(
    password_data: StorePasswordRequest,
    service: DeviceService = Depends(get_device_service),
):
    """
    Store device password (called by locker app after changing macOS password).

    This endpoint stores the encrypted macOS user password in the backend
    so studio owners can access it if needed. Uses device token for authentication.
    """
    success = await service.store_device_password(password_data)

    return {
        "success": success,
        "message": "Password stored successfully",
        "code": 200
    }


@router.get("/{device_id}/password", response_model=DevicePasswordResponse)
async def get_device_password(
    device_id: int,
    current_user: User = Depends(get_current_user),
    service: DeviceService = Depends(get_device_service),
):
    """
    Get device password (studio owner only).

    Returns the decrypted macOS user password for the device.
    Only the device owner can access this endpoint.
    """
    password_response = await service.get_device_password(device_id, current_user.id)
    return password_response


@router.post("/get-password", response_model=DevicePasswordResponse)
async def get_device_password_by_token(
    request: DeviceHeartbeatRequest,
    service: DeviceService = Depends(get_device_service),
):
    """
    Get device password using device token (device-to-backend authentication).

    This endpoint allows the locker app to fetch its current password from the backend
    so it can sync the macOS user password with the admin panel setting.

    Authentication: Uses device_uuid and device_token (not user JWT).
    """
    password_response = await service.get_device_password_by_token(
        request.device_uuid,
        request.device_token
    )
    return password_response


@router.post("/create-payment-session", response_model=CreateDevicePaymentSessionResponse)
async def create_device_payment_session(
    request: CreateDevicePaymentSessionRequest,
    service: DeviceService = Depends(get_device_service),
    db: AsyncSession = Depends(get_db),
):
    """
    Create Stripe checkout session for device unlock payment.

    This endpoint creates a payment session for temporarily unlocking a device.
    Users can pay to unlock the device for a specified number of hours.

    **Request Body:**
    - **device_uuid**: Device UUID
    - **unlock_duration_hours**: Number of hours to unlock (1-168)

    **Returns:**
    - **session_id**: Stripe checkout session ID
    - **payment_url**: URL to Stripe checkout page
    - **amount**: Payment amount in USD
    """
    try:
        result = await service.create_device_payment_session(
            device_uuid=request.device_uuid,
            unlock_duration_hours=request.unlock_duration_hours
        )

        await db.commit()

        return CreateDevicePaymentSessionResponse(
            session_id=result['session_id'],
            payment_url=result['payment_url'],
            amount=result['amount'],
            currency=result['currency']
        )

    except Exception as e:
        await db.rollback()
        raise


@router.get("/payment-success", response_model=DevicePaymentSuccessResponse)
async def device_payment_success(
    session_id: str,
    device_uuid: str,
    service: DeviceService = Depends(get_device_service),
    db: AsyncSession = Depends(get_db),
):
    """
    Process successful device payment.

    Called by frontend after successful Stripe checkout.
    Updates unlock session status and sets expiration time.

    **Query Parameters:**
    - **session_id**: Stripe checkout session ID
    - **device_uuid**: Device UUID

    **Returns:**
    - **success**: Payment processing status
    - **message**: Status message
    - **unlock_session_id**: Unlock session ID
    - **expires_at**: Device unlock expiration time
    """
    try:
        result = await service.process_device_payment_success(
            session_id=session_id,
            device_uuid=device_uuid
        )

        await db.commit()

        return DevicePaymentSuccessResponse(
            success=result['success'],
            message=result['message'],
            unlock_session_id=result['unlock_session_id'],
            expires_at=result['expires_at'],
            device_name=result.get('device_name'),
            device_password=result.get('device_password')
        )

    except Exception as e:
        await db.rollback()
        raise
