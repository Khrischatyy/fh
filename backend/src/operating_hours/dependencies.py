"""
Operating Hours dependencies - Dependency injection configuration.
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.operating_hours.repository import OperatingHoursRepository
from src.operating_hours.service import OperatingHoursService


async def get_operating_hours_repository(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> OperatingHoursRepository:
    """Dependency provider for OperatingHoursRepository."""
    return OperatingHoursRepository(session)


async def get_operating_hours_service(
    repository: Annotated[OperatingHoursRepository, Depends(get_operating_hours_repository)]
) -> OperatingHoursService:
    """Dependency provider for OperatingHoursService."""
    return OperatingHoursService(repository)
