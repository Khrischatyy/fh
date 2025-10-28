"""
Address dependencies - Dependency injection providers.
Configures service and repository instances for request handling.
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.addresses.repository import AddressRepository
from src.addresses.service import AddressService


async def get_address_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> AddressRepository:
    """Provide AddressRepository instance with database session."""
    return AddressRepository(session)


async def get_address_service(
    repository: Annotated[AddressRepository, Depends(get_address_repository)]
) -> AddressService:
    """Provide AddressService instance with repository dependency."""
    return AddressService(repository)
