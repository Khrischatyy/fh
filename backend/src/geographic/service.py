"""
Geographic service - Business logic layer.
"""
from src.geographic.models import Country, City
from src.geographic.repository import GeographicRepository
from src.exceptions import NotFoundException


class GeographicService:
    """Service for geographic operations."""

    def __init__(self, repository: GeographicRepository):
        self._repository = repository

    async def get_all_countries(self) -> list[Country]:
        """Retrieve all countries."""
        return await self._repository.get_all_countries()

    async def get_country(self, country_id: int) -> Country:
        """Get country by ID or raise exception."""
        country = await self._repository.get_country_by_id(country_id)
        if not country:
            raise NotFoundException(f"Country with ID {country_id} not found")
        return country

    async def get_cities_by_country(self, country_id: int) -> list[City]:
        """
        Retrieve all cities for a country.
        Validates country exists first.
        """
        await self.get_country(country_id)  # Validate country exists
        return await self._repository.get_cities_by_country(country_id)

    async def get_city(self, city_id: int) -> City:
        """Get city by ID or raise exception."""
        city = await self._repository.get_city_by_id(city_id)
        if not city:
            raise NotFoundException(f"City with ID {city_id} not found")
        return city
