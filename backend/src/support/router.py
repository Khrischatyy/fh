"""
Support ticket router for API endpoints.
Provides endpoints for creating and viewing support tickets.
"""
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.auth.dependencies import get_current_user, get_optional_current_user
from src.auth.models import User
from src.support import schemas
from src.support.service import SupportTicketService
from src.support.models import TicketStatus


router = APIRouter(prefix="/support", tags=["support"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.LaravelSupportTicketResponse,
    summary="Create support ticket",
    description="Create a new support ticket. Works for both authenticated and anonymous users."
)
async def create_support_ticket(
    data: schemas.SupportTicketCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_optional_current_user)] = None,
):
    """
    Create a new support ticket.

    - Authenticated users: user_id is automatically linked
    - Anonymous users: email and name are required

    Returns:
    - Created support ticket with ID and timestamps
    """
    service = SupportTicketService(db)

    ticket = await service.create_ticket(
        data=data,
        user_id=current_user.id if current_user else None,
    )

    return schemas.LaravelSupportTicketResponse(
        success=True,
        data=schemas.SupportTicketResponse.model_validate(ticket),
        message="Support ticket created successfully. We'll get back to you soon!",
        code=201,
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=schemas.LaravelSupportTicketsResponse,
    summary="Get all support tickets (Admin)",
    description="Get all support tickets. Admin access only."
)
async def get_all_tickets(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    status_filter: Optional[TicketStatus] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Get all support tickets (admin only).

    Query parameters:
    - status: Filter by ticket status (open, in_progress, resolved, closed)
    - limit: Max number of tickets to return (default 50)
    - offset: Pagination offset

    Returns:
    - List of support tickets
    """
    # Check if user is admin (has admin role or is support team)
    if current_user.role not in ["admin", "support"]:
        # Return only user's own tickets if not admin
        service = SupportTicketService(db)
        tickets = await service.get_user_tickets(current_user.id)
        return schemas.LaravelSupportTicketsResponse(
            success=True,
            data=[schemas.SupportTicketListItem.model_validate(t) for t in tickets],
            message="Your support tickets retrieved successfully",
            code=200,
        )

    service = SupportTicketService(db)
    tickets = await service.get_all_tickets(
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    return schemas.LaravelSupportTicketsResponse(
        success=True,
        data=[schemas.SupportTicketListItem.model_validate(t) for t in tickets],
        message="Support tickets retrieved successfully",
        code=200,
    )


@router.get(
    "/my-tickets",
    status_code=status.HTTP_200_OK,
    response_model=schemas.LaravelSupportTicketsResponse,
    summary="Get my support tickets",
    description="Get all support tickets created by the current user."
)
async def get_my_tickets(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get all support tickets for the authenticated user.

    Returns:
    - List of user's support tickets
    """
    service = SupportTicketService(db)
    tickets = await service.get_user_tickets(current_user.id)

    return schemas.LaravelSupportTicketsResponse(
        success=True,
        data=[schemas.SupportTicketListItem.model_validate(t) for t in tickets],
        message="Your support tickets retrieved successfully",
        code=200,
    )


@router.get(
    "/{ticket_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.LaravelSupportTicketResponse,
    summary="Get support ticket details",
    description="Get detailed information about a specific support ticket."
)
async def get_ticket_details(
    ticket_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get support ticket details.

    - Admin/Support: Can view any ticket
    - User: Can only view their own tickets

    Returns:
    - Detailed support ticket information
    """
    service = SupportTicketService(db)
    ticket = await service.get_ticket(ticket_id)

    # Check access permissions
    if current_user.role not in ["admin", "support"]:
        if ticket.user_id != current_user.id:
            from src.exceptions import ForbiddenException
            raise ForbiddenException("You don't have permission to view this ticket")

    return schemas.LaravelSupportTicketResponse(
        success=True,
        data=schemas.SupportTicketResponse.model_validate(ticket),
        message="Support ticket retrieved successfully",
        code=200,
    )


@router.patch(
    "/{ticket_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.LaravelSupportTicketResponse,
    summary="Update support ticket (Admin)",
    description="Update a support ticket's status, priority, or assignment. Admin access only."
)
async def update_ticket(
    ticket_id: int,
    data: schemas.SupportTicketUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Update a support ticket (admin only).

    Request body:
    - status: New ticket status
    - priority: New ticket priority
    - assigned_to_id: User ID to assign ticket to
    - admin_notes: Internal admin notes

    Returns:
    - Updated support ticket
    """
    # Check admin access
    if current_user.role not in ["admin", "support"]:
        from src.exceptions import ForbiddenException
        raise ForbiddenException("Admin access required")

    service = SupportTicketService(db)
    ticket = await service.update_ticket(ticket_id, data)

    return schemas.LaravelSupportTicketResponse(
        success=True,
        data=schemas.SupportTicketResponse.model_validate(ticket),
        message="Support ticket updated successfully",
        code=200,
    )
