"""
User router - HTTP endpoints for user operations.
Matches Laravel API routes for backward compatibility.
"""
from typing import Annotated, Any
from fastapi import APIRouter, Depends, status
import stripe
from stripe import StripeError

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.geographic.schemas import LaravelResponse
from src.config import settings
from src.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

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
        # Use a valid URL for business profile (Stripe doesn't accept localhost)
        business_url = settings.frontend_url if not settings.frontend_url.startswith("http://localhost") else "https://funny-how.com"

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
