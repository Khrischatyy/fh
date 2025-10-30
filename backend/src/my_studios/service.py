"""
My Studios service - Business logic layer.
"""
from typing import Optional

from src.my_studios.repository import MyStudiosRepository
from src.addresses.models import Address
from src.geographic.models import City


class MyStudiosService:
    """Service for managing user's studios."""

    def __init__(self, repository: MyStudiosRepository):
        self._repository = repository

    async def get_user_cities(self, user_id: int) -> list[City]:
        """
        Get all unique cities where the user has studios.

        Args:
            user_id: The user ID

        Returns:
            List of City objects
        """
        return await self._repository.get_user_cities(user_id)

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
        return await self._repository.get_user_studios(user_id, city_id)
