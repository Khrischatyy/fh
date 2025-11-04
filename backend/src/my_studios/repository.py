"""
My Studios repository - Database access layer.
"""
from typing import Optional
from sqlalchemy import select, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from src.addresses.models import Address
from src.companies.models import Company, AdminCompany
from src.geographic.models import City
from src.rooms.models import Room


class MyStudiosRepository:
    """Repository for user's studios operations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_user_cities(self, user_id: int) -> list[City]:
        """
        Get all unique cities where the user has studios.

        Args:
            user_id: The user ID

        Returns:
            List of City objects
        """
        # Query cities through: User -> AdminCompany -> Company -> Address -> City
        stmt = (
            select(City)
            .distinct()
            .join(Address, Address.city_id == City.id)
            .join(Company, Company.id == Address.company_id)
            .join(AdminCompany, AdminCompany.company_id == Company.id)
            .where(AdminCompany.admin_id == user_id)
            .order_by(City.name)
        )

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_studios(
        self,
        user_id: int,
        city_id: Optional[int] = None,
    ) -> list[Address]:
        """
        Get all studios/addresses for the user, optionally filtered by city.

        Args:
            user_id: The user ID
            city_id: Optional city ID to filter by

        Returns:
            List of Address objects with relationships loaded
        """
        # Query addresses through: User -> AdminCompany -> Company -> Address
        stmt = (
            select(Address)
            .join(Company, Company.id == Address.company_id)
            .join(AdminCompany, AdminCompany.company_id == Company.id)
            .where(AdminCompany.admin_id == user_id)
            .options(
                joinedload(Address.city),
                joinedload(Address.company).selectinload(Company.admin_companies).joinedload(AdminCompany.admin),
                selectinload(Address.operating_hours),
                selectinload(Address.badges),
                selectinload(Address.rooms).selectinload(Room.photos),
                selectinload(Address.rooms).selectinload(Room.prices),
            )
            .order_by(Address.id.desc())
        )

        # Apply city filter if provided
        if city_id is not None:
            stmt = stmt.where(Address.city_id == city_id)

        result = await self._session.execute(stmt)
        return list(result.unique().scalars().all())
