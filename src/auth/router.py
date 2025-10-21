"""
Authentication router with login, registration, and OAuth endpoints.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from authlib.integrations.starlette_client import OAuth
import httpx

from src.database import get_db
from src.auth import schemas
from src.auth.models import User
from src.auth.service import auth_service
from src.auth.dependencies import get_current_user
from src.config import settings
from src.exceptions import UnauthorizedException, BadRequestException


router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth setup
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.post("/register", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: schemas.UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.

    - **email**: User's email address (must be unique)
    - **password**: Password (min 8 characters)
    - **firstname**: User's first name
    - **lastname**: User's last name
    """
    user = await auth_service.register_user(db, user_data)

    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    # TODO: Send verification email
    # await send_verification_email(user.email, verification_token)

    return schemas.TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/login", response_model=schemas.TokenResponse)
async def login(
    credentials: schemas.UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return access token.

    - **email**: User's email address
    - **password**: User's password
    """
    user = await auth_service.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise UnauthorizedException("Incorrect email or password")

    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return schemas.TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user information.
    Requires authentication token in Authorization header.
    """
    return current_user


@router.post("/verify-email")
async def verify_email(
    verification_data: schemas.EmailVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify user email with verification token.

    - **token**: Email verification token sent to user's email
    """
    # TODO: Implement email verification logic
    # - Decode/validate token
    # - Get user from token
    # - Mark email as verified
    # - Return success response

    return {"message": "Email verified successfully"}


@router.post("/forgot-password")
async def forgot_password(
    reset_request: schemas.PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset link.

    - **email**: User's email address
    """
    user = await auth_service.get_user_by_email(db, reset_request.email)
    if user:
        # Generate reset token
        reset_token = auth_service.generate_verification_token()

        # TODO: Store reset token with expiration
        # TODO: Send password reset email
        # await send_password_reset_email(user.email, reset_token)

    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    reset_data: schemas.PasswordReset,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password with reset token.

    - **token**: Password reset token from email
    - **password**: New password
    - **password_confirmation**: Password confirmation
    """
    # TODO: Implement password reset logic
    # - Validate reset token
    # - Get user from token
    # - Change password
    # - Invalidate reset token
    # - Return success response

    return {"message": "Password reset successfully"}


@router.get("/google/redirect")
async def google_redirect():
    """
    Redirect to Google OAuth consent screen.
    Returns the Google OAuth authorization URL.
    """
    redirect_uri = settings.google_redirect_uri
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.google_client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=openid email profile&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    return {"url": google_auth_url}


@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Google OAuth callback.

    - **code**: Authorization code from Google (query parameter)
    """
    # Exchange code for access token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.google_redirect_uri,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data)
        if token_response.status_code != 200:
            raise BadRequestException("Failed to obtain access token from Google")

        token_json = token_response.json()
        access_token = token_json.get("access_token")

        # Get user info from Google
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_response = await client.get(userinfo_url, headers=headers)

        if userinfo_response.status_code != 200:
            raise BadRequestException("Failed to get user info from Google")

        user_info = userinfo_response.json()

    # Create or get user
    google_id = user_info.get("id")
    email = user_info.get("email")
    firstname = user_info.get("given_name", "")
    lastname = user_info.get("family_name", "")
    avatar = user_info.get("picture")

    user = await auth_service.get_user_by_google_id(db, google_id)
    if not user:
        user = await auth_service.create_google_user(
            db,
            google_id=google_id,
            email=email,
            firstname=firstname,
            lastname=lastname,
            avatar=avatar,
        )

    # Create access token
    app_access_token = auth_service.create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return schemas.GoogleAuthResponse(
        access_token=app_access_token,
        token_type="bearer",
        user=schemas.UserResponse.model_validate(user),
    )


@router.post("/resend-verification")
async def resend_verification(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Resend email verification link.
    Requires authentication.
    """
    if current_user.is_verified:
        raise BadRequestException("Email is already verified")

    # Generate new verification token
    verification_token = auth_service.generate_verification_token()

    # TODO: Store verification token
    # TODO: Send verification email
    # await send_verification_email(current_user.email, verification_token)

    return {"message": "Verification email sent"}
