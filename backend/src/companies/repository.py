"""
Company repository - Data access layer.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.companies.models import Company, AdminCompany
from src.exceptions import NotFoundException


class CompanyRepository:
    """Repository for Company entity database operations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, company: Company) -> Company:
        """Persist a new company."""
        self._session.add(company)
        await self._session.flush()
        await self._session.refresh(company)
        return company

    async def find_by_id(self, company_id: int) -> Optional[Company]:
        """Retrieve company by ID with relationships."""
        stmt = (
            select(Company)
            .where(Company.id == company_id)
            .options(
                selectinload(Company.addresses),
                selectinload(Company.admin_companies),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_slug(self, slug: str) -> Optional[Company]:
        """Retrieve company by slug with relationships."""
        stmt = (
            select(Company)
            .where(Company.slug == slug)
            .options(
                selectinload(Company.addresses),
                selectinload(Company.admin_companies),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_user(self, user_id: int) -> list[Company]:
        """Retrieve all companies where user is an admin."""
        stmt = (
            select(Company)
            .join(AdminCompany)
            .where(AdminCompany.user_id == user_id)
            .options(selectinload(Company.addresses))
            .order_by(Company.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, company: Company) -> Company:
        """Update existing company."""
        await self._session.flush()
        await self._session.refresh(company)
        return company

    async def delete(self, company: Company) -> None:
        """Remove company from database."""
        await self._session.delete(company)
        await self._session.flush()

    async def exists_by_slug(self, slug: str, exclude_id: Optional[int] = None) -> bool:
        """Check if company with slug exists."""
        stmt = select(Company.id).where(Company.slug == slug)
        if exclude_id:
            stmt = stmt.where(Company.id != exclude_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def add_admin(self, company_id: int, user_id: int) -> AdminCompany:
        """Add user as company admin."""
        admin_company = AdminCompany(
            company_id=company_id,
            user_id=user_id,
        )
        self._session.add(admin_company)
        await self._session.flush()
        await self._session.refresh(admin_company)
        return admin_company

    async def remove_admin(self, company_id: int, user_id: int) -> None:
        """Remove user as company admin."""
        stmt = select(AdminCompany).where(
            AdminCompany.company_id == company_id,
            AdminCompany.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        admin_company = result.scalar_one_or_none()
        if admin_company:
            await self._session.delete(admin_company)
            await self._session.flush()

    async def is_admin(self, company_id: int, user_id: int) -> bool:
        """Check if user is company admin."""
        stmt = select(AdminCompany.id).where(
            AdminCompany.company_id == company_id,
            AdminCompany.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
