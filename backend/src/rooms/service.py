"""
Room service - Business logic layer for rooms, prices, and photos.
"""
from decimal import Decimal
from src.rooms.models import Room, RoomPrice, RoomPhoto
from src.rooms.repository import RoomRepository
from src.rooms.schemas import (
    RoomCreate,
    RoomUpdate,
    RoomPriceCreate,
    RoomPriceUpdate,
    RoomPhotoCreate,
    RoomPhotoUpdate,
)
from src.exceptions import NotFoundException


class RoomService:
    """Service for room business operations."""

    def __init__(self, repository: RoomRepository):
        self._repository = repository

    # Room operations

    async def create_room(self, data: RoomCreate) -> Room:
        """
        Create a new room.

        Business rules:
        - Room must belong to an address
        """
        room = Room(
            name=data.name,
            address_id=data.address_id,
        )
        return await self._repository.create(room)

    async def get_room(self, room_id: int) -> Room:
        """Get room by ID or raise exception."""
        room = await self._repository.find_by_id(room_id)
        if not room:
            raise NotFoundException(f"Room with ID {room_id} not found")
        return room

    async def get_rooms_by_address(self, address_id: int) -> list[Room]:
        """Get all rooms for an address."""
        return await self._repository.find_by_address(address_id)

    async def update_room(self, room_id: int, data: RoomUpdate) -> Room:
        """Update room details."""
        room = await self.get_room(room_id)

        if data.name is not None:
            room.name = data.name

        return await self._repository.update(room)

    async def delete_room(self, room_id: int) -> None:
        """Delete a room."""
        room = await self.get_room(room_id)
        await self._repository.delete(room)

    # Room Price operations

    async def create_price(self, room_id: int, data: RoomPriceCreate) -> RoomPrice:
        """
        Create a new price tier for a room.

        Business rules:
        - price_per_hour is calculated from total_price / hours
        - Prices start as disabled by default unless specified
        """
        # Verify room exists
        await self.get_room(room_id)

        # Calculate price per hour
        price_per_hour = data.total_price / Decimal(data.hours)

        price = RoomPrice(
            room_id=room_id,
            hours=data.hours,
            total_price=data.total_price,
            price_per_hour=price_per_hour,
            is_enabled=data.is_enabled,
        )
        return await self._repository.create_price(price)

    async def update_price(self, price_id: int, data: RoomPriceUpdate) -> RoomPrice:
        """
        Update a price tier.

        Business rules:
        - If hours or total_price changes, recalculate price_per_hour
        """
        price = await self._repository.find_price_by_id(price_id)
        if not price:
            raise NotFoundException(f"Room price with ID {price_id} not found")

        # Update fields
        if data.hours is not None:
            price.hours = data.hours
        if data.total_price is not None:
            price.total_price = data.total_price
        if data.is_enabled is not None:
            price.is_enabled = data.is_enabled

        # Recalculate price_per_hour if hours or total_price changed
        if data.hours is not None or data.total_price is not None:
            price.price_per_hour = price.total_price / Decimal(price.hours)

        return await self._repository.update_price(price)

    async def get_prices(self, room_id: int) -> list[RoomPrice]:
        """Get all price tiers for a room."""
        # Verify room exists
        await self.get_room(room_id)
        return await self._repository.find_prices_by_room(room_id)

    async def delete_price(self, price_id: int, room_id: int) -> None:
        """
        Delete a price tier.

        Args:
            price_id: The price ID to delete
            room_id: The room ID (for validation)

        Raises:
            NotFoundException: If price not found or doesn't belong to room
        """
        price = await self._repository.find_price_by_id(price_id)
        if not price:
            raise NotFoundException(f"Room price with ID {price_id} not found")
        if price.room_id != room_id:
            raise NotFoundException(f"Price {price_id} does not belong to room {room_id}")

        await self._repository.delete_price(price)

    # Room Photo operations

    async def create_photo(self, room_id: int, data: RoomPhotoCreate) -> RoomPhoto:
        """
        Add a photo to a room.

        Business rules:
        - If no index specified, append to end
        """
        # Verify room exists
        await self.get_room(room_id)

        # If no index provided, get max index + 1
        if data.index is None:
            existing_photos = await self._repository.find_photos_by_room(room_id)
            index = max([p.index for p in existing_photos], default=-1) + 1
        else:
            index = data.index

        photo = RoomPhoto(
            room_id=room_id,
            photo_path=data.photo_path,
            index=index,
        )
        return await self._repository.create_photo(photo)

    async def update_photo_index(self, photo_id: int, new_index: int) -> RoomPhoto:
        """
        Update a photo's order index.

        Business rules:
        - Photo can be reordered within the room's photos
        """
        photo = await self._repository.find_photo_by_id(photo_id)
        if not photo:
            raise NotFoundException(f"Room photo with ID {photo_id} not found")

        photo.index = new_index
        return await self._repository.update_photo(photo)

    async def get_photos(self, room_id: int) -> list[RoomPhoto]:
        """Get all photos for a room, ordered by index."""
        # Verify room exists
        await self.get_room(room_id)
        return await self._repository.find_photos_by_room(room_id)

    async def delete_photo(self, photo_id: int) -> None:
        """Delete a photo."""
        photo = await self._repository.find_photo_by_id(photo_id)
        if not photo:
            raise NotFoundException(f"Room photo with ID {photo_id} not found")

        await self._repository.delete_photo(photo)
