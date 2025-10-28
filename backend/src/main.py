"""
Main FastAPI application entry point.
Initializes the app, registers routers, and configures middleware.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import time

from src.config import settings
from src.database import init_db
from src.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    integrity_error_handler,
    generic_exception_handler,
)

# Import all models first to ensure SQLAlchemy relationships are properly configured
# Import order matters: base models first, then models with foreign keys
from src.auth.models import User, UserRole  # noqa: F401
from src.geographic.models import Country, City  # noqa: F401
from src.companies.models import Company, AdminCompany  # noqa: F401
from src.addresses.models import Address, OperatingHour, StudioClosure, Equipment, EquipmentType, Badge  # noqa: F401
from src.rooms.models import Room  # noqa: F401
from src.bookings.models import Booking  # noqa: F401
from src.messages.models import Message  # noqa: F401
from src.payments.models import Charge, Payout, SquareLocation, SquareToken  # noqa: F401

# Import routers
from src.auth.router import router as auth_router  # Custom Laravel-compatible auth
# from src.auth.router_fastapi_users import router as auth_router  # FastAPI Users (disabled)

# Configure logging
logging.config.fileConfig("logging.ini", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
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

    yield

    # Shutdown
    logger.info("Shutting down application...")


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


# Register routers
app.include_router(auth_router, prefix=settings.api_prefix)

# Address router
from src.addresses.router import router as addresses_router
app.include_router(addresses_router, prefix=settings.api_prefix)

# Geographic router
from src.geographic.router import router as geographic_router
app.include_router(geographic_router, prefix=settings.api_prefix)

# Company router
from src.companies.router import router as companies_router
app.include_router(companies_router, prefix=settings.api_prefix)

# Room router
from src.rooms.router import router as rooms_router
app.include_router(rooms_router, prefix=settings.api_prefix)

# Operating Hours router
from src.operating_hours.router import router as operating_hours_router
app.include_router(operating_hours_router, prefix=settings.api_prefix)

# TODO: Register additional routers as they are implemented
# from src.users.router import router as users_router
# from src.bookings.router import router as bookings_router
# from src.payments.router import router as payments_router
# from src.messages.router import router as messages_router
# from src.teams.router import router as teams_router

# app.include_router(users_router, prefix=settings.api_prefix)
# app.include_router(companies_router, prefix=settings.api_prefix)
# app.include_router(rooms_router, prefix=settings.api_prefix)
# app.include_router(bookings_router, prefix=settings.api_prefix)
# app.include_router(payments_router, prefix=settings.api_prefix)
# app.include_router(messages_router, prefix=settings.api_prefix)
# app.include_router(teams_router, prefix=settings.api_prefix)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_config="logging.ini",
    )
