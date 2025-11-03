"""Badge repository for database operations."""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.badges.models import Badge


class BadgeRepository:
    """Repository for badge database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, badge_id: int) -> Optional[Badge]:
        """Get badge by ID."""
        result = await self.db.execute(
            select(Badge).where(Badge.id == badge_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Badge]:
        """Get badge by name."""
        result = await self.db.execute(
            select(Badge).where(Badge.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> list[Badge]:
        """Get all badges with pagination."""
        result = await self.db.execute(
            select(Badge)
            .offset(skip)
            .limit(limit)
            .order_by(Badge.name)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        """Count total badges."""
        result = await self.db.execute(select(func.count(Badge.id)))
        return result.scalar_one()

    async def create(self, badge: Badge) -> Badge:
        """Create new badge."""
        self.db.add(badge)
        await self.db.flush()
        await self.db.refresh(badge)
        return badge

    async def update(self, badge: Badge) -> Badge:
        """Update existing badge."""
        await self.db.flush()
        await self.db.refresh(badge)
        return badge

    async def delete(self, badge: Badge) -> None:
        """Delete badge."""
        await self.db.delete(badge)
        await self.db.flush()

    async def get_by_ids(self, badge_ids: list[int]) -> list[Badge]:
        """Get badges by list of IDs."""
        result = await self.db.execute(
            select(Badge).where(Badge.id.in_(badge_ids))
        )
        return list(result.scalars().all())
