"""
Support ticket service for business logic.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from src.support.models import SupportTicket, TicketStatus, TicketPriority
from src.support.repository import SupportTicketRepository
from src.support.schemas import (
    SupportTicketCreateRequest,
    SupportTicketUpdateRequest,
    SupportTicketResponse,
    SupportTicketListItem,
)
from src.exceptions import NotFoundException, ForbiddenException


class SupportTicketService:
    """Service for support ticket business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = SupportTicketRepository(db)

    async def create_ticket(
        self,
        data: SupportTicketCreateRequest,
        user_id: Optional[int] = None,
    ) -> SupportTicket:
        """
        Create a new support ticket.

        Args:
            data: Ticket creation data
            user_id: Optional user ID (for authenticated users)

        Returns:
            Created support ticket
        """
        ticket = SupportTicket(
            user_id=user_id,
            email=data.email,
            name=data.name,
            subject=data.subject,
            message=data.message,
            status=TicketStatus.OPEN,
            priority=TicketPriority.MEDIUM,
        )

        return await self.repository.create(ticket)

    async def get_ticket(self, ticket_id: int) -> SupportTicket:
        """Get a support ticket by ID."""
        ticket = await self.repository.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException(f"Support ticket {ticket_id} not found")
        return ticket

    async def get_all_tickets(
        self,
        status: Optional[TicketStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[SupportTicket]:
        """Get all support tickets (admin only)."""
        return await self.repository.get_all(status=status, limit=limit, offset=offset)

    async def get_user_tickets(self, user_id: int) -> List[SupportTicket]:
        """Get all tickets for a specific user."""
        return await self.repository.get_by_user_id(user_id)

    async def update_ticket(
        self,
        ticket_id: int,
        data: SupportTicketUpdateRequest,
    ) -> SupportTicket:
        """
        Update a support ticket (admin only).

        Args:
            ticket_id: Ticket ID to update
            data: Update data

        Returns:
            Updated support ticket
        """
        ticket = await self.get_ticket(ticket_id)

        if data.status is not None:
            ticket.status = data.status
        if data.priority is not None:
            ticket.priority = data.priority
        if data.assigned_to_id is not None:
            ticket.assigned_to_id = data.assigned_to_id
        if data.admin_notes is not None:
            ticket.admin_notes = data.admin_notes

        return await self.repository.update(ticket)

    async def get_open_tickets_count(self) -> int:
        """Get count of open tickets."""
        return await self.repository.count_open_tickets()
