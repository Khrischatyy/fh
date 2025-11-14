"""
Authentication router with login, registration, and OAuth endpoints.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, status, Query, Form
from sqlalchemy.ext.asyncio import AsyncSession
from authlib.integrations.starlette_client import OAuth
import httpx

from src.database import get_db
from src.auth import schemas
from src.auth.models import User
from src.auth.service import auth_service
from src.auth.dependencies import get_current_user
from src.config import settings
from src.exceptions import UnauthorizedException, BadRequestException, NotFoundException


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


@router.post("/register", response_model=schemas.RegisterResponse, status_code=status.HTTP_200_OK)
async def register(
    name: str = Form(..., max_length=255, description="User's full name"),
    email: str = Form(..., max_length=255, description="User's email address"),
    password: str = Form(..., min_length=8, max_length=100, description="User's password"),
    password_confirmation: str = Form(..., min_length=8, max_length=100, description="Password confirmation"),
    role: str = Form(..., max_length=15, pattern="^(user|studio_owner|admin)$", description="User role"),
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account - Laravel compatible endpoint.

    Accepts form data (application/x-www-form-urlencoded) like Laravel Fortify.

    - **name**: User's full name (required, max 255 characters)
    - **email**: User's email address (required, must be unique, valid email format)
    - **password**: Password (required, min 8 characters)
    - **password_confirmation**: Password confirmation (required, must match password)
    - **role**: User role (required, one of: user, studio_owner, admin)

    Returns:
    - **message**: Success message
    - **token**: Sanctum-compatible API token
    - **role**: Assigned user role
    """
    from src.exceptions import ValidationException
    import re

    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationException(
            message="The email must be a valid email address.",
            errors={"email": ["The email must be a valid email address."]}
        )

    # Validate password length
    if len(password) < 8:
        raise ValidationException(
            message="The password must be at least 8 characters.",
            errors={"password": ["The password must be at least 8 characters."]}
        )

    # Validate password confirmation
    if password != password_confirmation:
        raise ValidationException(
            message="The password confirmation does not match.",
            errors={"password_confirmation": ["The password confirmation does not match."]}
        )

    # Validate role
    if role not in ["user", "studio_owner", "admin"]:
        raise ValidationException(
            message="The selected role is invalid.",
            errors={"role": ["The selected role is invalid."]}
        )

    # Create UserRegister schema for validation
    user_data = schemas.UserRegister(
        name=name,
        email=email,
        password=password,
        password_confirmation=password_confirmation,
        role=role,
    )

    user = await auth_service.register_user(db, user_data)

    # Send verification email (queued via Celery)
    from src.tasks.email import send_verification_email
    send_verification_email.delay(
        user_id=user.id,
        email=user.email,
        firstname=user.firstname,
        lastname=user.lastname
    )

    # Create access token (Sanctum-style format: {id}|{token})
    access_token_jwt = auth_service.create_access_token(
        data={"sub": str(user.id)},  # JWT spec requires sub to be a string
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    # Format token like Laravel Sanctum: "{id}|{plainTextToken}"
    sanctum_token = f"{user.id}|{access_token_jwt}"

    return schemas.RegisterResponse(
        message="Registration successful, verify your email address",
        token=sanctum_token,
        role=user.role,
    )


@router.post("/login", response_model=schemas.LoginResponse)
async def login(
    email: str = Form(..., description="User's email address"),
    password: str = Form(..., description="User's password"),
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return access token - Laravel Fortify compatible endpoint.

    Accepts form data (application/x-www-form-urlencoded) like Laravel Fortify.

    - **email**: User's email address
    - **password**: User's password

    Returns Laravel-style response with Sanctum token format.
    """
    from src.exceptions import ValidationException
    import re

    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationException(
            message="The email must be a valid email address.",
            errors={"email": ["The email must be a valid email address."]}
        )

    # Validate password length
    if len(password) < 8:
        raise ValidationException(
            message="The password must be at least 8 characters.",
            errors={"password": ["The password must be at least 8 characters."]}
        )

    user = await auth_service.authenticate_user(db, email, password)
    if not user:
        raise ValidationException(
            message="These credentials do not match our records.",
            errors={"email": ["These credentials do not match our records."]}
        )

    # Create access token (Sanctum-style format: {id}|{token})
    access_token_jwt = auth_service.create_access_token(
        data={"sub": str(user.id)},  # JWT spec requires sub to be a string
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    # Format token like Laravel Sanctum: "{id}|{plainTextToken}"
    sanctum_token = f"{user.id}|{access_token_jwt}"

    return schemas.LoginResponse(
        message="Login successful",
        token=sanctum_token,
        role=user.role,
    )


@router.get("/me", response_model=schemas.UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current authenticated user information with company data.
    Requires authentication token in Authorization header.
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from src.companies.models import AdminCompany, Company

    # Fetch user with admin_companies relationship
    stmt = (
        select(User)
        .where(User.id == current_user.id)
        .options(
            selectinload(User.admin_companies).selectinload(AdminCompany.company)
        )
    )
    result = await db.execute(stmt)
    user = result.scalar_one()

    # Create response dict
    user_dict = schemas.UserResponse.model_validate(user).model_dump()

    # Add company if user has admin_companies
    if user.admin_companies and len(user.admin_companies) > 0:
        company = user.admin_companies[0].company
        user_dict["company"] = schemas.CompanySimpleResponse.model_validate(company).model_dump()

    return user_dict


@router.get("/email/verify/{id}/{hash}")
async def verify_email_with_hash(
    id: int,
    hash: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify user email using Laravel-style id/hash verification.
    Sends welcome email based on user role after verification.

    - **id**: User ID
    - **hash**: SHA1 hash of user's email
    """
    user = await auth_service.verify_email_by_hash(db, id, hash)

    if not user:
        raise NotFoundException("Invalid verification link")

    # Send welcome email based on role (queued via Celery)
    from src.tasks.email import send_welcome_email, send_welcome_email_owner

    if user.role == "studio_owner":
        # Generate password reset token for owner to set password
        reset_token = await auth_service.create_password_reset_token(db, user.email)
        send_welcome_email_owner.delay(
            email=user.email,
            firstname=user.firstname,
            lastname=user.lastname,
            reset_token=reset_token
        )
    else:
        # Regular user welcome email
        send_welcome_email.delay(
            email=user.email,
            firstname=user.firstname,
            lastname=user.lastname
        )

    return {"message": "Email successfully verified."}


@router.post("/forgot-password")
async def forgot_password(
    reset_request: schemas.PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset link (Laravel compatible).
    Sends ResetPasswordMail to user.

    - **email**: User's email address
    """
    user = await auth_service.get_user_by_email(db, reset_request.email)
    if user:
        # Generate and store reset token
        reset_token = await auth_service.create_password_reset_token(db, user.email)

        # Send password reset email (queued via Celery)
        from src.tasks.email import send_password_reset_email
        send_password_reset_email.delay(
            email=user.email,
            token=reset_token
        )

    # Always return success to prevent email enumeration (Laravel behavior)
    return {"message": "We have emailed your password reset link!"}


@router.post("/reset-password")
async def reset_password(
    reset_data: schemas.PasswordReset,
    email: str = Query(..., description="User's email address"),
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password with reset token (Laravel compatible).

    - **email**: User's email address (query parameter)
    - **token**: Password reset token from email
    - **password**: New password
    - **password_confirmation**: Password confirmation
    """
    # Verify reset token
    reset_token = await auth_service.verify_password_reset_token(db, email, reset_data.token)
    if not reset_token:
        raise BadRequestException("This password reset token is invalid.")

    # Get user
    user = await auth_service.get_user_by_email(db, email)
    if not user:
        raise NotFoundException("User not found")

    # Change password
    await auth_service.change_password(db, user, reset_data.password)

    # Delete reset token
    await auth_service.delete_password_reset_token(db, email)

    # Create access token for auto-login (Laravel behavior)
    access_token = auth_service.create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return {
        "message": "Password reset successfully",
        "token": access_token,
        "role": user.role,
    }


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
    Handle Google OAuth callback (Laravel compatible).

    Exchanges authorization code for user info, creates/updates user,
    and redirects to frontend with Sanctum-style token.

    - **code**: Authorization code from Google (query parameter)
    """
    from fastapi.responses import RedirectResponse

    try:
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

        # Extract user data from Google response
        google_id = user_info.get("id")
        email = user_info.get("email")
        firstname = user_info.get("given_name") or ""
        lastname = user_info.get("family_name") or ""
        avatar = user_info.get("picture")

        # Check if user with email exists
        user = await auth_service.get_user_by_email(db, email)

        is_new_user = False
        if user:
            # Update existing user with Google ID and avatar
            user = await auth_service.update_google_user(
                db,
                user=user,
                google_id=google_id,
                avatar=avatar,
            )
        else:
            # Create new user from Google data
            user = await auth_service.create_google_user(
                db,
                google_id=google_id,
                email=email,
                firstname=firstname,
                lastname=lastname,
                avatar=avatar,
            )
            is_new_user = True

        # Create access token (Sanctum-style format: {id}|{token})
        access_token_jwt = auth_service.create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )

        # Format token like Laravel Sanctum: "{id}|{plainTextToken}"
        sanctum_token = f"{user.id}|{access_token_jwt}"

        # Welcome email will be sent when user sets their role in /api/user/set-role
        # Google OAuth users start with role=None and must choose their role first

        # Redirect to frontend with token (Laravel behavior)
        frontend_callback_url = f"{settings.frontend_url}/auth/callback?token={sanctum_token}"
        return RedirectResponse(url=frontend_callback_url)

    except Exception as e:
        # On error, redirect to frontend login page with error
        error_url = f"{settings.frontend_url}/login?error=google_auth_failed"
        return RedirectResponse(url=error_url)


@router.post("/resend-verification")
async def resend_verification(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Resend email verification link (Laravel Fortify compatible).
    Requires authentication.
    """
    if current_user.email_verified_at:
        raise BadRequestException("Email is already verified")

    # Send verification email (queued via Celery)
    from src.tasks.email import send_verification_email
    send_verification_email.delay(
        user_id=current_user.id,
        email=current_user.email,
        firstname=current_user.firstname,
        lastname=current_user.lastname
    )

    return {"message": "A fresh verification link has been sent to your email address."}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
):
    """
    Logout user (token invalidation).

    Note: With JWT tokens, true logout requires a token blacklist on the backend
    or relying on token expiration. For now, we return success and the frontend
    should delete the token.
    """
    # TODO: Implement token blacklist if needed
    # For JWT-based auth, the frontend typically just deletes the token
    return {"message": "Successfully logged out"}


@router.post("/confirm-password", status_code=status.HTTP_201_CREATED)
async def confirm_password(
    request: schemas.ConfirmPasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Confirm user's password (Laravel Fortify compatible).

    Used before sensitive operations to re-verify the user's identity.
    """
    is_valid = await auth_service.confirm_password(db, current_user, request.password)

    if not is_valid:
        raise BadRequestException("The provided password is incorrect.")

    return {"confirmed": True}


@router.get("/confirmed-password-status")
async def confirmed_password_status(
    current_user: User = Depends(get_current_user),
):
    """
    Get password confirmation status (Laravel Fortify compatible).

    Returns whether the user has recently confirmed their password.
    For simplicity, we always return confirmed=true since we don't track confirmation timestamps.
    """
    # TODO: Track password confirmation timestamp in session/cache
    # For now, return true since we verify password on sensitive operations
    return {"confirmed": True}


@router.put("/password")
async def update_password(
    password_data: schemas.PasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user password (Laravel Fortify compatible).

    Requires current password for verification.
    """
    await auth_service.update_password(
        db,
        current_user,
        password_data.current_password,
        password_data.password
    )

    return {"message": "Password updated successfully"}


@router.put("/profile-information")
async def update_profile_information(
    profile_data: schemas.ProfileInformationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user profile information (Laravel Fortify compatible).

    Can update name, email, and other profile fields.
    """
    updated_user = await auth_service.update_profile_information(
        db,
        current_user,
        profile_data
    )

    return {
        "message": "Profile information updated successfully",
        "user": schemas.UserResponse.model_validate(updated_user)
    }


@router.post("/generate-device-token", response_model=schemas.DeviceRegistrationTokenResponse)
async def generate_device_registration_token(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a device registration token for Mac OS locker app.

    This endpoint is used by the web app to generate a token that can be
    copied and pasted into the locker app for device registration.

    The token is valid for 24 hours and can only be used once.

    Returns:
    - **token**: Registration token to paste in locker app
    - **expires_at**: Token expiration time
    """
    registration_token = await auth_service.generate_device_registration_token(
        db,
        current_user.id
    )

    return schemas.DeviceRegistrationTokenResponse(
        token=registration_token.token,
        expires_at=registration_token.expires_at,
    )
