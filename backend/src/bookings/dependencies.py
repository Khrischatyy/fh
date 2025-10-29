"""
Booking dependencies for FastAPI dependency injection.
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.bookings.repository import BookingRepository
from src.bookings.service import BookingService


async def get_booking_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> BookingRepository:
    """Get booking repository instance."""
    return BookingRepository(db)


async def get_booking_service(
    repository: Annotated[BookingRepository, Depends(get_booking_repository)]
) -> BookingService:
    """Get booking service instance."""
    return BookingService(repository)
