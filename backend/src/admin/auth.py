"""
Basic HTTP Authentication for Admin Panel.
Provides simple username/password authentication for SQLAdmin.
"""
import secrets
from typing import Optional
from fastapi import Request
from sqladmin.authentication import AuthenticationBackend
from src.config import settings


class BasicAuthBackend(AuthenticationBackend):
    """
    Basic HTTP Authentication backend for SQLAdmin.

    Uses credentials from environment variables:
    - ADMIN_USERNAME
    - ADMIN_PASSWORD
    """

    async def login(self, request: Request) -> bool:
        """
        Authenticate user with username and password from form.

        Args:
            request: FastAPI request object with form data

        Returns:
            bool: True if authentication successful, False otherwise
        """
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        # Validate credentials
        if (
            username == settings.admin_username
            and password == settings.admin_password
        ):
            # Store authentication token in session
            request.session.update({"token": secrets.token_urlsafe(32)})
            return True

        return False

    async def logout(self, request: Request) -> bool:
        """
        Log out user by clearing session.

        Args:
            request: FastAPI request object

        Returns:
            bool: Always True
        """
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """
        Check if user is authenticated.

        Args:
            request: FastAPI request object

        Returns:
            bool: True if authenticated, False otherwise
        """
        token = request.session.get("token")
        return token is not None
