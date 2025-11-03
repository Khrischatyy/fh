"""
SMS Authentication Router.
Handles SMS verification code sending and authentication.
"""
import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from twilio.base.exceptions import TwilioRestException

from src.database import get_db, get_redis
from src.auth import sms_schemas
from src.auth.sms_service import SMSService
from src.auth.service import AuthService
from src.config import settings
from src.exceptions import BadRequestException, UnauthorizedException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/sms", tags=["SMS Authentication"])


def get_sms_service(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> SMSService:
    """Dependency to get SMS service instance."""
    return SMSService(
        db=db,
        redis=redis,
        twilio_account_sid=settings.twilio_account_sid,
        twilio_auth_token=settings.twilio_auth_token,
        twilio_phone_number=settings.twilio_phone_number,
    )


@router.post(
    "/send",
    response_model=sms_schemas.SMSSendResponse,
    status_code=status.HTTP_200_OK,
    summary="Send SMS verification code",
    description="Send a 6-digit verification code to the provided phone number via SMS",
)
async def send_verification_code(
    request: sms_schemas.SMSSendRequest,
    sms_service: SMSService = Depends(get_sms_service),
) -> sms_schemas.SMSSendResponse:
    """
    Send SMS verification code to phone number.

    Args:
        request: Phone number in international format (e.g., +1234567890)
        sms_service: SMS service dependency

    Returns:
        Success response with phone and expiry time

    Raises:
        HTTPException 400: If SMS sending fails (invalid number, Twilio error, etc.)
        HTTPException 422: If phone number validation fails
    """
    try:
        code, expires_in = await sms_service.send_verification_code(request.phone)

        logger.info(f"Verification code sent to {request.phone}")

        return sms_schemas.SMSSendResponse(
            message="Verification code sent successfully",
            phone=request.phone,
            expires_in=expires_in,
        )

    except TwilioRestException as e:
        logger.error(f"Twilio error sending SMS to {request.phone}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Failed to send SMS: {e.msg}",
                "errors": {"phone": [f"Failed to send SMS: {e.msg}"]},
            },
        )
    except Exception as e:
        logger.error(f"Unexpected error sending SMS to {request.phone}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to send verification code",
                "errors": {"phone": ["An unexpected error occurred"]},
            },
        )


@router.post(
    "/verify",
    response_model=sms_schemas.SMSVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify SMS code and authenticate",
    description="Verify the SMS code and authenticate the user (create account if new)",
)
async def verify_code_and_authenticate(
    request: sms_schemas.SMSVerifyRequest,
    sms_service: SMSService = Depends(get_sms_service),
) -> sms_schemas.SMSVerifyResponse:
    """
    Verify SMS code and authenticate user.

    This endpoint:
    1. Verifies the SMS code against the stored code in Redis
    2. Creates a new user if the phone number doesn't exist
    3. Returns a JWT token for authentication

    Args:
        request: Phone number and verification code
        sms_service: SMS service dependency

    Returns:
        Authentication response with JWT token and user info

    Raises:
        HTTPException 400: If code is invalid or expired
        HTTPException 422: If validation fails
    """
    try:
        # Authenticate via SMS
        result = await sms_service.authenticate_with_sms(request.phone, request.code)

        if result is None:
            logger.warning(f"Failed SMS verification for {request.phone}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Invalid or expired verification code",
                    "errors": {"code": ["The verification code is invalid or expired"]},
                },
            )

        user, is_new_user = result

        # Create JWT token (Laravel Sanctum-style format)
        access_token_jwt = AuthService.create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )

        # Format token like Laravel Sanctum: "{id}|{plainTextToken}"
        sanctum_token = f"{user.id}|{access_token_jwt}"

        logger.info(
            f"SMS authentication successful for {request.phone}: "
            f"user_id={user.id}, is_new={is_new_user}"
        )

        return sms_schemas.SMSVerifyResponse(
            message=(
                "Account created and authenticated successfully"
                if is_new_user
                else "Authentication successful"
            ),
            token=sanctum_token,
            role=user.role,
            user_id=user.id,
            is_new_user=is_new_user,
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during SMS verification for {request.phone}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "An unexpected error occurred during verification",
                "errors": {"code": ["An unexpected error occurred"]},
            },
        )
