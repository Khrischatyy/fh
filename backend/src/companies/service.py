"""
Company service - Business logic layer for companies.
"""
import re
from src.companies.models import Company, AdminCompany
from src.companies.repository import CompanyRepository
from src.companies.schemas import CompanyCreate, CompanyUpdate
from src.exceptions import NotFoundException, ConflictException


class CompanyService:
    """Service for company business operations."""

    def __init__(self, repository: CompanyRepository):
        self._repository = repository

    async def create_company(self, data: CompanyCreate, user_id: int) -> Company:
        """
        Create a new company.

        Business rules:
        - User can only have one company
        - Slug is auto-generated from name
        - User is automatically added as admin
        """
        # Check if user already has a company
        existing_companies = await self._repository.find_by_user(user_id)
        if existing_companies:
            raise ConflictException("User already has a company")

        # Generate unique slug
        slug = self._generate_slug(data.name)
        slug = await self._ensure_unique_slug(slug)

        company = Company(
            name=data.name,
            logo=data.logo,
            slug=slug,
        )

        company = await self._repository.create(company)

        # Add user as admin
        await self._repository.add_admin(company.id, user_id)

        return company

    async def get_company(self, company_id: int) -> Company:
        """Get company by ID or raise exception."""
        company = await self._repository.find_by_id(company_id)
        if not company:
            raise NotFoundException(f"Company with ID {company_id} not found")
        return company

    async def get_company_by_slug(self, slug: str) -> Company:
        """Get company by slug or raise exception."""
        company = await self._repository.find_by_slug(slug)
        if not company:
            raise NotFoundException(f"Company with slug '{slug}' not found")
        return company

    async def get_user_companies(self, user_id: int) -> list[Company]:
        """Get all companies where user is admin."""
        return await self._repository.find_by_user(user_id)

    async def update_company(self, company_id: int, data: CompanyUpdate) -> Company:
        """Update company details."""
        company = await self.get_company(company_id)

        if data.name is not None:
            company.name = data.name
            # Regenerate slug if name changed
            new_slug = self._generate_slug(data.name)
            if new_slug != company.slug:
                new_slug = await self._ensure_unique_slug(new_slug, exclude_id=company_id)
                company.slug = new_slug

        if data.logo is not None:
            company.logo = data.logo

        return await self._repository.update(company)

    async def delete_company(self, company_id: int) -> None:
        """Delete a company."""
        company = await self.get_company(company_id)
        await self._repository.delete(company)

    async def add_admin(self, company_id: int, user_id: int) -> AdminCompany:
        """Add a user as company admin."""
        # Verify company exists
        await self.get_company(company_id)

        # Check if already admin
        if await self._repository.is_admin(company_id, user_id):
            raise ConflictException("User is already an admin of this company")

        return await self._repository.add_admin(company_id, user_id)

    async def remove_admin(self, company_id: int, user_id: int) -> None:
        """Remove a user as company admin."""
        # Verify company exists
        await self.get_company(company_id)

        # Check if user is admin
        if not await self._repository.is_admin(company_id, user_id):
            raise NotFoundException("User is not an admin of this company")

        await self._repository.remove_admin(company_id, user_id)

    async def is_admin(self, company_id: int, user_id: int) -> bool:
        """Check if user is admin of company."""
        return await self._repository.is_admin(company_id, user_id)

    def _generate_slug(self, name: str) -> str:
        """Generate URL-safe slug from company name."""
        slug = name.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug.strip("-")

    async def _ensure_unique_slug(self, slug: str, exclude_id: int = None) -> str:
        """Ensure slug is unique by appending number if needed."""
        original_slug = slug
        counter = 1

        while await self._repository.exists_by_slug(slug, exclude_id):
            slug = f"{original_slug}-{counter}"
            counter += 1

        return slug
