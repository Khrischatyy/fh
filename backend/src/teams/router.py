"""
Team router - Laravel-compatible endpoints for team member management.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.database import get_db
from src.teams.schemas import AddMemberRequest, DeleteTeamMemberRequest
from src.teams.service import TeamService

router = APIRouter(prefix="/team", tags=["Team"])


@router.post("/member", status_code=status.HTTP_200_OK)
async def add_team_member(
    request: AddMemberRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Add team member to studio.

    Laravel compatible: POST /api/team/member

    Creates a new user account, assigns role, sets hourly rate,
    and sends invitation email with password reset link.

    **Request Body:**
    - name: Member full name
    - email: Member email (must be unique)
    - address_id: Studio address ID
    - role: studio_engineer or studio_manager
    - rate_per_hour: Hourly rate
    """
    try:
        service = TeamService(db)
        user = await service.add_member(
            name=request.name,
            email=request.email,
            address_id=request.address_id,
            role=request.role,
            rate_per_hour=request.rate_per_hour,
            current_user_id=current_user.id
        )

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            "roles": [user.role],
        }

        return {
            "success": True,
            "data": user_data,
            "message": "Staff member added successfully.",
            "code": 200
        }

    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        detail = getattr(e, "detail", {"message": str(e), "errors": {}})

        return {
            "success": False,
            "data": None,
            "message": detail.get("message", str(e)),
            "code": status_code
        }


@router.get("/email/check", status_code=status.HTTP_200_OK)
async def check_member_email(
    q: Annotated[str, Query(description="Email search query")],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Search for studio engineers by email (autocomplete).

    Laravel compatible: GET /api/team/email/check?q={query}

    Returns list of users with studio_engineer role matching the email pattern.
    Used for autocomplete/typeahead in frontend.

    **Query Parameters:**
    - q: Email search string
    """
    try:
        service = TeamService(db)
        results = await service.check_member_email(q)

        return {
            "success": True,
            "data": results,
            "message": "Emails matching the query retrieved successfully.",
            "code": 200
        }

    except Exception as e:
        return {
            "success": False,
            "data": [],
            "message": str(e),
            "code": 500
        }


@router.delete("/member", status_code=status.HTTP_200_OK)
async def remove_team_member(
    request: DeleteTeamMemberRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Remove team member from studio.

    Laravel compatible: DELETE /api/team/member

    Detaches user from address (does not delete user account).

    **Request Body:**
    - address_id: Studio address ID
    - member_id: Team member user ID
    """
    try:
        service = TeamService(db)
        await service.remove_member(
            address_id=request.address_id,
            member_id=request.member_id,
            current_user_id=current_user.id
        )

        return {
            "success": True,
            "data": [],
            "message": "Staff member removed successfully.",
            "code": 200
        }

    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        detail = getattr(e, "detail", {"message": str(e), "errors": {}})

        return {
            "success": False,
            "data": None,
            "message": detail.get("message", str(e)),
            "code": status_code
        }
