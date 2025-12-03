"""
Support ticket repository for database operations.
"""
from typing import Optional, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.support.models import SupportTicket, TicketStatus


class SupportTicketRepository:
    """Repository for support ticket database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, ticket: SupportTicket) -> SupportTicket:
        """Create a new support ticket."""
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def get_by_id(self, ticket_id: int) -> Optional[SupportTicket]:
        """Get a support ticket by ID."""
        result = await self.db.execute(
            select(SupportTicket)
            .options(joinedload(SupportTicket.user))
            .where(SupportTicket.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        status: Optional[TicketStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[SupportTicket]:
        """Get all support tickets with optional filtering."""
        query = select(SupportTicket).order_by(desc(SupportTicket.created_at))

        if status:
            query = query.where(SupportTicket.status == status)

        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: int) -> List[SupportTicket]:
        """Get all support tickets for a specific user."""
        result = await self.db.execute(
            select(SupportTicket)
            .where(SupportTicket.user_id == user_id)
            .order_by(desc(SupportTicket.created_at))
        )
        return list(result.scalars().all())

    async def get_by_email(self, email: str) -> List[SupportTicket]:
        """Get all support tickets for a specific email."""
        result = await self.db.execute(
            select(SupportTicket)
            .where(SupportTicket.email == email)
            .order_by(desc(SupportTicket.created_at))
        )
        return list(result.scalars().all())

    async def update(self, ticket: SupportTicket) -> SupportTicket:
        """Update a support ticket."""
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def count_open_tickets(self) -> int:
        """Count all open tickets."""
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count(SupportTicket.id))
            .where(SupportTicket.status == TicketStatus.OPEN)
        )
        return result.scalar() or 0
