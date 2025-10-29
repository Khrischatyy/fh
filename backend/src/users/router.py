"""
User router - HTTP endpoints for user operations.
Matches Laravel API routes for backward compatibility.
"""
from typing import Annotated, Any
from fastapi import APIRouter, Depends, status

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.geographic.schemas import LaravelResponse

router = APIRouter(prefix="/user", tags=["User"])


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
