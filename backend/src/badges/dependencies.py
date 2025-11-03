"""Badge dependencies for FastAPI."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.badges.repository import BadgeRepository
from src.badges.service import BadgeService


def get_badge_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> BadgeRepository:
    """Get badge repository instance."""
    return BadgeRepository(db)


def get_badge_service(
    repository: Annotated[BadgeRepository, Depends(get_badge_repository)]
) -> BadgeService:
    """Get badge service instance."""
    return BadgeService(repository)