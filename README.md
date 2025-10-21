# Funny How - Studio Booking API (FastAPI)

A modern, high-performance studio booking platform API built with FastAPI, following the Module-Functionality architecture pattern.

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

- **Authentication & Authorization**
  - Email/Password authentication with JWT tokens
  - Google OAuth 2.0 integration
  - Role-based access control (User, Studio Owner, Admin)
  - Email verification and password reset

- **Studio Management**
  - Create, update, and manage studio listings
  - Multi-room support per studio
  - Photo galleries for rooms
  - Equipment and amenity tracking
  - Operating hours and closure management
  - Geolocation-based search

- **Booking System**
  - Real-time availability checking
  - Dynamic pricing based on duration
  - Temporary payment links (30-minute expiry)
  - Booking cancellation with refunds
  - Email notifications for all booking events

- **Payment Processing**
  - Multi-gateway support (Stripe & Square)
  - Secure payment sessions
  - Automated payouts to studio owners
  - Service fee calculation (4%)

- **Messaging**
  - Direct messaging between users and studio owners
  - Booking-context messaging

- **Team Management**
  - Add team members to studios
  - Role-based permissions

## Architecture

This project follows the **Module-Functionality** pattern as described in Amir Lavasani's article "How to Structure Your FastAPI Projects."

### Key Principles:

1. **Self-Contained Modules**: Each domain (auth, users, bookings, etc.) is a complete package
2. **Clear Separation of Concerns**: router → service → database
3. **Dependency Injection**: FastAPI's DI system for database sessions, auth, etc.
4. **Type Safety**: Full typing with Pydantic models and SQLAlchemy 2.0

### Module Structure:

Each module contains:
- `router.py` - API endpoints
- `schemas.py` - Pydantic models for request/response validation
- `models.py` - SQLAlchemy database models
- `service.py` - Business logic
- `dependencies.py` - FastAPI dependencies (auth, permissions, etc.)
- `exceptions.py` - Module-specific exceptions (if needed)
- `utils.py` - Helper functions (if needed)

## Tech Stack

- **Framework**: FastAPI 0.109+
- **Python**: 3.11+
- **Database**: PostgreSQL 15+ with asyncpg
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose) + OAuth (Authlib)
- **Task Queue**: Celery with RabbitMQ
- **Caching**: Redis
- **Payment Gateways**: Stripe, Square
- **Cloud Storage**: AWS S3 (boto3)
- **Email**: aiosmtplib
- **Testing**: pytest, pytest-asyncio
- **Code Quality**: black, ruff, mypy

## Project Structure

```
new_backend/
├── src/
│   ├── auth/                  # Authentication & user management
│   │   ├── __init__.py
│   │   ├── router.py         # Auth endpoints
│   │   ├── schemas.py        # Request/response models
│   │   ├── models.py         # User database model
│   │   ├── service.py        # Auth business logic
│   │   └── dependencies.py   # Auth dependencies
│   ├── users/                 # User profile management
│   ├── companies/             # Company/business entities
│   ├── addresses/             # Studio locations
│   ├── rooms/                 # Bookable rooms/spaces
│   ├── bookings/              # Reservation system
│   ├── payments/              # Payment processing
│   ├── messages/              # Direct messaging
│   ├── teams/                 # Team member management
│   ├── geographic/            # Countries, cities
│   ├── tasks/                 # Celery background tasks
│   │   ├── celery_app.py     # Celery configuration
│   │   ├── email.py          # Email tasks
│   │   ├── booking.py        # Booking tasks
│   │   └── payment.py        # Payment tasks
│   ├── config.py              # Application settings
│   ├── database.py            # Database configuration
│   ├── exceptions.py          # Global exception handlers
│   ├── models.py              # Base models and mixins
│   └── main.py                # FastAPI app entry point
├── alembic/                   # Database migrations
│   ├── versions/              # Migration files
│   ├── env.py                 # Alembic environment
│   └── script.py.mako         # Migration template
├── tests/                     # Test suite
│   ├── auth/
│   ├── users/
│   ├── bookings/
│   └── ...
├── templates/                 # Email templates (Jinja2)
├── requirements/              # Python dependencies
│   ├── base.txt              # Core dependencies
│   ├── dev.txt               # Development tools
│   └── prod.txt              # Production requirements
├── dev.yml                    # Docker Compose (development)
├── prod.yml                   # Docker Compose (production)
├── Dockerfile.dev             # Development Dockerfile
├── Dockerfile                 # Production Dockerfile
├── Makefile                   # Automation commands
├── alembic.ini                # Alembic configuration
├── logging.ini                # Logging configuration
├── .env                       # Environment variables
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development without Docker)
- PostgreSQL 15+ (if running locally)
- Redis (if running locally)
- RabbitMQ (if running locally)

### Quick Start with Docker (Recommended)

1. **Clone the repository**
   ```bash
   cd new_backend
   ```

2. **Configure environment variables**
   ```bash
   # Edit .env file with your credentials
   nano .env
   ```

   At minimum, update:
   - `SECRET_KEY` (generate a secure random key)
   - `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` (for OAuth)
   - `STRIPE_API_KEY` and `STRIPE_CLIENT_ID` (for payments)
   - `SQUARE_*` credentials (if using Square)
   - `AWS_*` credentials (for file uploads)
   - `SMTP_*` settings (for emails)

3. **Build and start services**
   ```bash
   make dev-build
   ```

   This will:
   - Build Docker images
   - Start PostgreSQL, Redis, RabbitMQ
   - Start FastAPI app with hot reload
   - Start Celery worker

4. **Run database migrations**
   ```bash
   make upgrade
   ```

5. **Access the application**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - RabbitMQ Management: http://localhost:15672 (guest/guest)

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

```bash
make help          # Show all available commands
make dev           # Run development server
make dev-build     # Build and run development server
make prod          # Run production server
make test          # Run all tests
make clean         # Stop and remove all containers
make migrate       # Create new migration (use: make migrate message="add users table")
make upgrade       # Apply all migrations
make downgrade     # Rollback last migration
make shell         # Open Python shell
make db-shell      # Open PostgreSQL shell
make format        # Format code with black
make lint          # Run linting checks
make logs          # View API logs
make restart       # Restart API container
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

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user info
- `GET /api/auth/google/redirect` - Google OAuth redirect
- `GET /api/auth/google/callback` - Google OAuth callback

#### Users
- `GET /api/user/me` - Get user profile
- `PUT /api/user/update` - Update profile
- `POST /api/user/set-role` - Set user role

#### Studios (Addresses)
- `GET /api/address/list` - List my studios
- `POST /api/address/add-studio` - Create studio
- `GET /api/address/studio/{slug}` - Get studio by slug
- `POST /api/address/toggle-favorite-studio` - Toggle favorite

#### Rooms
- `POST /api/room/add-room` - Create room
- `POST /api/room/{id}/prices` - Set room prices
- `POST /api/room/reservation` - Book a room

#### Bookings
- `GET /api/booking-management` - Get future bookings
- `GET /api/history` - Get booking history
- `POST /api/room/cancel-booking` - Cancel booking

#### Payments
- `POST /api/user/payment/stripe/create-account` - Create Stripe account
- `GET /api/user/payment/stripe/balance` - Get balance
- `POST /api/create-payout` - Create payout

## Environment Variables

See `.env` file for all configuration options. Key variables:

```bash
# Application
APP_NAME="Funny How - Studio Booking API"
APP_ENV=development
DEBUG=true
SECRET_KEY=<generate-secure-key>

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# OAuth
GOOGLE_CLIENT_ID=<your-client-id>
GOOGLE_CLIENT_SECRET=<your-client-secret>

# Payments
STRIPE_API_KEY=sk_test_...
SQUARE_APPLICATION_ID=<your-app-id>

# AWS
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_BUCKET_NAME=<your-bucket>

# Email
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=<username>
SMTP_PASSWORD=<password>
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting: `make test && make lint`
4. Format code: `make format`
5. Create a pull request

## License

Proprietary - All rights reserved

## Support

For issues and questions, please contact the development team or create an issue in the repository.

---

Built with ❤️ using FastAPI and the Module-Functionality architecture pattern.
