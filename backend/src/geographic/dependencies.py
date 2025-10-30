"""
Geographic dependencies - Dependency injection configuration.
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.geographic.repository import GeographicRepository
from src.geographic.service import GeographicService


async def get_geographic_repository(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> GeographicRepository:
    """Provide GeographicRepository instance."""
    return GeographicRepository(session)


async def get_geographic_service(
    repository: Annotated[GeographicRepository, Depends(get_geographic_repository)]
) -> GeographicService:
    """Provide GeographicService instance."""
    return GeographicService(repository)
