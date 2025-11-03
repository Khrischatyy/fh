"""Badge business logic service."""

from typing import Optional

from src.badges.models import Badge
from src.badges.repository import BadgeRepository
from src.badges.schemas import BadgeCreate, BadgeUpdate, BadgeResponse, BadgeListResponse
from src.exceptions import NotFoundException, BadRequestException
from src.storage import get_gcs


class BadgeService:
    """Service for badge business logic."""

    def __init__(self, repository: BadgeRepository):
        self.repository = repository
        self.gcs = get_gcs()

    async def get_badge(self, badge_id: int) -> BadgeResponse:
        """Get badge by ID."""
        badge = await self.repository.get_by_id(badge_id)
        if not badge:
            raise NotFoundException(f"Badge with ID {badge_id} not found")

        return self._to_response(badge)

    async def get_all_badges(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> BadgeListResponse:
        """Get all badges with pagination."""
        badges = await self.repository.get_all(skip=skip, limit=limit)
        total = await self.repository.count()

        return BadgeListResponse(
            badges=[self._to_response(badge) for badge in badges],
            total=total
        )

    async def create_badge(self, data: BadgeCreate) -> BadgeResponse:
        """Create new badge."""
        # Check if badge with same name exists
        existing = await self.repository.get_by_name(data.name)
        if existing:
            raise BadRequestException(f"Badge with name '{data.name}' already exists")

        badge = Badge(
            name=data.name,
            image=data.image,
            description=data.description
        )

        badge = await self.repository.create(badge)
        return self._to_response(badge)

    async def update_badge(
        self,
        badge_id: int,
        data: BadgeUpdate
    ) -> BadgeResponse:
        """Update existing badge."""
        badge = await self.repository.get_by_id(badge_id)
        if not badge:
            raise NotFoundException(f"Badge with ID {badge_id} not found")

        # Check name uniqueness if updating name
        if data.name and data.name != badge.name:
            existing = await self.repository.get_by_name(data.name)
            if existing:
                raise BadRequestException(f"Badge with name '{data.name}' already exists")
            badge.name = data.name

        if data.image is not None:
            badge.image = data.image

        if data.description is not None:
            badge.description = data.description

        badge = await self.repository.update(badge)
        return self._to_response(badge)

    async def delete_badge(self, badge_id: int) -> None:
        """Delete badge."""
        badge = await self.repository.get_by_id(badge_id)
        if not badge:
            raise NotFoundException(f"Badge with ID {badge_id} not found")

        await self.repository.delete(badge)

    async def get_badges_by_ids(self, badge_ids: list[int]) -> list[BadgeResponse]:
        """Get multiple badges by IDs."""
        badges = await self.repository.get_by_ids(badge_ids)
        return [self._to_response(badge) for badge in badges]

    def _to_response(self, badge: Badge) -> BadgeResponse:
        """Convert Badge model to response schema with full image URL."""
        # Get full public URL for the image
        image_url = self.gcs.get_public_url(badge.image)

        return BadgeResponse(
            id=badge.id,
            name=badge.name,
            image=badge.image,
            image_url=image_url,
            description=badge.description
        )