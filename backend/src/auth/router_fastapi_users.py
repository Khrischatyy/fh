"""
Authentication router using FastAPI Users.
"""
from fastapi import APIRouter, Depends
from fastapi_users import models

from src.auth.schemas_fastapi_users import UserRead, UserCreate, UserUpdate
from src.auth.users import auth_backend, fastapi_users, current_active_user
from src.auth.models_fastapi_users import User

# Create router
router = APIRouter()

# Include FastAPI Users auth routes
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


# Custom endpoint for getting current user (backward compatibility)
@router.get("/auth/me", response_model=UserRead, tags=["auth"])
async def get_me(user: User = Depends(current_active_user)):
    """Get current authenticated user."""
    return user


# Health check endpoint
@router.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "authentication": "fastapi-users",
        "version": "2.0.0"
    }
