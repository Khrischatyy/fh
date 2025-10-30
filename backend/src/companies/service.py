"""
Company service - Business logic layer for companies.
"""
import re
from typing import Dict
from decimal import Decimal
from datetime import time as time_type

from src.companies.models import Company, AdminCompany
from src.companies.repository import CompanyRepository
from src.companies.schemas import CompanyCreate, CompanyUpdate, BrandCreateRequest
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

    async def create_brand(self, data: BrandCreateRequest, user_id: int) -> Dict[str, any]:
        """
        Create a complete brand setup: company + address + default room + default hours.

        This is a convenience method that creates everything a studio owner needs in one go.
        Matches Laravel's AddressController::createBrand functionality.

        Steps:
        1. Find or create country
        2. Find or create city
        3. Create company (with admin relationship)
        4. Create address
        5. Create default room ("Room1")
        6. Create default operating hours
        7. Create default price ($60/hour)

        Returns:
            Dictionary with slug, address_id, room_id
        """
        from sqlalchemy import select
        from src.geographic.models import Country, City
        from src.addresses.models import Address, OperatingHour
        from src.rooms.models import Room, RoomPrice

        # Step 1 & 2: Find or create country and city
        # Find or create country
        stmt = select(Country).where(Country.name == data.country)
        result = await self._repository._session.execute(stmt)
        country = result.scalar_one_or_none()

        if not country:
            country = Country(name=data.country)
            self._repository._session.add(country)
            await self._repository._session.flush()

        # Find or create city
        stmt = select(City).where(
            City.name == data.city.lower(),
            City.country_id == country.id
        )
        result = await self._repository._session.execute(stmt)
        city = result.scalar_one_or_none()

        if not city:
            city = City(name=data.city.lower(), country_id=country.id)
            self._repository._session.add(city)
            await self._repository._session.flush()

        # Step 3: Create company (using existing method)
        company_data = CompanyCreate(name=data.company)
        company = await self.create_company(company_data, user_id)

        # Step 4: Create address
        address_slug = self._generate_slug(f"{data.company}-{data.city}")
        address_slug = await self._ensure_unique_address_slug(address_slug)

        address = Address(
            street=data.street,
            longitude=data.longitude,
            latitude=data.latitude,
            city_id=city.id,
            company_id=company.id,
            slug=address_slug,
            timezone=data.timezone or "UTC",
        )
        self._repository._session.add(address)
        await self._repository._session.flush()

        # Step 5: Create default room
        room = Room(
            name="Room1",
            address_id=address.id,
        )
        self._repository._session.add(room)
        await self._repository._session.flush()

        # Step 6: Create default operating hours (24/7 mode)
        operating_hour = OperatingHour(
            address_id=address.id,
            mode_id=1,  # 24/7 mode
            day_of_week=0,  # Sunday (not used in 24/7 mode)
            open_time=time_type(0, 0, 0),  # 00:00:00
            close_time=time_type(23, 59, 59),  # 23:59:59
            is_closed=False,
        )
        self._repository._session.add(operating_hour)
        await self._repository._session.flush()

        # Step 7: Create default price ($60/hour for 1 hour)
        room_price = RoomPrice(
            room_id=room.id,
            hours=1,
            price_per_hour=Decimal("60.00"),
            total_price=Decimal("60.00"),  # 1 hour * $60/hour
            is_enabled=True,
        )
        self._repository._session.add(room_price)
        await self._repository._session.flush()

        return {
            "slug": company.slug,
            "address_id": address.id,
            "room_id": room.id,
        }

    async def _ensure_unique_address_slug(self, slug: str, exclude_id: int = None) -> str:
        """Ensure address slug is unique by appending number if needed."""
        from sqlalchemy import select
        from src.addresses.models import Address

        original_slug = slug
        counter = 1

        while True:
            stmt = select(Address).where(Address.slug == slug)
            if exclude_id:
                stmt = stmt.where(Address.id != exclude_id)

            result = await self._repository._session.execute(stmt)
            if not result.scalar_one_or_none():
                break

            slug = f"{original_slug}-{counter}"
            counter += 1

        return slug
