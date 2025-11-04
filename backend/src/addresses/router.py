"""
Address router - API endpoint definitions.
Handles HTTP requests and delegates to service layer.
"""
from typing import Annotated, Any
from fastapi import APIRouter, Depends, status, Query

from src.addresses.dependencies import get_address_service
from src.operating_hours.dependencies import get_operating_hours_service
from src.operating_hours.schemas import OperatingHourResponse, OperatingModeResponse
from src.operating_hours.service import OperatingHoursService
from src.addresses.schemas import (
    AddressCreate,
    AddressResponse,
    AddressUpdate,
    EquipmentTypeResponse,
    EquipmentWithTypeResponse,
    AddEquipmentRequest,
    BadgeResponse,
    AddBadgeRequest,
    MapStudioResponse,
)
from src.addresses.service import AddressService
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.geographic.schemas import LaravelResponse


router = APIRouter(prefix="/addresses", tags=["Addresses"])

# Laravel-compatible singular /address routes
address_router = APIRouter(prefix="/address", tags=["Address"])


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
    current_user: Annotated[User, Depends(get_current_user)],
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
    current_user: Annotated[User, Depends(get_current_user)],
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
    current_user: Annotated[User, Depends(get_current_user)],
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
    current_user: Annotated[User, Depends(get_current_user)],
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
    current_user: Annotated[User, Depends(get_current_user)],
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
    current_user: Annotated[User, Depends(get_current_user)],
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
    current_user: Annotated[User, Depends(get_current_user)],
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
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Add badges/amenities to an address.

    Matches Laravel route: POST /address/{address_id}/badge
    """
    badges = await service.add_badges(address_id, data.badge_ids)
    return [BadgeResponse.model_validate(badge) for badge in badges]


# Laravel-compatible /address/studio/{slug} endpoint
@address_router.get(
    "/studio/{address_slug}",
    status_code=status.HTTP_200_OK,
)
async def get_studio_by_slug(
    address_slug: str,
):
    """
    Retrieve a studio (address) by its slug with all related data.

    Note: This endpoint returns the studio even if not fully configured,
    allowing studio owners to view their incomplete setup.

    Laravel compatible: GET /api/address/studio/{address_slug}

    Returns:
        Complete address with all relationships: badges, rooms, photos, prices,
        company, operating hours, equipment, and is_complete status

    Raises:
        NotFoundException: If address not found
    """
    from src.addresses.repository import AddressRepository
    from src.addresses.utils import build_studio_dict
    from src.database import AsyncSessionLocal
    from src.exceptions import NotFoundException

    async with AsyncSessionLocal() as session:
        repository = AddressRepository(session)
        address = await repository.find_by_slug_with_relations(address_slug)

        if not address:
            raise NotFoundException(f"Address with slug '{address_slug}' not found")

        # Build standardized studio dict with is_complete calculation
        stripe_cache = {}
        addr_dict = build_studio_dict(
            address,
            include_is_complete=True,
            include_payment_status=False,
            stripe_cache=stripe_cache
        )

        # Ensure latitude/longitude are strings for this endpoint (Laravel compatibility)
        if addr_dict.get("latitude") is not None:
            addr_dict["latitude"] = str(addr_dict["latitude"])
        if addr_dict.get("longitude") is not None:
            addr_dict["longitude"] = str(addr_dict["longitude"])

        return addr_dict


# Laravel-compatible operating hours endpoints
@address_router.get(
    "/operating-hours",
    summary="Get operating hours (Laravel-compatible)",
    description="Laravel-compatible endpoint to retrieve operating hours for an address using query parameter.",
)
async def get_operating_hours_laravel(
    address_id: Annotated[int, Query(description="Address ID")],
    service: Annotated[OperatingHoursService, Depends(get_operating_hours_service)],
):
    """
    Get operating hours for an address (Laravel-compatible route).

    This endpoint matches Laravel's URL pattern: GET /api/address/operating-hours?address_id=13
    """
    operating_hours = await service.get_operating_hours_by_address(address_id)
    hours_data = [OperatingHourResponse.model_validate(hour).model_dump() for hour in operating_hours]

    # Return Laravel-compatible format with data wrapper
    return {
        "success": True,
        "data": hours_data,
        "message": "Operating hours retrieved successfully",
        "code": 200
    }


@address_router.post(
    "/operating-hours",
    status_code=status.HTTP_201_CREATED,
    summary="Set operating hours (Laravel-compatible)",
    description="Laravel-compatible endpoint to set operating hours for an address.",
)
async def set_operating_hours_laravel(
    data: dict,
    service: Annotated[OperatingHoursService, Depends(get_operating_hours_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Set operating hours for an address (Laravel-compatible route).

    Handles three modes:
    - Mode 1 (24/7): Only requires mode_id and address_id
    - Mode 2 (Fixed): Requires mode_id, address_id, open_time, close_time
    - Mode 3 (Variable): Requires mode_id, address_id, and hours array
    """
    from src.addresses.models import OperatingHour
    from datetime import time as time_type

    # Convert address_id and mode_id to integers (they come as strings from frontend)
    address_id = int(data.get("address_id")) if data.get("address_id") else None
    mode_id = int(data.get("mode_id")) if data.get("mode_id") else None

    if not address_id or not mode_id:
        from src.exceptions import ConflictException
        raise ConflictException("address_id and mode_id are required")

    # Delete existing operating hours for this address
    await service.delete_operating_hours_by_address(address_id)

    created_hours = []

    if mode_id == 1:
        # Mode 1: 24/7 - Create one record for Sunday (day 0)
        operating_hour = OperatingHour(
            address_id=address_id,
            mode_id=mode_id,
            day_of_week=0,
            open_time=time_type(0, 0, 0),
            close_time=time_type(23, 59, 59),
            is_closed=False,
        )
        created = await service._repository.create_operating_hour(operating_hour)
        created_hours.append(created)

    elif mode_id == 2:
        # Mode 2: Fixed hours - Same hours every day (one record for Monday, day 1)
        open_time_str = data.get("open_time")
        close_time_str = data.get("close_time")

        if not open_time_str or not close_time_str:
            from src.exceptions import ConflictException
            raise ConflictException("open_time and close_time are required for mode 2")

        # Parse time strings (format: "HH:MM" or "HH:MM:SS")
        open_parts = open_time_str.split(":")
        close_parts = close_time_str.split(":")

        open_time = time_type(int(open_parts[0]), int(open_parts[1]))
        close_time = time_type(int(close_parts[0]), int(close_parts[1]))

        operating_hour = OperatingHour(
            address_id=address_id,
            mode_id=mode_id,
            day_of_week=1,  # Monday
            open_time=open_time,
            close_time=close_time,
            is_closed=False,
        )
        created = await service._repository.create_operating_hour(operating_hour)
        created_hours.append(created)

    elif mode_id == 3:
        # Mode 3: Variable hours - Different hours for each day
        hours = data.get("hours", [])

        if not hours:
            from src.exceptions import ConflictException
            raise ConflictException("hours array is required for mode 3")

        for hour_data in hours:
            day_of_week = int(hour_data.get("day_of_week")) if hour_data.get("day_of_week") is not None else None
            is_closed = hour_data.get("is_closed", False)

            if is_closed:
                # Create a closed day entry
                operating_hour = OperatingHour(
                    address_id=address_id,
                    mode_id=mode_id,
                    day_of_week=day_of_week,
                    open_time=None,
                    close_time=None,
                    is_closed=True,
                )
            else:
                open_time_str = hour_data.get("open_time")
                close_time_str = hour_data.get("close_time")

                if not open_time_str or not close_time_str:
                    continue

                open_parts = open_time_str.split(":")
                close_parts = close_time_str.split(":")

                open_time = time_type(int(open_parts[0]), int(open_parts[1]))
                close_time = time_type(int(close_parts[0]), int(close_parts[1]))

                operating_hour = OperatingHour(
                    address_id=address_id,
                    mode_id=mode_id,
                    day_of_week=day_of_week,
                    open_time=open_time,
                    close_time=close_time,
                    is_closed=False,
                )

            created = await service._repository.create_operating_hour(operating_hour)
            created_hours.append(created)

    # Return Laravel-compatible format
    hours_data = [OperatingHourResponse.model_validate(hour).model_dump() for hour in created_hours]

    return {
        "success": True,
        "data": hours_data,
        "message": "Operating hours set successfully",
        "code": 201
    }


# Laravel-compatible badges endpoints
@address_router.post(
    "/{address_id}/badge",
    summary="Toggle badge for address (Laravel-compatible)",
    description="Laravel-compatible endpoint to toggle a badge for an address.",
)
async def toggle_badge_laravel(
    address_id: int,
    data: dict,
    service: Annotated[AddressService, Depends(get_address_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Toggle a badge for an address (Laravel-compatible route).

    This endpoint matches Laravel's URL pattern: POST /api/address/{address_id}/badge
    If badge is already assigned, it removes it. Otherwise, it adds it.
    """
    badge_id = int(data.get("badge_id"))

    # Get the address with badges
    address = await service.get_address(address_id)

    # Check if badge is already assigned
    current_badge_ids = [badge.id for badge in address.badges]

    if badge_id in current_badge_ids:
        # Remove the badge
        current_badge_ids.remove(badge_id)
    else:
        # Add the badge
        current_badge_ids.append(badge_id)

    # Update badges
    badges = await service.add_badges(address_id, current_badge_ids)

    # Return Laravel-compatible format with just the taken badge IDs
    return {
        "success": True,
        "data": current_badge_ids,
        "message": "Badge updated successfully",
        "code": 200
    }


@address_router.get(
    "/{address_id}/badges",
    summary="Get all available badges (Laravel-compatible)",
    description="Laravel-compatible endpoint to retrieve all available badges for an address.",
)
async def get_all_badges_laravel(
    address_id: int,
    service: Annotated[AddressService, Depends(get_address_service)],
):
    """
    Get all available badges (Laravel-compatible route).

    This endpoint matches Laravel's URL pattern: GET /api/address/{address_id}/badges
    Returns all badges in the system, not just the ones assigned to this address.
    """
    from src.addresses.models import Badge
    from sqlalchemy import select
    from src.database import AsyncSessionLocal
    from src.gcs_utils import get_public_url

    async with AsyncSessionLocal() as session:
        # Get all badges from the database
        stmt = select(Badge).order_by(Badge.id)
        result = await session.execute(stmt)
        badges = list(result.scalars().all())

        # Get the address to retrieve taken badges
        address = await service.get_address(address_id)

        badges_data = []
        taken_badge_ids = [badge.id for badge in address.badges]

        for badge in badges:
            badge_dict = BadgeResponse.model_validate(badge).model_dump()
            # Convert GCS path to full public URL (no credentials needed)
            if badge.image:
                badge_dict["image"] = get_public_url(badge.image)
            badges_data.append(badge_dict)

        # Return Laravel-compatible format with all_badges and taken_badges
        return {
            "success": True,
            "data": {
                "all_badges": badges_data,
                "taken_badges": taken_badge_ids
            },
            "message": "Badges retrieved successfully",
            "code": 200
        }


# Laravel-compatible equipment-type endpoint
@address_router.get(
    "/equipment-type",
    summary="Get all equipment types (Laravel-compatible)",
    description="Laravel-compatible endpoint to retrieve all equipment types.",
)
async def get_equipment_types_laravel(
    service: Annotated[AddressService, Depends(get_address_service)],
):
    """
    Get all equipment types (Laravel-compatible route).

    This endpoint matches Laravel's URL pattern: GET /api/address/equipment-type
    """
    equipment_types = await service.get_equipment_types()
    equipment_types_data = [EquipmentTypeResponse.model_validate(et).model_dump() for et in equipment_types]

    # Return Laravel-compatible format
    return {
        "success": True,
        "data": equipment_types_data,
        "message": "Equipment types retrieved successfully",
        "code": 200
    }


# Laravel-compatible equipment endpoint
@address_router.get(
    "/{address_id}/equipment",
    summary="Get equipment for an address (Laravel-compatible)",
    description="Laravel-compatible endpoint to retrieve equipment for a specific address.",
)
async def get_address_equipment_laravel(
    address_id: int,
    service: Annotated[AddressService, Depends(get_address_service)],
):
    """
    Get equipment for an address (Laravel-compatible route).

    This endpoint matches Laravel's URL pattern: GET /api/address/{address_id}/equipment
    """
    equipment = await service.get_address_equipment(address_id)
    equipment_data = [EquipmentWithTypeResponse.model_validate(eq).model_dump() for eq in equipment]

    # Return Laravel-compatible format
    return {
        "success": True,
        "data": equipment_data,
        "message": "Equipment retrieved successfully",
        "code": 200
    }


# Map router - for map view endpoints
map_router = APIRouter(prefix="/map", tags=["Map"])


@map_router.get(
    "/studios",
    response_model=list[MapStudioResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all studios for map view",
    description="Returns all complete studios for displaying on map. Only shows studios with operating hours and payment gateway configured.",
)
async def get_map_studios(
    service: Annotated[AddressService, Depends(get_address_service)],
) -> list[MapStudioResponse]:
    """
    Get all studios/addresses for map display.

    Matches Laravel: GET /api/map/studios

    Only returns studios where:
    - Operating hours are configured
    - Payment gateway (Stripe/Square) has payouts enabled

    Returns studios with:
    - Basic address info (location, name, etc.)
    - Badges/amenities
    - Rooms with photos and prices
    - Company info with logo and user_id
    - Operating hours
    - is_complete status

    Used for displaying studios on interactive map.
    """
    from src.addresses.utils import build_studio_dict, should_show_in_public_search

    studios = await service.get_all_studios_for_map()

    # Cache Stripe account statuses
    stripe_cache = {}

    # Filter and convert to response format
    response_studios = []
    for studio in studios:
        # FILTER: Only include complete studios for public map view
        if not should_show_in_public_search(studio, stripe_cache):
            continue

        # Build standardized studio dict
        studio_dict = build_studio_dict(
            studio,
            include_is_complete=True,
            include_payment_status=False,
            stripe_cache=stripe_cache
        )

        # Map view needs specific additional fields
        studio_dict["name"] = studio.name

        response_studios.append(MapStudioResponse.model_validate(studio_dict))

    return response_studios
