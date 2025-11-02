"""
FastMCP server setup for auto-exposing FastAPI endpoints as MCP tools.
"""

from typing import TYPE_CHECKING

import httpx
from fastapi import FastAPI
from fastmcp import FastMCP

if TYPE_CHECKING:
    from fastapi import FastAPI

# Global variable to store MCP HTTP app for lifespan integration
_mcp_http_app = None


def create_mcp_server(app: FastAPI) -> FastMCP:
    """
    Create and configure an MCP server that auto-exposes all FastAPI endpoints.

    Args:
        app: The FastAPI application instance

    Returns:
        FastMCP server instance

    Example:
        >>> from fastapi import FastAPI
        >>> from src.mcp import create_mcp_server
        >>>
        >>> app = FastAPI()
        >>> mcp = create_mcp_server(app)
    """
    # Create MCP server from FastAPI app
    # FastMCP.from_fastapi auto-exposes all FastAPI routes as MCP tools
    mcp = FastMCP.from_fastapi(app)

    # Add manual tools for form-data endpoints (FastMCP can't auto-convert these)
    # These endpoints use Form() parameters which require form-data, not JSON

    @mcp.tool()
    async def register_user(
        name: str,
        email: str,
        password: str,
        password_confirmation: str,
        role: str,
    ) -> dict:
        """
        Register a new user account.

        Args:
            name: User's full name
            email: User's email address
            password: User's password (minimum 8 characters)
            password_confirmation: Password confirmation (must match password)
            role: User role - must be one of: user, studio_owner, admin

        Returns:
            Registration response with user details and auth token
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/auth/register",
                data={  # Send as form-data
                    "name": name,
                    "email": email,
                    "password": password,
                    "password_confirmation": password_confirmation,
                    "role": role,
                },
            )
            response.raise_for_status()
            return response.json()

    @mcp.tool()
    async def login_user(email: str, password: str) -> dict:
        """
        Login with email and password.

        Args:
            email: User's email address
            password: User's password

        Returns:
            Login response with auth token and user details
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/auth/login",
                data={  # Send as form-data
                    "email": email,
                    "password": password,
                },
            )
            response.raise_for_status()
            return response.json()

    return mcp


def setup_mcp(app: FastAPI) -> None:
    """
    Setup and mount the MCP server to the FastAPI application.

    This will expose all API endpoints as MCP tools accessible at /mcp endpoint.

    Args:
        app: The FastAPI application instance

    Note:
        - MCP endpoint is intended for internal use (server-to-server)
        - Should not be exposed via reverse proxy in production
        - Accessible at: http://api:8000/mcp (Docker internal network)
        - MUST call get_mcp_lifespan() in FastAPI lifespan for proper initialization
    """
    global _mcp_http_app

    # Create MCP server from FastAPI app
    mcp = create_mcp_server(app)

    # Get the MCP HTTP app
    _mcp_http_app = mcp.http_app()

    # Mount the MCP HTTP app at /mcp
    # This makes the MCP server accessible via HTTP at the /mcp path
    app.mount("/mcp", _mcp_http_app)

    print("✓ MCP server mounted at /mcp endpoint")
    print("  All FastAPI endpoints are now exposed as MCP tools")
    print("  Access via: http://api:8000/mcp (internal network)")
    print("  IMPORTANT: MCP lifespan must be integrated in FastAPI lifespan")


def get_mcp_lifespan():
    """
    Get the MCP HTTP app's lifespan context manager.

    Returns:
        The MCP app's lifespan context manager, or None if MCP not initialized

    Usage in FastAPI lifespan:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Your startup code
            ...

            # Start MCP lifespan
            mcp_lifespan = get_mcp_lifespan()
            if mcp_lifespan:
                async with mcp_lifespan(app):
                    yield
            else:
                yield

            # Your shutdown code
            ...
    """
    global _mcp_http_app
    return getattr(_mcp_http_app, 'lifespan', None) if _mcp_http_app else None
