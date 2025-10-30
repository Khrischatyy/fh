"""
My Studios dependencies - FastAPI dependency injection.
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.my_studios.repository import MyStudiosRepository
from src.my_studios.service import MyStudiosService


async def get_my_studios_service(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> MyStudiosService:
    """Get MyStudiosService instance with dependencies."""
    repository = MyStudiosRepository(session)
    return MyStudiosService(repository)
