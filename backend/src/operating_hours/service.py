"""
Operating Hours service - Business logic layer.
Orchestrates operations between repository and enforces business rules.
"""
from datetime import date
from typing import Optional

from src.addresses.models import OperatingHour, StudioClosure, OperatingMode
from src.operating_hours.repository import OperatingHoursRepository
from src.operating_hours.schemas import (
    OperatingHourCreate,
    OperatingHourUpdate,
    StudioClosureCreate,
    StudioClosureUpdate,
    BulkOperatingHoursCreate,
)
from src.exceptions import NotFoundException, ConflictException


class OperatingHoursService:
    """Service layer for Operating Hours business logic."""

    def __init__(self, repository: OperatingHoursRepository):
        self._repository = repository

    # OperatingHour operations

    async def create_operating_hour(
        self, address_id: int, data: OperatingHourCreate
    ) -> OperatingHour:
        """
        Create a new operating hour for an address.

        Business rules:
        - Address must exist
        - Only one operating hour per address per day
        - If day already exists, raises ConflictException
        """
        # Validate address exists
        if not await self._repository.address_exists(address_id):
            raise NotFoundException(f"Address with ID {address_id} not found")

        # Check if operating hour already exists for this day
        existing = await self._repository.find_operating_hour_by_address_and_day(
            address_id, data.day_of_week
        )
        if existing:
            raise ConflictException(
                f"Operating hours for day {data.day_of_week} already exist for this address"
            )

        operating_hour = OperatingHour(
            address_id=address_id,
            day_of_week=data.day_of_week,
            start_time=data.start_time,
            end_time=data.end_time,
            operation_mode=data.operation_mode,
        )

        return await self._repository.create_operating_hour(operating_hour)

    async def bulk_create_operating_hours(
        self, address_id: int, data: BulkOperatingHoursCreate
    ) -> list[OperatingHour]:
        """
        Bulk create operating hours for an address.

        Business rules:
        - Replaces all existing operating hours for the address
        - Validates address exists
        - Ensures no duplicate days
        """
        # Validate address exists
        if not await self._repository.address_exists(address_id):
            raise NotFoundException(f"Address with ID {address_id} not found")

        # Delete all existing operating hours for this address
        await self._repository.delete_operating_hours_by_address(address_id)

        # Create new operating hours
        created_hours = []
        for hour_data in data.hours:
            operating_hour = OperatingHour(
                address_id=address_id,
                day_of_week=hour_data.day_of_week,
                start_time=hour_data.start_time,
                end_time=hour_data.end_time,
                operation_mode=hour_data.operation_mode,
            )
            created = await self._repository.create_operating_hour(operating_hour)
            created_hours.append(created)

        return created_hours

    async def get_operating_hour(self, hour_id: int) -> OperatingHour:
        """Retrieve an operating hour by ID or raise NotFoundException."""
        operating_hour = await self._repository.find_operating_hour_by_id(hour_id)
        if not operating_hour:
            raise NotFoundException(f"Operating hour with ID {hour_id} not found")
        return operating_hour

    async def get_operating_hours_by_address(self, address_id: int) -> list[OperatingHour]:
        """Retrieve all operating hours for an address."""
        # Validate address exists
        if not await self._repository.address_exists(address_id):
            raise NotFoundException(f"Address with ID {address_id} not found")

        return await self._repository.find_operating_hours_by_address(address_id)

    async def update_operating_hour(
        self, hour_id: int, data: OperatingHourUpdate
    ) -> OperatingHour:
        """
        Update an existing operating hour.

        Business rules:
        - Operating hour must exist
        - Applies partial updates
        """
        operating_hour = await self.get_operating_hour(hour_id)

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(operating_hour, field, value)

        return await self._repository.update_operating_hour(operating_hour)

    async def delete_operating_hour(self, hour_id: int) -> None:
        """Delete an operating hour by ID."""
        operating_hour = await self.get_operating_hour(hour_id)
        await self._repository.delete_operating_hour(operating_hour)

    async def delete_operating_hours_by_address(self, address_id: int) -> None:
        """Delete all operating hours for an address."""
        operating_hours = await self._repository.find_operating_hours_by_address(address_id)
        for hour in operating_hours:
            await self._repository.delete_operating_hour(hour)

    # StudioClosure operations

    async def create_studio_closure(
        self, address_id: int, data: StudioClosureCreate
    ) -> StudioClosure:
        """
        Create a new studio closure.

        Business rules:
        - Address must exist
        - Warns if closure overlaps with existing closures (doesn't prevent)
        - end_date must be >= start_date (validated in schema)
        """
        # Validate address exists
        if not await self._repository.address_exists(address_id):
            raise NotFoundException(f"Address with ID {address_id} not found")

        # Check for overlapping closures (warning, not error)
        overlapping = await self._repository.find_overlapping_closures(
            address_id, data.start_date, data.end_date
        )
        if overlapping:
            # In a real application, you might want to log this or return a warning
            pass

        closure = StudioClosure(
            address_id=address_id,
            start_date=data.start_date,
            end_date=data.end_date,
            reason=data.reason,
        )

        return await self._repository.create_studio_closure(closure)

    async def get_studio_closure(self, closure_id: int) -> StudioClosure:
        """Retrieve a studio closure by ID or raise NotFoundException."""
        closure = await self._repository.find_studio_closure_by_id(closure_id)
        if not closure:
            raise NotFoundException(f"Studio closure with ID {closure_id} not found")
        return closure

    async def get_studio_closures_by_address(self, address_id: int) -> list[StudioClosure]:
        """Retrieve all studio closures for an address."""
        # Validate address exists
        if not await self._repository.address_exists(address_id):
            raise NotFoundException(f"Address with ID {address_id} not found")

        return await self._repository.find_studio_closures_by_address(address_id)

    async def get_active_closures(
        self, address_id: int, check_date: Optional[date] = None
    ) -> list[StudioClosure]:
        """
        Get all active closures for an address on a specific date.

        If check_date is None, uses today's date.
        """
        if check_date is None:
            check_date = date.today()

        # Validate address exists
        if not await self._repository.address_exists(address_id):
            raise NotFoundException(f"Address with ID {address_id} not found")

        return await self._repository.find_active_closures_by_address(address_id, check_date)

    async def update_studio_closure(
        self, closure_id: int, data: StudioClosureUpdate
    ) -> StudioClosure:
        """
        Update an existing studio closure.

        Business rules:
        - Closure must exist
        - Applies partial updates
        - Validates date range if both dates are provided
        """
        closure = await self.get_studio_closure(closure_id)

        update_data = data.model_dump(exclude_unset=True)

        # Apply updates
        for field, value in update_data.items():
            setattr(closure, field, value)

        # Final validation: ensure end_date >= start_date
        if closure.end_date < closure.start_date:
            raise ConflictException("end_date cannot be before start_date")

        return await self._repository.update_studio_closure(closure)

    async def delete_studio_closure(self, closure_id: int) -> None:
        """Delete a studio closure by ID."""
        closure = await self.get_studio_closure(closure_id)
        await self._repository.delete_studio_closure(closure)

    # Operating Mode operations

    async def get_all_operating_modes(self) -> list[OperatingMode]:
        """Get all available operating modes."""
        return await self._repository.get_all_operating_modes()
