"""
Operating Hours router - API endpoint definitions.
Handles HTTP requests for operating hours and studio closures.
"""
from typing import Annotated, Optional
from datetime import date
from fastapi import APIRouter, Depends, status, Query

from src.operating_hours.dependencies import get_operating_hours_service
from src.operating_hours.schemas import (
    OperatingHourCreate,
    OperatingHourResponse,
    OperatingHourUpdate,
    BulkOperatingHoursCreate,
    StudioClosureCreate,
    StudioClosureResponse,
    StudioClosureUpdate,
)
from src.operating_hours.service import OperatingHoursService
from src.auth.users import current_active_user
from src.auth.models_fastapi_users import User


router = APIRouter(prefix="/operating-hours", tags=["Operating Hours"])


# Operating Hours Endpoints

@router.post(
    "/address/{address_id}",
    response_model=OperatingHourResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create operating hour for an address",
    description="Create a single operating hour entry for a specific day of the week.",
)
async def create_operating_hour(
    address_id: int,
    data: OperatingHourCreate,
    service: Annotated[OperatingHoursService, Depends(get_operating_hours_service)],
    current_user: Annotated[User, Depends(current_active_user)],
) -> OperatingHourResponse:
    """
    Create a new operating hour for an address.

    **Business Rules:**
    - Only one operating hour per day of week per address
    - For OPEN mode, both start_time and end_time are required
    - For CLOSED mode, start_time and end_time must be null
    """
    operating_hour = await service.create_operating_hour(address_id, data)
    return OperatingHourResponse.model_validate(operating_hour)


@router.post(
    "/address/{address_id}/bulk",
    response_model=list[OperatingHourResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Bulk set operating hours",
    description="Replace all operating hours for an address with a new set of hours.",
)
async def bulk_create_operating_hours(
    address_id: int,
    data: BulkOperatingHoursCreate,
    service: Annotated[OperatingHoursService, Depends(get_operating_hours_service)],
    current_user: Annotated[User, Depends(current_active_user)],
) -> list[OperatingHourResponse]:
    """
    Bulk create operating hours for an address.

    **Business Rules:**
    - Replaces ALL existing operating hours
    - Can provide 1-7 days
    - Each day can only be specified once
    """
    operating_hours = await service.bulk_create_operating_hours(address_id, data)
    return [OperatingHourResponse.model_validate(hour) for hour in operating_hours]


@router.get(
    "/address/{address_id}",
    response_model=list[OperatingHourResponse],
    summary="Get operating hours for an address",
    description="Retrieve all operating hours for a specific address, ordered by day of week.",
)
async def get_operating_hours_by_address(
    address_id: int,
    service: Annotated[OperatingHoursService, Depends(get_operating_hours_service)],
) -> list[OperatingHourResponse]:
    """Retrieve all operating hours for an address."""
    operating_hours = await service.get_operating_hours_by_address(address_id)
    return [OperatingHourResponse.model_validate(hour) for hour in operating_hours]


@router.get(
    "/{hour_id}",
    response_model=OperatingHourResponse,
    summary="Get operating hour by ID",
    description="Retrieve a specific operating hour entry by its ID.",
)
async def get_operating_hour(
    hour_id: int,
    service: Annotated[OperatingHoursService, Depends(get_operating_hours_service)],
) -> OperatingHourResponse:
    """Retrieve operating hour by ID."""
    operating_hour = await service.get_operating_hour(hour_id)
    return OperatingHourResponse.model_validate(operating_hour)


@router.patch(
    "/{hour_id}",
    response_model=OperatingHourResponse,
    summary="Update operating hour",
    description="Update an existing operating hour entry.",
)
async def update_operating_hour(
    hour_id: int,
    data: OperatingHourUpdate,
    service: Annotated[OperatingHoursService, Depends(get_operating_hours_service)],
    current_user: Annotated[User, Depends(current_active_user)],
) -> OperatingHourResponse:
    """Update existing operating hour."""
    operating_hour = await service.update_operating_hour(hour_id, data)
    return OperatingHourResponse.model_validate(operating_hour)


@router.delete(
    "/{hour_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete operating hour",
    description="Permanently remove an operating hour entry.",
)
async def delete_operating_hour(
    hour_id: int,
    service: Annotated[OperatingHoursService, Depends(get_operating_hours_service)],
    current_user: Annotated[User, Depends(current_active_user)],
) -> None:
    """Delete operating hour."""
    await service.delete_operating_hour(hour_id)


# Studio Closure Endpoints

@router.post(
    "/closures/address/{address_id}",
    response_model=StudioClosureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create studio closure",
    description="Create a closure period for a studio (holidays, maintenance, etc.).",
)
async def create_studio_closure(
    address_id: int,
    data: StudioClosureCreate,
    service: Annotated[OperatingHoursService, Depends(get_operating_hours_service)],
    current_user: Annotated[User, Depends(current_active_user)],
) -> StudioClosureResponse:
    """
    Create a new studio closure period.

    **Business Rules:**
    - end_date must be >= start_date
    - Can overlap with existing closures (warning only)
    - Optional reason text
    """
    closure = await service.create_studio_closure(address_id, data)
    return StudioClosureResponse.model_validate(closure)


@router.get(
    "/closures/address/{address_id}",
    response_model=list[StudioClosureResponse],
    summary="Get studio closures",
    description="Retrieve all closure periods for a studio.",
)
async def get_studio_closures_by_address(
    address_id: int,
    service: Annotated[OperatingHoursService, Depends(get_operating_hours_service)],
) -> list[StudioClosureResponse]:
    """Retrieve all studio closures for an address."""
    closures = await service.get_studio_closures_by_address(address_id)
    return [StudioClosureResponse.model_validate(closure) for closure in closures]


@router.get(
    "/closures/address/{address_id}/active",
    response_model=list[StudioClosureResponse],
    summary="Get active closures",
    description="Retrieve closures that are active on a specific date (defaults to today).",
)
async def get_active_closures(
    address_id: int,
    service: Annotated[OperatingHoursService, Depends(get_operating_hours_service)],
    check_date: Optional[date] = Query(None, description="Date to check (defaults to today)"),
) -> list[StudioClosureResponse]:
    """
    Get active closures for an address on a specific date.

    If check_date is not provided, defaults to today.
    """
    closures = await service.get_active_closures(address_id, check_date)
    return [StudioClosureResponse.model_validate(closure) for closure in closures]


@router.get(
    "/closures/{closure_id}",
    response_model=StudioClosureResponse,
    summary="Get studio closure by ID",
    description="Retrieve a specific closure period by its ID.",
)
async def get_studio_closure(
    closure_id: int,
    service: Annotated[OperatingHoursService, Depends(get_operating_hours_service)],
) -> StudioClosureResponse:
    """Retrieve studio closure by ID."""
    closure = await service.get_studio_closure(closure_id)
    return StudioClosureResponse.model_validate(closure)


@router.patch(
    "/closures/{closure_id}",
    response_model=StudioClosureResponse,
    summary="Update studio closure",
    description="Update an existing studio closure period.",
)
async def update_studio_closure(
    closure_id: int,
    data: StudioClosureUpdate,
    service: Annotated[OperatingHoursService, Depends(get_operating_hours_service)],
    current_user: Annotated[User, Depends(current_active_user)],
) -> StudioClosureResponse:
    """Update existing studio closure."""
    closure = await service.update_studio_closure(closure_id, data)
    return StudioClosureResponse.model_validate(closure)


@router.delete(
    "/closures/{closure_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete studio closure",
    description="Permanently remove a studio closure period.",
)
async def delete_studio_closure(
    closure_id: int,
    service: Annotated[OperatingHoursService, Depends(get_operating_hours_service)],
    current_user: Annotated[User, Depends(current_active_user)],
) -> None:
    """Delete studio closure."""
    await service.delete_studio_closure(closure_id)
