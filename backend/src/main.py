"""
Main FastAPI application entry point.
Initializes the app, registers routers, and configures middleware.
"""
import logging
import logging.config
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
import time

from src.config import settings
from src.database import init_db, engine
from src.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    integrity_error_handler,
    generic_exception_handler,
)
from src.mcp import setup_mcp, get_mcp_lifespan

# Import all models first to ensure SQLAlchemy relationships are properly configured
# Import order matters: base models first, then models with foreign keys
from src.auth.models import User, UserRole  # noqa: F401
from src.geographic.models import Country, City  # noqa: F401
from src.companies.models import Company, AdminCompany  # noqa: F401
from src.addresses.models import Address, OperatingMode, OperatingHour, StudioClosure, Equipment, EquipmentType, Badge  # noqa: F401
from src.rooms.models import Room  # noqa: F401
from src.bookings.models import Booking  # noqa: F401
from src.messages.models import Message  # noqa: F401
from src.payments.models import Charge, Payout, SquareLocation, SquareToken  # noqa: F401
from src.devices.models import Device, DeviceLog, DeviceUnlockSession  # noqa: F401
from src.support.models import SupportTicket  # noqa: F401

# Import routers
from src.auth.router import router as auth_router  # Custom Laravel-compatible auth
from src.auth.sms_router import router as sms_auth_router  # SMS authentication
# from src.auth.router_fastapi_users import router as auth_router  # FastAPI Users (disabled)

# Configure logging
logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    Integrates MCP server lifespan for proper initialization.
    """
    # Startup
    logger.info("Starting up application...")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Debug mode: {settings.debug}")

    # Initialize database (optional - Alembic is recommended)
    if settings.app_env == "development" and settings.debug:
        # await init_db()  # Uncomment to auto-create tables (not recommended for prod)
        logger.info("Database initialization skipped (use Alembic migrations)")

    # Initialize Sentry (if configured)
    if settings.sentry_dsn:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.app_env,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=0.1 if settings.app_env == "production" else 1.0,
        )
        logger.info("Sentry initialized")

    # Integrate MCP lifespan (if MCP server is configured)
    mcp_lifespan = get_mcp_lifespan()
    if mcp_lifespan:
        logger.info("Starting MCP server lifespan...")
        async with mcp_lifespan(app):
            yield
    else:
        yield

    # Shutdown
    logger.info("Shutting down application...")

    # Close Redis connection
    from src.database import close_redis
    await close_redis()
    logger.info("Redis connection closed")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Studio booking platform API built with FastAPI",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Store settings in app state
app.state.settings = settings

# Add proxy headers middleware (must be first to handle X-Forwarded-* headers)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# Add session middleware for admin authentication
app.add_middleware(SessionMiddleware, secret_key=settings.admin_secret_key)

# Setup SQLAdmin
from src.admin import setup_admin
admin = setup_admin(app, engine)


# Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.app_env,
        "version": "1.0.0",
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Funny How API",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
    }


# Laravel-compatible operation-modes endpoint
@app.get(f"{settings.api_prefix}/operation-modes", tags=["Operating Hours"])
async def get_operation_modes():
    """
    Get all operation modes (Laravel-compatible endpoint).

    Returns all available operating modes: 24/7, Fixed Hours, Variable Hours.
    """
    from src.operating_hours.dependencies import get_operating_hours_service
    from src.operating_hours.schemas import OperatingModeResponse

    # Get service instance
    from src.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        from src.operating_hours.repository import OperatingHoursRepository
        from src.operating_hours.service import OperatingHoursService

        repository = OperatingHoursRepository(session)
        service = OperatingHoursService(repository)

        modes = await service.get_all_operating_modes()

        # Format modes for frontend (add description field from description_registration)
        formatted_modes = []
        for mode in modes:
            mode_dict = OperatingModeResponse.model_validate(mode).model_dump()
            # Add description field that frontend expects
            mode_dict["description"] = mode_dict.get("description_registration", "")
            formatted_modes.append(mode_dict)

        # Return Laravel-compatible format with data wrapper
        return {
            "success": True,
            "data": formatted_modes,
            "message": "Operating modes retrieved successfully",
            "code": 200
        }


# Register routers
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(sms_auth_router, prefix=settings.api_prefix)

# User router
from src.users.router import router as user_router
app.include_router(user_router, prefix=settings.api_prefix)

# Address router
from src.addresses.router import router as addresses_router, address_router, map_router
from src.addresses.laravel_endpoints import address_laravel_router
app.include_router(addresses_router, prefix=settings.api_prefix)
app.include_router(address_router, prefix=settings.api_prefix)
app.include_router(address_laravel_router, prefix=settings.api_prefix)  # Laravel-compatible address endpoints
app.include_router(map_router, prefix=settings.api_prefix)

# Geographic router
from src.geographic.router import router as geographic_router
app.include_router(geographic_router, prefix=settings.api_prefix)

# Company router
from src.companies.router import router as companies_router, brand_router
app.include_router(companies_router, prefix=settings.api_prefix)
app.include_router(brand_router, prefix=settings.api_prefix)  # Brand creation (POST /api/brand)

# Room router
from src.rooms.router import router as rooms_router, room_router
from src.photos.router import router as photos_router
app.include_router(rooms_router, prefix=settings.api_prefix)
app.include_router(room_router, prefix=settings.api_prefix)  # Laravel-compatible singular /room routes
app.include_router(photos_router, prefix=settings.api_prefix)  # Photo upload management

# Operating Hours router
from src.operating_hours.router import router as operating_hours_router
app.include_router(operating_hours_router, prefix=settings.api_prefix)

# Booking router
from src.bookings.router import router as bookings_router
app.include_router(bookings_router, prefix=settings.api_prefix)

# Payment router
from src.payments.router import router as payments_router
app.include_router(payments_router, prefix=settings.api_prefix)

# My Studios router
from src.my_studios.router import router as my_studios_router
app.include_router(my_studios_router, prefix=settings.api_prefix)

# Badges router
from src.badges.router import router as badges_router
app.include_router(badges_router, prefix=settings.api_prefix)

# Team management router
from src.teams.router import router as teams_router
app.include_router(teams_router, prefix=settings.api_prefix)

# Menu router
from src.menu.router import router as menu_router
app.include_router(menu_router, prefix=settings.api_prefix)

# Messages/Chat router
from src.messages.router import router as messages_router
app.include_router(messages_router, prefix=settings.api_prefix)

# Devices router
from src.devices.router import router as devices_router
app.include_router(devices_router, prefix=settings.api_prefix)

# Downloads router
from src.downloads.router import router as downloads_router
app.include_router(downloads_router, prefix=settings.api_prefix)

# Webhooks router (Stripe, etc.)
from src.webhooks.router import router as webhooks_router
app.include_router(webhooks_router, prefix=settings.api_prefix)

# Support tickets router
from src.support.router import router as support_router
app.include_router(support_router, prefix=settings.api_prefix)


# Setup MCP server (Model Context Protocol)
# IMPORTANT: Must be called AFTER all routers are registered
# This allows FastMCP to access the complete OpenAPI schema with all endpoints
setup_mcp(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_config="logging.ini",
    )
