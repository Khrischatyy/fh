"""
SQLAdmin Authentication Backend.
Provides email-based authentication with is_superuser check for SQLAdmin.
"""
from typing import Optional
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from passlib.context import CryptContext

from src.auth.models import User
from src.database import SessionLocal

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SuperuserAuthBackend(AuthenticationBackend):
    """
    Email-based authentication backend for SQLAdmin.
    Only users with is_superuser=True can access the admin panel.
    """

    async def login(self, request: Request) -> bool:
        """
        Authenticate user with email and password.

        Args:
            request: Starlette request object with form data

        Returns:
            bool: True if login successful, False otherwise
        """
        form = await request.form()
        username = form.get("username", "")
        password = form.get("password", "")

        # Validate form data
        if not username or len(username) < 3:
            return False

        # Query database for user
        with SessionLocal() as db:
            result = db.execute(
                select(User).where(User.email == username)
            )
            user = result.scalar_one_or_none()

            if not user:
                return False

            # Check if user is superuser
            if not user.is_superuser:
                return False

            # Verify password
            if not user.password_hash or not pwd_context.verify(password, user.password_hash):
                return False

            # Store authentication in session
            request.session.update({
                "admin_user_id": user.id,
                "admin_user_email": user.email,
                "admin_user_name": f"{user.firstname} {user.lastname}"
            })

            return True

    async def logout(self, request: Request) -> bool:
        """
        Log out user by clearing session.

        Args:
            request: Starlette request object

        Returns:
            bool: True if logout successful
        """
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """
        Check if user is authenticated.

        Args:
            request: Starlette request object

        Returns:
            bool: True if authenticated, False otherwise
        """
        user_id = request.session.get("admin_user_id")
        if not user_id:
            return False

        # Verify user still exists and is still a superuser
        with SessionLocal() as db:
            result = db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if user and user.is_superuser:
                return True

        return False
