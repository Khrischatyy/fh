"""
Operating Hours repository - Data access layer.
Handles all database operations for OperatingHour and StudioClosure entities.
"""
from typing import Optional
from datetime import date
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.addresses.models import OperatingHour, StudioClosure, Address


class OperatingHoursRepository:
    """Repository for OperatingHour and StudioClosure database operations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    # OperatingHour operations

    async def create_operating_hour(self, operating_hour: OperatingHour) -> OperatingHour:
        """Persist a new operating hour to the database."""
        self._session.add(operating_hour)
        await self._session.flush()
        await self._session.refresh(operating_hour)
        return operating_hour

    async def find_operating_hour_by_id(self, hour_id: int) -> Optional[OperatingHour]:
        """Retrieve an operating hour by ID."""
        stmt = select(OperatingHour).where(OperatingHour.id == hour_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_operating_hours_by_address(self, address_id: int) -> list[OperatingHour]:
        """Retrieve all operating hours for an address, ordered by day of week."""
        stmt = (
            select(OperatingHour)
            .where(OperatingHour.address_id == address_id)
            .order_by(OperatingHour.day_of_week)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_operating_hour_by_address_and_day(
        self, address_id: int, day_of_week: int
    ) -> Optional[OperatingHour]:
        """Find an operating hour for a specific address and day."""
        stmt = select(OperatingHour).where(
            and_(
                OperatingHour.address_id == address_id,
                OperatingHour.day_of_week == day_of_week,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_operating_hour(self, operating_hour: OperatingHour) -> OperatingHour:
        """Update an existing operating hour."""
        await self._session.flush()
        await self._session.refresh(operating_hour)
        return operating_hour

    async def delete_operating_hour(self, operating_hour: OperatingHour) -> None:
        """Remove an operating hour from the database."""
        await self._session.delete(operating_hour)
        await self._session.flush()

    async def delete_operating_hours_by_address(self, address_id: int) -> None:
        """Delete all operating hours for an address."""
        stmt = select(OperatingHour).where(OperatingHour.address_id == address_id)
        result = await self._session.execute(stmt)
        hours = result.scalars().all()
        for hour in hours:
            await self._session.delete(hour)
        await self._session.flush()

    # StudioClosure operations

    async def create_studio_closure(self, closure: StudioClosure) -> StudioClosure:
        """Persist a new studio closure to the database."""
        self._session.add(closure)
        await self._session.flush()
        await self._session.refresh(closure)
        return closure

    async def find_studio_closure_by_id(self, closure_id: int) -> Optional[StudioClosure]:
        """Retrieve a studio closure by ID."""
        stmt = select(StudioClosure).where(StudioClosure.id == closure_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_studio_closures_by_address(self, address_id: int) -> list[StudioClosure]:
        """Retrieve all studio closures for an address, ordered by start date."""
        stmt = (
            select(StudioClosure)
            .where(StudioClosure.address_id == address_id)
            .order_by(StudioClosure.start_date.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_active_closures_by_address(
        self, address_id: int, check_date: date
    ) -> list[StudioClosure]:
        """Find all closures that are active on a specific date."""
        stmt = select(StudioClosure).where(
            and_(
                StudioClosure.address_id == address_id,
                StudioClosure.start_date <= check_date,
                StudioClosure.end_date >= check_date,
            )
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_overlapping_closures(
        self, address_id: int, start_date: date, end_date: date, exclude_id: Optional[int] = None
    ) -> list[StudioClosure]:
        """Find closures that overlap with the given date range."""
        conditions = [
            StudioClosure.address_id == address_id,
            or_(
                # New closure starts during existing closure
                and_(
                    StudioClosure.start_date <= start_date,
                    StudioClosure.end_date >= start_date,
                ),
                # New closure ends during existing closure
                and_(
                    StudioClosure.start_date <= end_date,
                    StudioClosure.end_date >= end_date,
                ),
                # New closure completely contains existing closure
                and_(
                    StudioClosure.start_date >= start_date,
                    StudioClosure.end_date <= end_date,
                ),
            ),
        ]

        if exclude_id:
            conditions.append(StudioClosure.id != exclude_id)

        stmt = select(StudioClosure).where(and_(*conditions))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_studio_closure(self, closure: StudioClosure) -> StudioClosure:
        """Update an existing studio closure."""
        await self._session.flush()
        await self._session.refresh(closure)
        return closure

    async def delete_studio_closure(self, closure: StudioClosure) -> None:
        """Remove a studio closure from the database."""
        await self._session.delete(closure)
        await self._session.flush()

    # Address validation

    async def address_exists(self, address_id: int) -> bool:
        """Check if an address exists."""
        stmt = select(Address.id).where(Address.id == address_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
