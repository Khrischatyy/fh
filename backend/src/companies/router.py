"""
Company router - HTTP endpoints for company management.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, status

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.companies.schemas import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyWithAddressesResponse,
)
from src.companies.service import CompanyService
from src.companies.dependencies import get_company_service

router = APIRouter(prefix="/companies", tags=["Companies"])


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
