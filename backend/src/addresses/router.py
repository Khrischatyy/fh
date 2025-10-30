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

    Laravel compatible: GET /api/address/studio/{address_slug}

    Returns:
        Complete address with all relationships: badges, rooms, photos, prices,
        company, operating hours, equipment

    Raises:
        NotFoundException: If address not found
    """
    from src.addresses.repository import AddressRepository
    from src.database import AsyncSessionLocal
    from src.exceptions import NotFoundException

    async with AsyncSessionLocal() as session:
        repository = AddressRepository(session)
        address = await repository.find_by_slug_with_relations(address_slug)

        if not address:
            raise NotFoundException(f"Address with slug '{address_slug}' not found")

        # Build address dict with all relationships
        addr_dict = {
            "id": address.id,
            "slug": address.slug,
            "street": address.street,
            "latitude": str(address.latitude) if address.latitude else None,
            "longitude": str(address.longitude) if address.longitude else None,
            "timezone": address.timezone,
            "rating": address.rating,
            "city_id": address.city_id,
            "company_id": address.company_id,
            "available_balance": float(address.available_balance),
            "created_at": address.created_at.isoformat(),
            "updated_at": address.updated_at.isoformat(),
            "badges": [{"id": b.id, "name": b.name, "image": b.image, "description": b.description} for b in address.badges],
            "rooms": [
                {
                    "id": r.id,
                    "name": r.name,
                    "photos": [{"id": p.id, "path": p.path, "index": p.index} for p in r.photos],
                    "prices": [
                        {
                            "id": pr.id,
                            "hours": pr.hours,
                            "total_price": float(pr.total_price),
                            "price_per_hour": float(pr.price_per_hour),
                            "is_enabled": pr.is_enabled
                        }
                        for pr in r.prices if pr.is_enabled  # Only enabled prices like Laravel
                    ],
                }
                for r in address.rooms
            ],
            "operating_hours": [
                {
                    "id": oh.id,
                    "day_of_week": oh.day_of_week,
                    "open_time": oh.open_time.isoformat() if oh.open_time else None,
                    "close_time": oh.close_time.isoformat() if oh.close_time else None,
                    "is_closed": oh.is_closed,
                    "mode_id": oh.mode_id,
                }
                for oh in address.operating_hours
            ],
            # Frontend expects "equipments" (plural)
            "equipments": [],
        }

        # Add flattened prices and photos (matching Laravel getPricesAttribute and getPhotosAttribute)
        all_prices = []
        all_photos = []
        for room in address.rooms:
            # Only add enabled prices
            all_prices.extend([
                {
                    "id": pr.id,
                    "hours": pr.hours,
                    "total_price": float(pr.total_price),
                    "price_per_hour": float(pr.price_per_hour),
                    "is_enabled": pr.is_enabled
                }
                for pr in room.prices if pr.is_enabled
            ])
            all_photos.extend([
                {
                    "id": p.id,
                    "path": p.path,
                    "index": p.index
                }
                for p in room.photos
            ])

        addr_dict["prices"] = all_prices
        addr_dict["photos"] = all_photos

        # Calculate is_complete (matching Laravel getIsCompleteAttribute)
        has_operating_hours = len(address.operating_hours) > 0
        has_stripe_gateway = False
        has_square_gateway = False

        if address.company and address.company.admin_companies:
            for admin_comp in address.company.admin_companies:
                if admin_comp.admin:
                    has_stripe_gateway = admin_comp.admin.stripe_account_id is not None
                    has_square_gateway = admin_comp.admin.payment_gateway == 'square'
                    break

        addr_dict["is_complete"] = has_operating_hours and (has_stripe_gateway or has_square_gateway)

        # Add company info
        if address.company:
            addr_dict["company"] = {
                "id": address.company.id,
                "name": address.company.name,
                "slug": address.company.slug,
                "logo": address.company.logo,
                # logo_url intentionally omitted - will be added when S3 integration is ready
            }

            # Add user_id from admin_company
            if address.company.admin_companies:
                for admin_comp in address.company.admin_companies:
                    if admin_comp.admin:
                        addr_dict["company"]["user_id"] = admin_comp.admin.id
                        break

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

    async with AsyncSessionLocal() as session:
        # Get all badges from the database
        stmt = select(Badge).order_by(Badge.id)
        result = await session.execute(stmt)
        badges = list(result.scalars().all())

        badges_data = [BadgeResponse.model_validate(badge).model_dump() for badge in badges]

        # Return Laravel-compatible format
        return {
            "success": True,
            "data": badges_data,
            "message": "Badges retrieved successfully",
            "code": 200
        }
