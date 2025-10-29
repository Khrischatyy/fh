"""
Address repository - Data access layer.
Handles all database operations for Address entities.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.addresses.models import Address, Equipment, EquipmentType, Badge
from src.exceptions import NotFoundException


class AddressRepository:
    """Repository for Address entity database operations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, address: Address) -> Address:
        """Persist a new address to the database."""
        self._session.add(address)
        await self._session.flush()
        await self._session.refresh(address)
        return address

    async def find_by_id(self, address_id: int) -> Optional[Address]:
        """Retrieve an address by ID with related entities."""
        stmt = (
            select(Address)
            .where(Address.id == address_id)
            .options(
                selectinload(Address.city),
                selectinload(Address.company),
                selectinload(Address.operating_hours),
                selectinload(Address.equipment),
                selectinload(Address.badges),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_slug(self, slug: str) -> Optional[Address]:
        """Retrieve an address by slug."""
        stmt = select(Address).where(Address.slug == slug)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_slug_with_relations(self, slug: str) -> Optional[Address]:
        """
        Retrieve an address by slug with all relationships.

        Matches Laravel: getAddressBySlug
        Loads: badges, rooms, rooms.photos, rooms.prices (enabled only),
               company, company.adminCompany.admin, operatingHours
        """
        from src.rooms.models import Room, RoomPrice
        from src.companies.models import Company, AdminCompany

        stmt = (
            select(Address)
            .where(Address.slug == slug)
            .options(
                selectinload(Address.badges),
                selectinload(Address.rooms).selectinload(Room.photos),
                selectinload(Address.rooms).selectinload(Room.prices),
                selectinload(Address.company).selectinload(Company.admin_companies).selectinload(AdminCompany.admin),
                selectinload(Address.operating_hours),
                # TODO: Add equipment loading when table is created
                # selectinload(Address.equipment).selectinload(Equipment.equipment_type),
                selectinload(Address.city),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_company(self, company_id: int) -> list[Address]:
        """Retrieve all addresses for a specific company."""
        stmt = (
            select(Address)
            .where(Address.company_id == company_id)
            .order_by(Address.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, address: Address) -> Address:
        """Update an existing address."""
        await self._session.flush()
        await self._session.refresh(address)
        return address

    async def delete(self, address: Address) -> None:
        """Remove an address from the database."""
        await self._session.delete(address)
        await self._session.flush()

    async def exists_by_slug(self, slug: str, exclude_id: Optional[int] = None) -> bool:
        """Check if an address with the given slug exists."""
        stmt = select(Address.id).where(Address.slug == slug)
        if exclude_id:
            stmt = stmt.where(Address.id != exclude_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    # Equipment operations

    async def get_all_equipment_types(self) -> list[EquipmentType]:
        """Get all equipment types."""
        stmt = select(EquipmentType).order_by(EquipmentType.name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_equipment_by_ids(self, equipment_ids: list[int]) -> list[Equipment]:
        """Get equipment by IDs."""
        stmt = (
            select(Equipment)
            .where(Equipment.id.in_(equipment_ids))
            .options(selectinload(Equipment.equipment_type))
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # Badge operations

    async def get_badge_by_ids(self, badge_ids: list[int]) -> list[Badge]:
        """Get badges by IDs."""
        stmt = select(Badge).where(Badge.id.in_(badge_ids))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_city(self, city_id: int) -> list[Address]:
        """
        Retrieve all addresses for a specific city with all relationships.

        Matches Laravel: getAddressByCityId
        Loads: badges, rooms, rooms.photos, rooms.prices, company, company.adminCompany.admin, operatingHours
        """
        from src.rooms.models import Room
        from src.companies.models import Company, AdminCompany

        stmt = (
            select(Address)
            .where(Address.city_id == city_id)
            .options(
                selectinload(Address.badges),
                selectinload(Address.rooms).selectinload(Room.photos),
                selectinload(Address.rooms).selectinload(Room.prices),
                selectinload(Address.company).selectinload(Company.admin_companies).selectinload(AdminCompany.admin),
                selectinload(Address.operating_hours),
                selectinload(Address.city),
            )
            .order_by(Address.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
