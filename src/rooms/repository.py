"""
Room repository - Data access layer for rooms, prices, and photos.
"""
from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.rooms.models import Room, RoomPrice, RoomPhoto


class RoomRepository:
    """Repository for Room entity database operations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    # Room CRUD

    async def create(self, room: Room) -> Room:
        """Persist a new room."""
        self._session.add(room)
        await self._session.flush()
        await self._session.refresh(room)
        return room

    async def find_by_id(self, room_id: int) -> Optional[Room]:
        """Retrieve room by ID with relationships."""
        stmt = (
            select(Room)
            .where(Room.id == room_id)
            .options(
                selectinload(Room.photos),
                selectinload(Room.prices),
                selectinload(Room.address),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_address(self, address_id: int) -> list[Room]:
        """Retrieve all rooms for an address."""
        stmt = (
            select(Room)
            .where(Room.address_id == address_id)
            .options(
                selectinload(Room.photos),
                selectinload(Room.prices),
            )
            .order_by(Room.name)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, room: Room) -> Room:
        """Update existing room."""
        await self._session.flush()
        await self._session.refresh(room)
        return room

    async def delete(self, room: Room) -> None:
        """Remove room from database."""
        await self._session.delete(room)
        await self._session.flush()

    # Room Price CRUD

    async def create_price(self, price: RoomPrice) -> RoomPrice:
        """Persist a new room price."""
        self._session.add(price)
        await self._session.flush()
        await self._session.refresh(price)
        return price

    async def find_price_by_id(self, price_id: int) -> Optional[RoomPrice]:
        """Retrieve price by ID."""
        stmt = select(RoomPrice).where(RoomPrice.id == price_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_prices_by_room(self, room_id: int) -> list[RoomPrice]:
        """Retrieve all prices for a room."""
        stmt = (
            select(RoomPrice)
            .where(RoomPrice.room_id == room_id)
            .order_by(RoomPrice.hours)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_price(self, price: RoomPrice) -> RoomPrice:
        """Update existing price."""
        await self._session.flush()
        await self._session.refresh(price)
        return price

    async def delete_price(self, price: RoomPrice) -> None:
        """Remove price from database."""
        await self._session.delete(price)
        await self._session.flush()

    # Room Photo CRUD

    async def create_photo(self, photo: RoomPhoto) -> RoomPhoto:
        """Persist a new room photo."""
        self._session.add(photo)
        await self._session.flush()
        await self._session.refresh(photo)
        return photo

    async def find_photo_by_id(self, photo_id: int) -> Optional[RoomPhoto]:
        """Retrieve photo by ID."""
        stmt = select(RoomPhoto).where(RoomPhoto.id == photo_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_photos_by_room(self, room_id: int) -> list[RoomPhoto]:
        """Retrieve all photos for a room."""
        stmt = (
            select(RoomPhoto)
            .where(RoomPhoto.room_id == room_id)
            .order_by(RoomPhoto.index)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_photo(self, photo: RoomPhoto) -> RoomPhoto:
        """Update existing photo."""
        await self._session.flush()
        await self._session.refresh(photo)
        return photo

    async def delete_photo(self, photo: RoomPhoto) -> None:
        """Remove photo from database."""
        await self._session.delete(photo)
        await self._session.flush()

    async def delete_photos_by_room(self, room_id: int) -> None:
        """Remove all photos for a room."""
        stmt = delete(RoomPhoto).where(RoomPhoto.room_id == room_id)
        await self._session.execute(stmt)
        await self._session.flush()
