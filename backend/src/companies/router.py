"""
Company router - HTTP endpoints for company management.
"""
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Form

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.companies.schemas import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyWithAddressesResponse,
    BrandCreateRequest,
    BrandCreateResponse,
)
from src.companies.service import CompanyService
from src.companies.dependencies import get_company_service

router = APIRouter(prefix="/companies", tags=["Companies"])

# Brand router (no prefix, matches Laravel route)
brand_router = APIRouter(tags=["Brand"])


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    data: CompanyCreate,
    service: Annotated[CompanyService, Depends(get_company_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Create a new company (brand).

    Business rules:
    - User can only have one company
    - Slug is auto-generated from name
    - Current user is automatically added as admin
    """
    company = await service.create_company(data, current_user.id)
    return CompanyResponse.model_validate(company)


@router.get("/my-companies", response_model=list[CompanyResponse], status_code=status.HTTP_200_OK)
async def get_my_companies(
    service: Annotated[CompanyService, Depends(get_company_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get all companies where current user is admin.
    """
    companies = await service.get_user_companies(current_user.id)
    return [CompanyResponse.model_validate(company) for company in companies]


@router.get("/{company_id}", response_model=CompanyResponse, status_code=status.HTTP_200_OK)
async def get_company(
    company_id: int,
    service: Annotated[CompanyService, Depends(get_company_service)],
):
    """
    Get company by ID.

    Args:
        company_id: The company ID

    Raises:
        NotFoundException: If company not found
    """
    company = await service.get_company(company_id)
    return CompanyResponse.model_validate(company)


@router.get("/slug/{slug}", response_model=CompanyWithAddressesResponse, status_code=status.HTTP_200_OK)
async def get_company_by_slug(
    slug: str,
    service: Annotated[CompanyService, Depends(get_company_service)],
):
    """
    Get company by slug with addresses.

    This endpoint matches Laravel's `GET /company/{slug}` route.

    Args:
        slug: The company slug

    Raises:
        NotFoundException: If company not found
    """
    company = await service.get_company_by_slug(slug)
    return CompanyWithAddressesResponse.model_validate(company)


@router.patch("/{company_id}", response_model=CompanyResponse, status_code=status.HTTP_200_OK)
async def update_company(
    company_id: int,
    data: CompanyUpdate,
    service: Annotated[CompanyService, Depends(get_company_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Update company details.

    Requires user to be admin of the company.

    Args:
        company_id: The company ID
        data: Company update data

    Raises:
        NotFoundException: If company not found
        ForbiddenException: If user is not admin
    """
    # Check if user is admin
    if not await service.is_admin(company_id, current_user.id):
        from src.exceptions import ForbiddenException
        raise ForbiddenException("You are not authorized to update this company")

    company = await service.update_company(company_id, data)
    return CompanyResponse.model_validate(company)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    service: Annotated[CompanyService, Depends(get_company_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Delete a company.

    Requires user to be admin of the company.

    Args:
        company_id: The company ID

    Raises:
        NotFoundException: If company not found
        ForbiddenException: If user is not admin
    """
    # Check if user is admin
    if not await service.is_admin(company_id, current_user.id):
        from src.exceptions import ForbiddenException
        raise ForbiddenException("You are not authorized to delete this company")

    await service.delete_company(company_id)


# Brand creation endpoint (matches Laravel POST /api/brand)
@brand_router.post(
    "/brand",
    status_code=status.HTTP_201_CREATED,
    summary="Create brand (company + address + default setup)",
    description="Creates a complete brand setup: company, address, default room, and default operating hours."
)
async def create_brand(
    company: Annotated[str, Form(description="Company name (unique)")],
    street: Annotated[str, Form(description="Street address")],
    city: Annotated[str, Form(description="City name")],
    country: Annotated[str, Form(description="Country name")],
    latitude: Annotated[float, Form(ge=-90, le=90, description="Latitude")],
    longitude: Annotated[float, Form(ge=-180, le=180, description="Longitude")],
    zip: Annotated[str, Form(description="ZIP/Postal code")],
    timezone: Annotated[str, Form(description="Timezone")],
    service: Annotated[CompanyService, Depends(get_company_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    address: Annotated[Optional[str], Form(description="Full address (optional)")] = None,
    about: Annotated[Optional[str], Form(description="About (optional)")] = None,
):
    """
    Create a complete brand/studio setup in one request.

    This endpoint is a convenience method that creates:
    - Company (brand)
    - Address with geolocation
    - Default room ("Room1")
    - Default operating hours (24/7)
    - Default pricing ($60/hour)

    **Form Data:**
    - **company**: Company name (must be unique)
    - **street**: Street address
    - **city**: City name
    - **country**: Country name
    - **latitude**: Latitude coordinate
    - **longitude**: Longitude coordinate
    - **zip**: ZIP/Postal code
    - **timezone**: Timezone (e.g., "America/Los_Angeles")
    - **address**: Full address (optional)
    - **about**: About the studio (optional)

    **Returns:**
    - **slug**: Company slug
    - **address_id**: Created address ID
    - **room_id**: Created room ID

    **Business Rules:**
    - User must be authenticated
    - User must have "studio_owner" role
    - User can only have one company (throws error if already exists)
    - Country and city are created if they don't exist
    - Address slug is auto-generated from company name and city
    """
    # Check if user is studio owner
    if current_user.role != "studio_owner":
        from src.exceptions import ForbiddenException
        raise ForbiddenException("You are not studio owner")

    # Create request object from form data
    data = BrandCreateRequest(
        company=company,
        street=street,
        city=city,
        country=country,
        latitude=latitude,
        longitude=longitude,
        zip=zip,
        timezone=timezone,
        address=address,
        about=about,
    )

    result = await service.create_brand(data, current_user.id)

    # Return Laravel-compatible response format
    return {
        "success": True,
        "data": {
            "slug": result["slug"],
            "address_id": result["address_id"],
            "room_id": result["room_id"],
        },
        "message": "Company and address added",
        "code": 201
    }
