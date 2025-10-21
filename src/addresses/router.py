"""
Address router - API endpoint definitions.
Handles HTTP requests and delegates to service layer.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, status

from src.addresses.dependencies import get_address_service
from src.addresses.schemas import (
    AddressCreate,
    AddressResponse,
    AddressUpdate,
    EquipmentTypeResponse,
    EquipmentWithTypeResponse,
    AddEquipmentRequest,
    BadgeResponse,
    AddBadgeRequest,
)
from src.addresses.service import AddressService
from src.auth.users import current_active_user
from src.auth.models_fastapi_users import User


router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.post(
    "/add-studio",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new studio",
    description="Creates a new studio address with automatic slug generation and validation.",
)
async def create_address(
    data: AddressCreate,
    service: Annotated[AddressService, Depends(get_address_service)],
    current_user: Annotated[User, Depends(current_active_user)],
) -> AddressResponse:
    """
    Create a new studio address.

    **Business Rules:**
    - Generates URL-friendly slug from name
    - Ensures slug uniqueness
    - Validates city and company existence (via foreign key constraints)
    - Initializes with default inactive/unpublished state
    """
    address = await service.create_address(data)
    return AddressResponse.model_validate(address)


@router.get(
    "/{address_id}",
    response_model=AddressResponse,
    summary="Get studio by ID",
    description="Retrieves a studio address with all related data.",
)
async def get_address(
    address_id: int,
    service: Annotated[AddressService, Depends(get_address_service)],
) -> AddressResponse:
    """Retrieve studio address by ID."""
    address = await service.get_address(address_id)
    return AddressResponse.model_validate(address)


@router.get(
    "/slug/{slug}",
    response_model=AddressResponse,
    summary="Get studio by slug",
    description="Retrieves a studio address by its URL slug.",
)
async def get_address_by_slug(
    slug: str,
    service: Annotated[AddressService, Depends(get_address_service)],
) -> AddressResponse:
    """Retrieve studio address by slug."""
    address = await service.get_address_by_slug(slug)
    return AddressResponse.model_validate(address)


@router.get(
    "/company/{company_id}",
    response_model=list[AddressResponse],
    summary="Get all studios for a company",
    description="Retrieves all studio addresses belonging to a specific company.",
)
async def get_company_addresses(
    company_id: int,
    service: Annotated[AddressService, Depends(get_address_service)],
) -> list[AddressResponse]:
    """Retrieve all addresses for a company."""
    addresses = await service.get_company_addresses(company_id)
    return [AddressResponse.model_validate(addr) for addr in addresses]


@router.patch(
    "/{address_id}",
    response_model=AddressResponse,
    summary="Update studio",
    description="Updates studio address information with automatic slug regeneration if name changes.",
)
async def update_address(
    address_id: int,
    data: AddressUpdate,
    service: Annotated[AddressService, Depends(get_address_service)],
    current_user: Annotated[User, Depends(current_active_user)],
) -> AddressResponse:
    """Update existing studio address."""
    address = await service.update_address(address_id, data)
    return AddressResponse.model_validate(address)


@router.delete(
    "/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete studio",
    description="Permanently removes a studio address and all related data (cascade delete).",
)
async def delete_address(
    address_id: int,
    service: Annotated[AddressService, Depends(get_address_service)],
    current_user: Annotated[User, Depends(current_active_user)],
) -> None:
    """Delete studio address."""
    await service.delete_address(address_id)


@router.post(
    "/{address_id}/publish",
    response_model=AddressResponse,
    summary="Publish studio",
    description="Makes a studio visible to the public. Only active studios can be published.",
)
async def publish_address(
    address_id: int,
    service: Annotated[AddressService, Depends(get_address_service)],
    current_user: Annotated[User, Depends(current_active_user)],
) -> AddressResponse:
    """Publish a studio address."""
    address = await service.publish_address(address_id)
    return AddressResponse.model_validate(address)


@router.post(
    "/{address_id}/unpublish",
    response_model=AddressResponse,
    summary="Unpublish studio",
    description="Hides a studio from public view without deleting it.",
)
async def unpublish_address(
    address_id: int,
    service: Annotated[AddressService, Depends(get_address_service)],
    current_user: Annotated[User, Depends(current_active_user)],
) -> AddressResponse:
    """Unpublish a studio address."""
    address = await service.unpublish_address(address_id)
    return AddressResponse.model_validate(address)


# Equipment Endpoints

@router.get(
    "/equipment-types",
    response_model=list[EquipmentTypeResponse],
    summary="Get all equipment types"
)
async def get_equipment_types(
    service: Annotated[AddressService, Depends(get_address_service)],
):
    """Get all available equipment types."""
    equipment_types = await service.get_equipment_types()
    return [EquipmentTypeResponse.model_validate(et) for et in equipment_types]


@router.get(
    "/{address_id}/equipment",
    response_model=list[EquipmentWithTypeResponse],
    summary="Get equipment for an address"
)
async def get_address_equipment(
    address_id: int,
    service: Annotated[AddressService, Depends(get_address_service)],
):
    """
    Get all equipment for a specific address.

    Matches Laravel route: GET /address/{address_id}/equipment
    """
    equipment = await service.get_address_equipment(address_id)
    return [EquipmentWithTypeResponse.model_validate(eq) for eq in equipment]


@router.post(
    "/{address_id}/equipment",
    response_model=list[EquipmentWithTypeResponse],
    summary="Add equipment to address"
)
async def add_equipment(
    address_id: int,
    data: AddEquipmentRequest,
    service: Annotated[AddressService, Depends(get_address_service)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    """
    Add equipment to an address.

    Matches Laravel route: POST /address/{address_id}/equipment
    """
    equipment = await service.add_equipment(address_id, data.equipment_ids)
    return [EquipmentWithTypeResponse.model_validate(eq) for eq in equipment]


@router.delete(
    "/{address_id}/equipment",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove equipment from address"
)
async def remove_equipment(
    address_id: int,
    equipment_ids: list[int],
    service: Annotated[AddressService, Depends(get_address_service)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    """
    Remove equipment from an address.

    Matches Laravel route: DELETE /address/{address_id}/equipment
    """
    await service.remove_equipment(address_id, equipment_ids)


# Badge Endpoints

@router.get(
    "/{address_id}/badges",
    response_model=list[BadgeResponse],
    summary="Get badges for an address"
)
async def get_address_badges(
    address_id: int,
    service: Annotated[AddressService, Depends(get_address_service)],
):
    """
    Get all badges/amenities for a specific address.

    Matches Laravel route: GET /address/{address_id}/badges
    """
    badges = await service.get_address_badges(address_id)
    return [BadgeResponse.model_validate(badge) for badge in badges]


@router.post(
    "/{address_id}/badges",
    response_model=list[BadgeResponse],
    summary="Add badges to address"
)
async def add_badges(
    address_id: int,
    data: AddBadgeRequest,
    service: Annotated[AddressService, Depends(get_address_service)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    """
    Add badges/amenities to an address.

    Matches Laravel route: POST /address/{address_id}/badge
    """
    badges = await service.add_badges(address_id, data.badge_ids)
    return [BadgeResponse.model_validate(badge) for badge in badges]
