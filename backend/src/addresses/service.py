"""
Address service - Business logic layer.
Orchestrates operations between repository and external dependencies.
"""
import re
from decimal import Decimal
from typing import Optional

from src.addresses.models import Address
from src.addresses.repository import AddressRepository
from src.addresses.schemas import AddressCreate, AddressUpdate
from src.exceptions import NotFoundException, ConflictException


class AddressService:
    """Service layer for Address business logic."""

    def __init__(self, repository: AddressRepository):
        self._repository = repository

    async def create_address(self, data: AddressCreate) -> Address:
        """
        Create a new address with validation and slug generation.

        Applies business rules:
        - Generates unique slug
        - Ensures slug uniqueness
        - Initializes default values
        """
        slug = data.slug if hasattr(data, 'slug') else f"address-{data.city_id}-{data.company_id}"
        slug = await self._ensure_unique_slug(slug)

        address = Address(
            slug=slug,
            street=data.street if hasattr(data, 'street') else None,
            latitude=data.latitude if hasattr(data, 'latitude') else None,
            longitude=data.longitude if hasattr(data, 'longitude') else None,
            timezone=data.timezone if hasattr(data, 'timezone') else None,
            city_id=data.city_id if hasattr(data, 'city_id') else None,
            company_id=data.company_id if hasattr(data, 'company_id') else None,
            available_balance=Decimal("0.00"),
        )

        return await self._repository.create(address)

    async def get_address(self, address_id: int) -> Address:
        """Retrieve an address by ID or raise NotFoundException."""
        address = await self._repository.find_by_id(address_id)
        if not address:
            raise NotFoundException(f"Address with ID {address_id} not found")
        return address

    async def get_address_by_slug(self, slug: str) -> Address:
        """Retrieve an address by slug or raise NotFoundException."""
        address = await self._repository.find_by_slug(slug)
        if not address:
            raise NotFoundException(f"Address with slug '{slug}' not found")
        return address

    async def get_company_addresses(self, company_id: int) -> list[Address]:
        """Retrieve all addresses for a company."""
        return await self._repository.find_by_company(company_id)

    async def update_address(self, address_id: int, data: AddressUpdate) -> Address:
        """
        Update an existing address with validation.

        Applies business rules:
        - Validates entity existence
        - Regenerates slug if name changes
        - Ensures slug uniqueness
        """
        address = await self.get_address(address_id)

        update_data = data.model_dump(exclude_unset=True)

        # Handle name change with slug regeneration
        if "name" in update_data and update_data["name"] != address.name:
            new_slug = self._generate_slug(update_data["name"])
            update_data["slug"] = await self._ensure_unique_slug(new_slug, exclude_id=address_id)

        for field, value in update_data.items():
            setattr(address, field, value)

        return await self._repository.update(address)

    async def delete_address(self, address_id: int) -> None:
        """Delete an address by ID."""
        address = await self.get_address(address_id)
        await self._repository.delete(address)

    async def publish_address(self, address_id: int) -> Address:
        """
        Publish an address, making it visible to the public.

        Business rule: Only active addresses can be published.
        """
        address = await self.get_address(address_id)

        if not address.is_active:
            raise ConflictException("Cannot publish an inactive address")

        address.is_published = True
        return await self._repository.update(address)

    async def unpublish_address(self, address_id: int) -> Address:
        """Unpublish an address, hiding it from public view."""
        address = await self.get_address(address_id)
        address.is_published = False
        return await self._repository.update(address)

    def _generate_slug(self, name: str) -> str:
        """
        Generate URL-friendly slug from name.

        Transformation rules:
        - Convert to lowercase
        - Replace spaces and special chars with hyphens
        - Remove consecutive hyphens
        - Strip leading/trailing hyphens
        """
        slug = name.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug.strip("-")

    async def _ensure_unique_slug(self, slug: str, exclude_id: Optional[int] = None) -> str:
        """
        Ensure slug uniqueness by appending a counter if needed.

        Strategy: Append incrementing counter until unique slug is found.
        """
        original_slug = slug
        counter = 1

        while await self._repository.exists_by_slug(slug, exclude_id):
            slug = f"{original_slug}-{counter}"
            counter += 1

        return slug

    # Equipment operations

    async def get_equipment_types(self):
        """Get all equipment types."""
        return await self._repository.get_all_equipment_types()

    async def get_address_equipment(self, address_id: int):
        """Get equipment for an address."""
        address = await self.get_address(address_id)
        return address.equipment

    async def add_equipment(self, address_id: int, equipment_ids: list[int]):
        """Add equipment to an address."""
        address = await self.get_address(address_id)

        # Get equipment entities
        equipment_list = await self._repository.get_equipment_by_ids(equipment_ids)

        # Add to address (many-to-many relationship)
        for equipment in equipment_list:
            if equipment not in address.equipment:
                address.equipment.append(equipment)

        await self._repository.update(address)
        return address.equipment

    async def remove_equipment(self, address_id: int, equipment_ids: list[int]):
        """Remove equipment from an address."""
        address = await self.get_address(address_id)

        # Remove equipment from address
        address.equipment = [
            eq for eq in address.equipment if eq.id not in equipment_ids
        ]

        await self._repository.update(address)
        return address.equipment

    # Badge operations

    async def get_address_badges(self, address_id: int):
        """Get badges for an address."""
        address = await self.get_address(address_id)
        return address.badges

    async def add_badges(self, address_id: int, badge_ids: list[int]):
        """Add badges to an address."""
        address = await self.get_address(address_id)

        # Get badge entities
        badge_list = await self._repository.get_badge_by_ids(badge_ids)

        # Add to address (many-to-many relationship)
        for badge in badge_list:
            if badge not in address.badges:
                address.badges.append(badge)

        await self._repository.update(address)
        return address.badges

    async def get_addresses_by_city(self, city_id: int) -> list[Address]:
        """
        Get all complete addresses for a specific city.

        Matches Laravel: getAddressByCityIdWithWorkingHours
        Filters only complete addresses (has operating hours + payment gateway configured).
        """
        addresses = await self._repository.find_by_city(city_id)

        # Filter only complete addresses
        complete_addresses = []
        for address in addresses:
            # Check if address is complete:
            # 1. Has operating hours
            has_operating_hours = len(address.operating_hours) > 0

            # 2. User has payment gateway configured (stripe or square)
            has_payment_gateway = False
            if address.company and address.company.admin_companies:
                for admin_company in address.company.admin_companies:
                    if admin_company.admin:  # Note: relationship is 'admin' not 'user'
                        user = admin_company.admin
                        has_stripe = user.stripe_account_id is not None
                        has_square = user.payment_gateway == 'square'
                        has_payment_gateway = has_stripe or has_square
                        break

            if has_operating_hours and has_payment_gateway:
                complete_addresses.append(address)

        return complete_addresses
