"""
Geographic repository - Data access layer.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.geographic.models import Country, City


class GeographicRepository:
    """Repository for geographic data operations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all_countries(self) -> list[Country]:
        """Retrieve all countries."""
        stmt = select(Country).order_by(Country.name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_country_by_id(self, country_id: int) -> Optional[Country]:
        """Retrieve country by ID."""
        stmt = select(Country).where(Country.id == country_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_cities_by_country(self, country_id: int) -> list[City]:
        """Retrieve all cities for a country."""
        stmt = (
            select(City)
            .where(City.country_id == country_id)
            .order_by(City.name)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_city_by_id(self, city_id: int) -> Optional[City]:
        """Retrieve city by ID."""
        stmt = select(City).where(City.id == city_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
