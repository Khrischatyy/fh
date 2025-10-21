"""
Room dependencies - Dependency injection configuration.
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.rooms.repository import RoomRepository
from src.rooms.service import RoomService


async def get_room_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> RoomRepository:
    """Provide RoomRepository instance."""
    return RoomRepository(session)


async def get_room_service(
    repository: Annotated[RoomRepository, Depends(get_room_repository)]
) -> RoomService:
    """Provide RoomService instance."""
    return RoomService(repository)
