# Funny How - Studio Booking Platform

A modern, high-performance studio booking platform with FastAPI backend, Nuxt 3 frontend, and real-time chat. Built with clean architecture principles and production-grade patterns.

> **Multi-Backend Architecture**: This platform includes both a **FastAPI backend (current/active)** and a **Laravel 9 legacy backend** for backward compatibility during migration.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Environment Variables](#environment-variables)

## Features

### 🔐 **Authentication & Authorization**
- Email/Password authentication with JWT tokens (Laravel Sanctum-compatible)
- Google OAuth 2.0 integration
- Role-based access control (User, Studio Owner, Admin)
- Email verification and password reset
- Multi-device session management

### 🏢 **Studio Management**
- Complete studio lifecycle management (create, update, publish)
- **Smart Completion System**: Studios must configure operating hours + payment gateway before going live
- Multi-room support with individual pricing
- Photo galleries with GCS storage and proxy serving
- Badge/amenity system (mixing, recording, rental services)
- **Three Operating Modes**:
  - Mode 1: 24/7 operation
  - Mode 2: Fixed daily hours
  - Mode 3: Variable hours per day of week
- Geolocation-based search with timezone support
- Slug-based URLs for SEO
- Studio visibility filtering (only complete studios show in public search)

### 📅 **Advanced Booking System**
- Real-time availability checking with timezone awareness
- Operating hours validation
- Conflict detection (excludes cancelled/expired bookings)
- Dynamic pricing based on duration
- Multi-day booking support
- Temporary payment links (30-minute expiry)
- Booking cancellation with automated refunds
- Email notifications for all booking events
- Booking status tracking (pending, confirmed, cancelled, expired, completed)

### 💳 **Payment Gateway Integration**
- **Multi-gateway support**: Stripe Connect & Square
- **Payout Verification**: Real-time checks via Stripe API (`payouts_enabled` validation)
- Secure payment sessions with automatic expiry
- Automated payouts to studio owners
- Service fee calculation (4%)
- Payment gateway caching to avoid rate limits
- Stripe Connect OAuth onboarding flow

### 💬 **Real-Time Messaging**
- Socket.io-powered chat service
- Direct messaging between users and studio owners
- Booking-context messaging
- Redis-backed message storage

### 👥 **Team Management**
- Add team members/engineers to studios
- Role-based permissions
- Admin company structure

### 🗺️ **Geographic & Discovery**
- City/country-based filtering
- Map view with complete studios only
- Public search with smart filtering
- Owner dashboard (all studios, including incomplete)

## Architecture

This project follows the **Module-Functionality** pattern with clear separation of concerns and production-grade patterns.

### 🏗️ **Overall System Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                         Caddy (Reverse Proxy)                   │
│                    http://127.0.0.1 or localhost                │
└──────────────┬──────────────────────────────┬───────────────────┘
               │                              │
               ▼                              ▼
    ┌──────────────────┐          ┌──────────────────────┐
    │  Nuxt 3 Frontend │          │   FastAPI Backend    │
    │   (Port 3000)    │◄────────►│    (Port 8000)       │
    │  Feature-Sliced  │  Axios   │  Module-Functionality│
    └──────────────────┘          └──────────┬───────────┘
                                              │
                        ┌─────────────────────┼───────────────────┐
                        ▼                     ▼                   ▼
                ┌───────────────┐   ┌─────────────────┐  ┌─────────────┐
                │  PostgreSQL   │   │  Google Cloud   │  │   Stripe    │
                │  (Port 5432)  │   │    Storage      │  │  Connect    │
                └───────────────┘   └─────────────────┘  └─────────────┘
                        ▲
                        │
              ┌─────────┴──────────┐
              ▼                    ▼
      ┌──────────────┐    ┌──────────────────┐
      │    Redis     │    │  Socket.io Chat  │
      │ (Port 6379)  │    │   (Port 6001)    │
      └──────────────┘    └──────────────────┘
              ▲
              │
      ┌───────┴──────────┐
      │   Celery Worker  │
      │   + RabbitMQ     │
      └──────────────────┘
```

### 🔧 **Backend Architecture (FastAPI)**

**Layer Flow:** `Router → Service → Repository → Models → Database`

#### Key Principles:

1. **Self-Contained Modules**: Each domain is a complete package with all layers
2. **Utility-First Design**: Shared logic in `utils.py` (e.g., `addresses/utils.py`)
3. **Dependency Injection**: FastAPI's DI for database, auth, and services
4. **Type Safety**: Full typing with Pydantic and SQLAlchemy 2.0
5. **DRY (Don't Repeat Yourself)**: Centralized utilities prevent code duplication

#### Module Structure:

Each module contains:
- `router.py` - API endpoints (thin, delegates to service)
- `schemas.py` - Pydantic models for request/response validation
- `models.py` - SQLAlchemy database models
- `service.py` - Business logic layer
- `repository.py` - Data access layer (database queries only)
- `dependencies.py` - FastAPI dependencies (auth, permissions, etc.)
- `exceptions.py` - Module-specific exceptions (optional)
- `constants.py` - Module constants (optional)
- `utils.py` - Shared utility functions (optional, but recommended)

#### Example: Studio Completion Utility Pattern

```python
# addresses/utils.py - Centralized business logic
def is_studio_complete(address: Address) -> bool:
    """Check if studio is ready for public visibility."""
    has_hours = len(address.operating_hours) > 0
    has_payment = has_payment_gateway_connected(address)
    return has_hours and has_payment

# Used in multiple endpoints
from src.addresses.utils import is_studio_complete, build_studio_dict

# Public search endpoint - filters by completion
if should_show_in_public_search(address):
    studios.append(build_studio_dict(address))

# Owner dashboard - shows all studios with status
studio_dict = build_studio_dict(address, include_is_complete=True)
```

### 🎨 **Frontend Architecture (Nuxt 3)**

**Feature-Sliced Design (FSD)** methodology:

```
src/
├── app/          # Application initialization, config
├── pages/        # Page components (routes)
├── widgets/      # Independent page blocks (TimeSelect, PhotoSwipe)
├── features/     # Business scenarios (BookingForm, DatePicker)
├── entities/     # Business entities (Studio, Room, User)
└── shared/       # Reusable UI components (UI-kit)
```

### 💾 **Data Flow Example: Studio Search**

```
User searches in city → Frontend (Nuxt)
                          ↓
                     GET /api/city/11/studios
                          ↓
              geographic/router.py (thin)
                          ↓
              addresses/service.py
                          ↓
              addresses/repository.py
                          ↓
                      PostgreSQL
                          ↓
              ← Address models with relationships
                          ↓
              addresses/utils.py (filtering & transformation)
                - Check operating hours
                - Verify Stripe payouts via API (with caching)
                - Transform photos to proxy URLs
                - Transform badges to proxy URLs
                          ↓
              ← Filtered, standardized studio dicts
                          ↓
              Laravel-compatible JSON response
                          ↓
              Frontend renders StudioCard components
```

## Tech Stack

### Backend (FastAPI)
- **Framework**: FastAPI 0.109+
- **Python**: 3.12+
- **Database**: PostgreSQL 16 with asyncpg
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose) + Google OAuth (Authlib)
- **Task Queue**: Celery 5.3 with RabbitMQ 3.13
- **Caching**: Redis 7.0
- **Payment Gateways**: Stripe Connect, Square
- **Cloud Storage**: Google Cloud Storage (GCS)
- **Media Proxy**: Custom GCS proxy endpoints
- **Email**: aiosmtplib
- **Testing**: pytest, pytest-asyncio
- **Code Quality**: black, ruff

### Frontend
- **Framework**: Nuxt 3
- **Architecture**: Feature-Sliced Design (FSD)
- **UI Library**: Tailwind CSS
- **State Management**: Pinia
- **HTTP Client**: Axios
- **Maps**: Google Maps API
- **Real-time**: Socket.io client

### Infrastructure
- **Reverse Proxy**: Caddy 2
- **Containerization**: Docker & Docker Compose
- **Development**: dev.yml (hot reload)
- **Production**: prod.yml (optimized)

### Legacy
- **Laravel**: Laravel 9 (PHP backend, being phased out)

## Project Structure

```
funny-how/
├── backend/                   # FastAPI Backend (Current)
│   ├── src/
│   │   ├── auth/              # Authentication & JWT tokens
│   │   ├── users/             # User profile + payment gateway info
│   │   ├── companies/         # Studio businesses
│   │   ├── addresses/         # Studio locations + operating hours
│   │   │   └── utils.py       # ⭐ Studio visibility & completion logic
│   │   ├── rooms/             # Bookable spaces with pricing
│   │   ├── bookings/          # Reservation + availability system
│   │   ├── operating_hours/   # 3-mode operating hours (24/7, fixed, variable)
│   │   ├── payments/          # Multi-gateway (Stripe, Square)
│   │   ├── my_studios/        # Owner dashboard endpoints
│   │   ├── messages/          # Direct messaging
│   │   ├── teams/             # Studio team members
│   │   ├── geographic/        # Countries, cities, public search
│   │   ├── badges/            # Studio amenities
│   │   ├── tasks/             # Celery background tasks
│   │   ├── config.py          # Application settings
│   │   ├── database.py        # PostgreSQL async connection
│   │   ├── storage.py         # ⭐ Google Cloud Storage integration
│   │   ├── gcs_utils.py       # ⭐ GCS proxy URL generation
│   │   ├── exceptions.py      # Custom exceptions
│   │   ├── models.py          # Base models & mixins
│   │   └── main.py            # FastAPI app entry point
│   ├── alembic/               # Database migrations
│   │   └── versions/          # Migration history
│   ├── tests/                 # Test suite
│   ├── Dockerfile             # Production image
│   ├── requirements.txt       # Python dependencies
│   └── alembic.ini            # Migration config
├── frontend/
│   ├── client/                # Nuxt 3 Frontend
│   │   ├── src/
│   │   │   ├── app/           # App initialization
│   │   │   ├── pages/         # Page routes
│   │   │   ├── widgets/       # Complex UI (TimeSelect, PhotoSwipe)
│   │   │   ├── features/      # Business features (BookingForm)
│   │   │   ├── entities/      # Business entities (Studio, Room)
│   │   │   └── shared/        # Reusable UI components
│   │   ├── pages/             # Nuxt page files
│   │   ├── nuxt.config.ts     # Nuxt configuration
│   │   └── package.json       # Node dependencies
│   └── chat/                  # Socket.io Chat Service
│       ├── index.js           # Express + Socket.io server
│       └── package.json       # Chat dependencies
├── laravel/                   # Laravel 9 Backend (Legacy)
│   ├── app/                   # Laravel application
│   ├── routes/                # API routes
│   └── database/              # Migrations & seeders
├── caddy/                     # Reverse Proxy Config
│   └── Caddyfile              # Routing rules
├── dev.yml                    # Docker Compose (Development)
├── prod.yml                   # Docker Compose (Production)
├── Makefile                   # ⭐ Root-level commands
├── .env                       # Environment variables
├── CLAUDE.md                  # ⭐ AI Assistant Instructions
└── README.md                  # This file

⭐ = Key files with critical business logic
```

### Key Directories Explained

**`backend/src/addresses/utils.py`**: Core studio business logic
- `is_studio_complete()` - Completion validation
- `should_show_in_public_search()` - Visibility filtering
- `build_studio_dict()` - Standardized response builder
- `check_stripe_payouts_enabled()` - Payment gateway verification

**`backend/src/storage.py` & `gcs_utils.py`**: Media management
- GCS upload/download
- Proxy URL generation for photos and badges
- Private file serving through backend

**`frontend/client/src/`**: Feature-Sliced Design
- `pages/` - Next.js style routing
- `widgets/` - Composite UI components
- `features/` - Business feature implementations
- `entities/` - Domain models and API clients
- `shared/` - Reusable UI kit

## Getting Started

### Prerequisites

- **Docker & Docker Compose** (required)
- **Python 3.12+** (for local development without Docker)
- **PostgreSQL 16+** (if running locally)
- **Redis 7.0** (if running locally)
- **RabbitMQ 3.13** (if running locally)
- **Node.js 18+** (for frontend development)

### Quick Start with Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd funny-how
   ```

2. **Configure environment variables**
   ```bash
   # Copy example and edit
   cp .env.example .env
   nano .env
   ```

   **Critical variables to configure:**
   ```bash
   # Application
   SECRET_KEY=<generate-with-openssl-rand-hex-32>

   # Database (PostgreSQL 16)
   POSTGRES_DB=book_studio
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=<your-secure-password>

   # Google OAuth
   GOOGLE_CLIENT_ID=<your-client-id>
   GOOGLE_CLIENT_SECRET=<your-client-secret>

   # Stripe Connect
   STRIPE_API_KEY=sk_test_...
   STRIPE_PUBLIC_KEY=pk_test_...

   # Google Cloud Storage
   GCS_BUCKET_NAME=<your-bucket>
   GCS_PROJECT_ID=<your-project-id>
   GCS_CREDENTIALS_PATH=/path/to/credentials.json

   # Email (SMTP)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=<your-email>
   SMTP_PASSWORD=<app-password>
   ```

3. **Build and start all services**
   ```bash
   make dev-build
   # Or manually:
   docker compose -f dev.yml up -d --build
   ```

   This starts:
   - ✅ Caddy (reverse proxy)
   - ✅ FastAPI backend (with hot reload)
   - ✅ Nuxt 3 frontend (with hot reload)
   - ✅ PostgreSQL 16
   - ✅ Redis 7.0
   - ✅ RabbitMQ 3.13
   - ✅ Celery worker
   - ✅ Socket.io chat service

4. **Run database migrations**
   ```bash
   make migrate
   # Or manually:
   docker compose -f dev.yml exec api alembic upgrade head
   ```

5. **Access the application**
   - **Main App**: http://127.0.0.1 or http://localhost
   - **API Backend**: http://127.0.0.1/api
   - **API Docs (Swagger)**: http://127.0.0.1/docs
   - **Frontend Dev Server**: http://localhost:3000
   - **RabbitMQ Management**: http://localhost:15672 (guest/guest)
   - **PostgreSQL**: localhost:5432
   - **Redis**: localhost:6379

### Local Development (Without Docker)

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   make install
   ```

3. **Set up PostgreSQL database**
   ```bash
   createdb book_studio
   ```

4. **Update .env for local setup**
   ```bash
   DATABASE_URL=postgresql://yourusername:yourpassword@localhost:5432/book_studio
   REDIS_URL=redis://localhost:6379/0
   RABBITMQ_URL=amqp://guest:guest@localhost:5672/
   ```

5. **Run migrations**
   ```bash
   make upgrade-local
   ```

6. **Start the application**
   ```bash
   uvicorn src.main:app --reload
   ```

7. **Start Celery worker (separate terminal)**
   ```bash
   celery -A src.tasks.celery_app worker --loglevel=info
   ```

## Development

### Available Make Commands

#### Development
```bash
make dev-build          # Build and start all services with hot reload
make dev-detach         # Run development in background
make stop               # Stop all services
make restart            # Restart API container
make clean              # Remove all containers and volumes
make status             # Show container status
```

#### Database & Migrations (FastAPI)
```bash
make migrate            # Apply migrations (alembic upgrade head)
make migrate-create message="description"  # Create new migration
make migrate-down       # Rollback last migration
make migrate-history    # Show migration history
make db-shell           # Open PostgreSQL shell
```

#### Code Quality
```bash
make format             # Format code with black and ruff
make lint               # Run linting checks
make test               # Run tests with coverage
make test-verbose       # Run with verbose output
```

#### Logs & Debugging
```bash
make logs               # View API logs
make logs-all           # View all service logs
make logs container=<name>  # View specific container logs
make shell              # Open Python shell in API container
```

#### Frontend
```bash
make update-frontend    # Restart frontend container
make npm-install        # Install npm dependencies
make npm-install-package p=<package>  # Install specific package
```

#### Laravel (Legacy - being phased out)
```bash
make composer           # Install PHP dependencies
make swagger            # Generate Swagger documentation
make artisan c="<command>"  # Run artisan command
```

### Creating a New Module

1. **Create module directory**
   ```bash
   mkdir src/my_module
   touch src/my_module/__init__.py
   ```

2. **Create module files**
   ```bash
   touch src/my_module/{router.py,schemas.py,models.py,service.py,dependencies.py}
   ```

3. **Define models** in `models.py`
   ```python
   from src.database import Base
   from src.models import IDMixin, TimestampMixin
   from sqlalchemy.orm import Mapped, mapped_column
   from sqlalchemy import String

   class MyModel(Base, IDMixin, TimestampMixin):
       __tablename__ = "my_models"
       name: Mapped[str] = mapped_column(String(100), nullable=False)
   ```

4. **Define schemas** in `schemas.py`
   ```python
   from pydantic import BaseModel

   class MyModelCreate(BaseModel):
       name: str

   class MyModelResponse(BaseModel):
       id: int
       name: str
       model_config = {"from_attributes": True}
   ```

5. **Create service** in `service.py`
   ```python
   from sqlalchemy.ext.asyncio import AsyncSession
   from sqlalchemy import select
   from .models import MyModel

   class MyModelService:
       async def create(self, db: AsyncSession, name: str) -> MyModel:
           model = MyModel(name=name)
           db.add(model)
           await db.commit()
           await db.refresh(model)
           return model
   ```

6. **Create router** in `router.py`
   ```python
   from fastapi import APIRouter, Depends
   from sqlalchemy.ext.asyncio import AsyncSession
   from src.database import get_db
   from . import schemas, service

   router = APIRouter(prefix="/my-module", tags=["My Module"])

   @router.post("/", response_model=schemas.MyModelResponse)
   async def create(
       data: schemas.MyModelCreate,
       db: AsyncSession = Depends(get_db),
   ):
       return await service.MyModelService().create(db, data.name)
   ```

7. **Register router** in `src/main.py`
   ```python
   from src.my_module.router import router as my_module_router
   app.include_router(my_module_router, prefix=settings.api_prefix)
   ```

8. **Create migration**
   ```bash
   make migrate message="add my_module"
   make upgrade
   ```

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
docker-compose -f dev.yml exec api pytest tests/auth/test_router.py -v

# Run with coverage report
docker-compose -f dev.yml exec api pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Type checking
mypy src/
```

## Testing

Create tests in the `tests/` directory mirroring the `src/` structure:

```python
# tests/auth/test_service.py
import pytest
from src.auth.service import auth_service

@pytest.mark.asyncio
async def test_register_user(db_session):
    user = await auth_service.register_user(
        db_session,
        email="test@example.com",
        password="testpass123",
        firstname="Test",
        lastname="User"
    )
    assert user.email == "test@example.com"
    assert user.is_active is True
```

## Deployment

### Production Deployment with Docker

1. **Update production environment**
   ```bash
   # Create .env for production with secure values
   cp .env .env.prod
   nano .env.prod
   ```

2. **Build production images**
   ```bash
   make build-prod
   ```

3. **Deploy**
   ```bash
   make prod-detach
   ```

4. **Run migrations**
   ```bash
   docker-compose -f prod.yml exec api alembic upgrade head
   ```

### Environment-Specific Settings

- Development: `APP_ENV=development`, `DEBUG=true`
- Production: `APP_ENV=production`, `DEBUG=false`

## API Documentation

### Interactive API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication

Most endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Key Endpoints

> Full API documentation available at http://127.0.0.1/docs when running

#### 🔐 Authentication
```http
POST   /api/auth/register           # Register new user
POST   /api/auth/login              # Login and get JWT token
GET    /api/auth/me                 # Get current user info
GET    /api/auth/google/redirect    # Google OAuth redirect
GET    /api/auth/google/callback    # Google OAuth callback
POST   /api/auth/verify-email       # Verify email address
```

#### 👤 User Profile
```http
GET    /api/user/me                 # Get user profile
PUT    /api/user/update             # Update profile
POST   /api/user/set-role           # Set user role (user/studio_owner)
```

#### 🏢 Studio Management (Owner Dashboard)
```http
POST   /api/my-studios/filter       # List/filter owner's studios (with is_complete status)
GET    /api/my-studios/cities       # Get cities where owner has studios
GET    /api/my-studios/              # Get all owner's studios
```

#### 🗺️ Public Studio Search
```http
GET    /api/city/{city_id}/studios  # Search studios by city (only complete studios)
GET    /api/map/studios              # Get studios for map view (only complete studios)
GET    /api/address/studio/{slug}    # Get studio details by slug (public + owner view)
```

#### 📍 Addresses (Studio Locations)
```http
POST   /api/addresses/add-studio    # Create new studio
GET    /api/addresses/{id}          # Get studio by ID
PATCH  /api/addresses/{id}          # Update studio
DELETE /api/addresses/{id}          # Delete studio
POST   /api/addresses/{id}/publish  # Publish studio (requires completion)
```

#### ⏰ Operating Hours
```http
GET    /api/address/operating-hours?address_id={id}  # Get operating hours
POST   /api/address/operating-hours                   # Set operating hours (3 modes)
```

#### 🎨 Badges & Amenities
```http
GET    /api/address/{id}/badges     # Get all badges (all_badges + taken_badges)
POST   /api/address/{id}/badge      # Toggle badge for studio
```

#### 🏠 Rooms
```http
POST   /api/room/add-room           # Create room in studio
POST   /api/room/{id}/prices        # Set room pricing tiers
GET    /api/room/{id}               # Get room details
```

#### 📅 Bookings & Availability
```http
GET    /api/address/reservation/start-time?room_id={id}&date={YYYY-MM-DD}
       # Get available start times for a room on a specific date

GET    /api/address/reservation/end-time?room_id={id}&date={YYYY-MM-DD}&start_time={HH:MM}
       # Get available end times from a given start time

POST   /api/room/reservation        # Book a room
GET    /api/booking-management      # Get future bookings
GET    /api/history                 # Get booking history
POST   /api/room/cancel-booking     # Cancel booking
```

#### 💳 Payments (Stripe Connect & Square)
```http
POST   /api/user/payment/stripe/create-account       # Create Stripe Connect account
GET    /api/user/payment/stripe/balance              # Get balance
POST   /api/create-payout                            # Create payout to studio owner
GET    /api/payment/stripe/connect                   # Stripe OAuth onboarding
```

#### 🖼️ Media Proxy Endpoints
```http
GET    /api/photos/image/{path}    # Serve photos through backend (GCS proxy)
GET    /api/badges/image/{path}    # Serve badges through backend (GCS proxy)
```

**Note**: Most endpoints require authentication via `Authorization: Bearer {user_id}|{jwt_token}` header (Laravel Sanctum-compatible format)

## Environment Variables

See `.env` file for all configuration options. **Critical variables:**

```bash
# ==================== Application ====================
APP_NAME="Funny How Studio Booking"
APP_ENV=development                    # development | production
DEBUG=true                             # false in production
SECRET_KEY=<openssl-rand-hex-32>       # REQUIRED: JWT signing key

# ==================== Database ====================
POSTGRES_HOST=db                       # Docker service name
POSTGRES_PORT=5432
POSTGRES_DB=book_studio
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<secure-password>

# SQLAlchemy connection (auto-constructed)
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# ==================== Redis ====================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://${REDIS_HOST}:${REDIS_PORT}/0

# ==================== RabbitMQ (Celery) ====================
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
CELERY_BROKER_URL=amqp://${RABBITMQ_USER}:${RABBITMQ_PASS}@${RABBITMQ_HOST}:${RABBITMQ_PORT}//

# ==================== Google OAuth 2.0 ====================
GOOGLE_CLIENT_ID=<your-client-id>.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=<your-client-secret>
GOOGLE_REDIRECT_URI=http://127.0.0.1/api/auth/google/callback

# ==================== Stripe Connect ====================
STRIPE_API_KEY=sk_test_...             # Secret key from Stripe Dashboard
STRIPE_PUBLIC_KEY=pk_test_...          # Publishable key from Stripe Dashboard
STRIPE_WEBHOOK_SECRET=whsec_...        # Webhook signing secret

# ==================== Square (Optional) ====================
SQUARE_APPLICATION_ID=<your-app-id>
SQUARE_ACCESS_TOKEN=<your-access-token>
SQUARE_ENVIRONMENT=sandbox             # sandbox | production

# ==================== Google Cloud Storage ====================
GCS_BUCKET_NAME=<your-gcs-bucket>
GCS_PROJECT_ID=<your-gcp-project-id>
GCS_CREDENTIALS_PATH=/path/to/service-account-key.json

# ==================== Email (SMTP) ====================
SMTP_HOST=smtp.gmail.com               # Or your SMTP provider
SMTP_PORT=587                          # TLS port
SMTP_USERNAME=<your-email@gmail.com>
SMTP_PASSWORD=<app-password>           # Generate app password for Gmail
SMTP_FROM=<noreply@yourdomain.com>

# ==================== Frontend (Nuxt) ====================
AXIOS_BASEURL=http://nginx             # Internal Docker network
AXIOS_BASEURL_CLIENT=http://127.0.0.1  # External client URL
AXIOS_API_VERSION=/api                 # API prefix
NUXT_ENV_GOOGLE_MAPS_API=<your-maps-api-key>

# ==================== Service URLs ====================
API_URL=http://127.0.0.1/api
FRONTEND_URL=http://127.0.0.1
```

### Generating Secure Keys

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate app password for Gmail SMTP
# Visit: https://myaccount.google.com/apppasswords
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting: `make test && make lint`
4. Format code: `make format`
5. Create a pull request

## License

Proprietary - All rights reserved

## Recent Updates & Migration Status

### ✅ Completed Features (FastAPI)
- **Studio Completion System**: Studios must configure operating hours + payment gateway before appearing in public search
- **Payment Gateway Verification**: Real-time Stripe API verification of `payouts_enabled` status
- **Media Management**: Google Cloud Storage with proxy endpoints for private serving
- **Utility-First Architecture**: Centralized business logic in `addresses/utils.py`
- **My Studios Dashboard**: Owner-specific endpoints with completion status tracking
- **Public Search Filtering**: Smart filtering ensures only ready studios appear publicly
- **Operating Hours**: 3-mode system (24/7, fixed, variable) with timezone support
- **Booking Availability**: Real-time checking with operating hours validation

### 🚧 Migration from Laravel to FastAPI
The platform is actively migrating from Laravel to FastAPI:

**Status**: ~80% complete
- ✅ Authentication & authorization
- ✅ Studio management
- ✅ Booking system
- ✅ Payment processing (Stripe Connect)
- ✅ Operating hours
- ✅ Media storage (GCS)
- ✅ Real-time chat (Socket.io)
- 🚧 Some legacy endpoints still on Laravel

**Architecture Benefits**:
- 🚀 **Performance**: Async/await for all I/O operations
- 🔒 **Type Safety**: Full Pydantic + SQLAlchemy typing
- 📦 **Code Reuse**: Utility functions eliminate duplication
- 🧹 **Clean Architecture**: Clear layer separation (router → service → repository)
- 🎯 **DRY Principle**: Single source of truth for business logic

### 📚 Documentation

- **For Developers**: See [`CLAUDE.md`](./CLAUDE.md) - Comprehensive guide to architecture, patterns, and troubleshooting
- **For API Users**: Visit http://127.0.0.1/docs when running (Swagger UI)
- **For Frontend**: Feature-Sliced Design structure in `frontend/client/src/`

## Support

For issues and questions:
- **Technical Issues**: Create an issue in the repository
- **Development Questions**: Refer to `CLAUDE.md` for detailed patterns and examples
- **API Questions**: Check interactive docs at `/docs` endpoint

---

**Built with:**
- 🚀 FastAPI (Python 3.12)
- ⚡ Nuxt 3 (Vue 3 + TypeScript)
- 🐘 PostgreSQL 16
- 🔴 Redis 7.0
- 🐰 RabbitMQ + Celery
- ☁️ Google Cloud Storage
- 💳 Stripe Connect
- 🎨 Tailwind CSS

*Following Module-Functionality architecture with Feature-Sliced Design on the frontend.*
