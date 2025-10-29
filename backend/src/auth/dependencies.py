"""
Authentication dependencies for route protection.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.auth.models import User, UserRole
from src.auth.service import auth_service
from src.exceptions import UnauthorizedException, ForbiddenException


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to get currently authenticated user.

    Handles both:
    - Standard JWT tokens: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    - Laravel Sanctum-style tokens: "2|eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

    Usage:
        @router.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    """
    token = credentials.credentials

    # Strip Sanctum-style prefix (e.g., "2|") if present
    if "|" in token:
        _, token = token.split("|", 1)

    try:
        payload = auth_service.decode_access_token(token)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise UnauthorizedException("Invalid authentication credentials")
        # Convert string user_id back to int
        user_id: int = int(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid user ID in token")
    except Exception as e:
        raise UnauthorizedException("Invalid authentication credentials")

    user = await auth_service.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise UnauthorizedException("User not found")

    # Note: Laravel doesn't have is_active field, so we skip this check
    # if not user.is_active:
    #     raise ForbiddenException("User account is inactive")

    return user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get currently authenticated user with verified email.

    Usage:
        @router.post("/create-listing")
        async def create_listing(current_user: User = Depends(get_current_verified_user)):
            ...
    """
    if not current_user.email_verified_at:
        raise ForbiddenException("Email verification required")
    return current_user


async def get_current_studio_owner(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to ensure current user is a studio owner.

    Usage:
        @router.post("/studio/create")
        async def create_studio(current_user: User = Depends(get_current_studio_owner)):
            ...
    """
    if current_user.role not in [UserRole.STUDIO_OWNER, UserRole.ADMIN]:
        raise ForbiddenException("Studio owner access required")
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to ensure current user is an admin.

    Usage:
        @router.delete("/users/{user_id}")
        async def delete_user(current_user: User = Depends(get_current_admin)):
            ...
    """
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException("Admin access required")
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Dependency to get current user if authenticated, None otherwise.
    Useful for endpoints that have different behavior for authenticated users.

    Usage:
        @router.get("/studios")
        async def list_studios(current_user: Optional[User] = Depends(get_optional_current_user)):
            # Show favorited studios if user is authenticated
            ...
    """
    if credentials is None:
        return None

    try:
        return get_current_user(credentials, db)
    except Exception:
        return None
