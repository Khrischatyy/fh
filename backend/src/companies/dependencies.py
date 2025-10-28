"""
Company dependencies - Dependency injection configuration.
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.companies.repository import CompanyRepository
from src.companies.service import CompanyService


async def get_company_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> CompanyRepository:
    """Provide CompanyRepository instance."""
    return CompanyRepository(session)


async def get_company_service(
    repository: Annotated[CompanyRepository, Depends(get_company_repository)]
) -> CompanyService:
    """Provide CompanyService instance."""
    return CompanyService(repository)
