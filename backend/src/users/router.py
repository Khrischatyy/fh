"""
User router - HTTP endpoints for user operations.
Matches Laravel API routes for backward compatibility.
"""
from typing import Annotated, Any
from fastapi import APIRouter, Depends, status, UploadFile, File, Form, HTTPException
import stripe
from stripe import StripeError

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.geographic.schemas import LaravelResponse
from src.config import settings
from src.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.users.schemas import UserUpdateRequest, PhotoUploadResponse, RoleRequest
from src.users.service import UserService

router = APIRouter(prefix="/user", tags=["User"])

# Initialize Stripe
stripe.api_key = settings.stripe_api_key


@router.get("/me", response_model=LaravelResponse[Any], status_code=status.HTTP_200_OK)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get current authenticated user information.

    Laravel compatible: GET /api/user/me

    Returns:
        User information with role, company details, and authentication status
    """
    from src.companies.models import AdminCompany
    from src.database import AsyncSessionLocal
    from sqlalchemy import select

    # Get user's company slug if they have one
    company_slug = None
    has_company = False
    company_data = None

    async with AsyncSessionLocal() as session:
        # Check if user is admin of any company
        stmt = select(AdminCompany).where(AdminCompany.admin_id == current_user.id)
        result = await session.execute(stmt)
        admin_company = result.scalar_one_or_none()

        if admin_company:
            has_company = True
            # Load company to get slug
            from src.companies.models import Company
            stmt = select(Company).where(Company.id == admin_company.company_id)
            result = await session.execute(stmt)
            company = result.scalar_one_or_none()
            if company:
                company_slug = company.slug
                company_data = {
                    "id": company.id,
                    "name": company.name,
                    "slug": company.slug,
                    "logo": company.logo,
                }

    # Build user data
    user_data = {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "firstname": current_user.firstname,
        "lastname": current_user.lastname,
        "username": current_user.username,
        "phone": current_user.phone,
        "date_of_birth": current_user.date_of_birth.isoformat() if current_user.date_of_birth else None,
        "profile_photo": current_user.profile_photo,
        "role": current_user.role,
        "email_verified_at": current_user.email_verified_at.isoformat() if current_user.email_verified_at else None,
        "payment_gateway": current_user.payment_gateway,
        "stripe_account_id": current_user.stripe_account_id,
        "google_id": current_user.google_id,
        "created_at": current_user.created_at.isoformat(),
        "updated_at": current_user.updated_at.isoformat(),
        "company": company_data,  # Add company to user object
    }

    return LaravelResponse(
        success=True,
        data={
            "message": "User information retrieved successfully",
            "role": current_user.role,
            "user": user_data,
            "company_slug": company_slug,
            "has_company": has_company,
        },
        message="User information retrieved successfully.",
        code=200
    )


@router.post("/payment/stripe/create-account", response_model=LaravelResponse[Any], status_code=status.HTTP_200_OK)
async def create_stripe_account(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create a Stripe Connect account for the user.

    Laravel compatible: POST /api/user/payment/stripe/create-account

    Returns:
        Stripe account ID (frontend will call /refresh to get the onboarding link)
    """
    try:
        # Check if user already has a Stripe account
        if current_user.stripe_account_id:
            return LaravelResponse(
                success=True,
                data={
                    "account_id": current_user.stripe_account_id,
                },
                message="Stripe account already exists.",
                code=200
            )

        # Create new Stripe Connect account
        # Use a valid URL for business profile (Stripe doesn't accept localhost or 127.0.0.1)
        if "localhost" in settings.frontend_url or "127.0.0.1" in settings.frontend_url:
            business_url = "https://funny-how.com"
        else:
            business_url = settings.frontend_url

        account = stripe.Account.create(
            type="express",
            country="US",
            email=current_user.email,
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            business_type="individual",
            business_profile={
                "mcc": "7922",  # Theatrical Producers and Ticket Agencies
                "url": business_url,
            },
        )

        # Update user with Stripe account ID
        current_user.stripe_account_id = account.id
        current_user.payment_gateway = "stripe"
        await db.commit()
        await db.refresh(current_user)

        return LaravelResponse(
            success=True,
            data={
                "account_id": account.id,
            },
            message="Stripe account created successfully.",
            code=200
        )

    except StripeError as e:
        return LaravelResponse(
            success=False,
            data={"error": str(e)},
            message=f"Stripe error: {str(e)}",
            code=400
        )
    except Exception as e:
        return LaravelResponse(
            success=False,
            data={"error": str(e)},
            message=f"Error creating Stripe account: {str(e)}",
            code=500
        )


@router.get("/payment/stripe/refresh", response_model=LaravelResponse[Any], status_code=status.HTTP_200_OK)
async def refresh_stripe_account_link(
    account_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Generate Stripe onboarding link for account setup.

    Laravel compatible: GET /api/user/payment/stripe/refresh?account_id={account_id}

    Returns:
        Stripe onboarding URL for user to complete account setup
    """
    try:
        # Check if user has no Stripe account yet
        if not current_user.stripe_account_id or account_id in ("undefined", "null", "None"):
            return LaravelResponse(
                success=False,
                data={
                    "error": "No Stripe account found",
                    "action": "create_account",
                    "message": "Please create a Stripe account first by calling /payment/stripe/create-account"
                },
                message="No Stripe account connected. Please create one first.",
                code=404
            )

        # Verify the account_id belongs to the current user
        if current_user.stripe_account_id != account_id:
            return LaravelResponse(
                success=False,
                data={"error": "Account ID does not match user"},
                message="Unauthorized access to Stripe account",
                code=403
            )

        # Create account link for onboarding
        account_link = stripe.AccountLink.create(
            account=account_id,
            refresh_url=f"{settings.frontend_url}/payout",
            return_url=f"{settings.frontend_url}/payout",
            type="account_onboarding",
        )

        return LaravelResponse(
            success=True,
            data={
                "url": account_link.url,
            },
            message="Stripe account link created successfully.",
            code=200
        )

    except StripeError as e:
        return LaravelResponse(
            success=False,
            data={"error": str(e)},
            message=f"Stripe error: {str(e)}",
            code=400
        )
    except Exception as e:
        return LaravelResponse(
            success=False,
            data={"error": str(e)},
            message=f"Error creating Stripe account link: {str(e)}",
            code=500
        )


@router.get("/payment/account/retrieve", response_model=LaravelResponse[Any], status_code=status.HTTP_200_OK)
async def retrieve_payment_account(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Retrieve payment account details.

    Laravel compatible: GET /api/user/payment/account/retrieve

    Returns:
        Payment account information including charges_enabled, payouts_enabled, etc.
    """
    try:
        # Check if user has a Stripe account
        if not current_user.stripe_account_id:
            return LaravelResponse(
                success=False,
                data={"error": "No payment account connected"},
                message="No payment account found",
                code=404
            )

        # Retrieve Stripe account details
        account = stripe.Account.retrieve(current_user.stripe_account_id)

        # Extract relevant account information
        account_data = {
            "id": account.id,
            "type": account.type,
            "email": account.email,
            "charges_enabled": account.charges_enabled,
            "payouts_enabled": account.payouts_enabled,
            "details_submitted": account.details_submitted,
            "default_currency": account.default_currency,
            "country": account.country,
        }

        return LaravelResponse(
            success=True,
            data=account_data,
            message="Payment account retrieved successfully.",
            code=200
        )

    except StripeError as e:
        return LaravelResponse(
            success=False,
            data={"error": str(e)},
            message=f"Stripe error: {str(e)}",
            code=400
        )
    except Exception as e:
        return LaravelResponse(
            success=False,
            data={"error": str(e)},
            message=f"Error retrieving payment account: {str(e)}",
            code=500
        )


@router.get("/payment/stripe/balance", response_model=LaravelResponse[Any], status_code=status.HTTP_200_OK)
async def get_stripe_balance(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get Stripe account balance.

    Laravel compatible: GET /api/user/payment/stripe/balance

    Returns:
        Stripe account balance information
    """
    try:
        # Check if user has a Stripe account
        if not current_user.stripe_account_id:
            return LaravelResponse(
                success=False,
                data={"error": "No Stripe account connected"},
                message="No Stripe account found",
                code=404
            )

        # Get balance for the connected account
        balance = stripe.Balance.retrieve(
            stripe_account=current_user.stripe_account_id
        )

        # Format balance data
        balance_data = {
            "available": [
                {
                    "amount": bal.amount,
                    "currency": bal.currency,
                    "source_types": bal.source_types if hasattr(bal, 'source_types') else {}
                }
                for bal in balance.available
            ],
            "pending": [
                {
                    "amount": bal.amount,
                    "currency": bal.currency,
                    "source_types": bal.source_types if hasattr(bal, 'source_types') else {}
                }
                for bal in balance.pending
            ],
        }

        return LaravelResponse(
            success=True,
            data=balance_data,
            message="Stripe balance retrieved successfully.",
            code=200
        )

    except StripeError as e:
        return LaravelResponse(
            success=False,
            data={"error": str(e)},
            message=f"Stripe error: {str(e)}",
            code=400
        )
    except Exception as e:
        return LaravelResponse(
            success=False,
            data={"error": str(e)},
            message=f"Error retrieving Stripe balance: {str(e)}",
            code=500
        )


@router.put("/update", response_model=LaravelResponse[Any], status_code=status.HTTP_200_OK)
async def update_user(
    request: UserUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Update user profile information.

    Laravel compatible: PUT /api/user/update

    Args:
        request: User update data (firstname, lastname, username, phone, date_of_birth)

    Returns:
        Updated user object
    """
    try:
        service = UserService(db)

        # Update user with provided fields
        updated_user = await service.update_user(
            user=current_user,
            firstname=request.firstname,
            lastname=request.lastname,
            username=request.username,
            phone=request.phone,
            date_of_birth=request.date_of_birth,
        )

        # Format response to match Laravel
        user_data = {
            "id": updated_user.id,
            "firstname": updated_user.firstname,
            "lastname": updated_user.lastname,
            "username": updated_user.username,
            "phone": updated_user.phone,
            "date_of_birth": updated_user.date_of_birth.isoformat() if updated_user.date_of_birth else None,
            "email": updated_user.email,
            "created_at": updated_user.created_at.isoformat(),
            "updated_at": updated_user.updated_at.isoformat(),
        }

        return LaravelResponse(
            success=True,
            data=user_data,
            message="User updated successfully.",
            code=200
        )

    except HTTPException as e:
        # Re-raise validation errors
        raise e
    except Exception as e:
        return LaravelResponse(
            success=False,
            data={"error": str(e)},
            message="Failed to update user.",
            code=500
        )


@router.post("/update-photo", response_model=LaravelResponse[PhotoUploadResponse], status_code=status.HTTP_200_OK)
async def update_photo(
    photo: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Update user profile photo.

    Laravel compatible: POST /api/user/update-photo

    Args:
        photo: Image file (jpeg, png, jpg, gif, heic, heif - max 5MB)

    Returns:
        Photo URL
    """
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/gif", "image/heic", "image/heif"]
        if photo.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "The photo must be a file of type: jpeg, png, jpg, gif, heic, heif.",
                    "errors": {"photo": ["The photo must be a file of type: jpeg, png, jpg, gif, heic, heif."]}
                }
            )

        # Validate file size (5MB = 5120 KB)
        content = await photo.read()
        await photo.seek(0)  # Reset file pointer
        if len(content) > 5120 * 1024:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "The photo must not be greater than 5120 kilobytes.",
                    "errors": {"photo": ["The photo must not be greater than 5120 kilobytes."]}
                }
            )

        service = UserService(db)
        photo_url = await service.update_photo(current_user, photo)

        return LaravelResponse(
            success=True,
            data={"photo_url": photo_url},
            message="Photo updated successfully.",
            code=200
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        return LaravelResponse(
            success=False,
            data={"error": str(e)},
            message="Failed to update photo.",
            code=500
        )


@router.post("/set-role", response_model=LaravelResponse[str], status_code=status.HTTP_200_OK)
async def set_role(
    request: RoleRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Set user role (one-time operation).

    Laravel compatible: POST /api/user/set-role

    Args:
        request: Role data (user or studio_owner)

    Returns:
        Role name

    Note:
        This can only be called once per user. After role is set, subsequent calls will return 409 Conflict.
    """
    try:
        service = UserService(db)
        role_name = await service.set_role(current_user, request.role)

        return LaravelResponse(
            success=True,
            data=role_name,
            message="Role updated successfully.",
            code=200
        )

    except HTTPException as e:
        if e.status_code == status.HTTP_409_CONFLICT:
            return LaravelResponse(
                success=False,
                data=None,
                message="User already has a role.",
                code=409
            )
        raise e
    except Exception as e:
        return LaravelResponse(
            success=False,
            data={"error": str(e)},
            message="Failed to update role.",
            code=500
        )
