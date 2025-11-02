"""
MCP (Model Context Protocol) server module.

This module provides MCP server integration for the FastAPI application,
automatically exposing all API endpoints as MCP tools for AI agent interaction.
"""

from .server import create_mcp_server, setup_mcp, get_mcp_lifespan

__all__ = ["create_mcp_server", "setup_mcp", "get_mcp_lifespan"]
