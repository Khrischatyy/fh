# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Funny-how is a studio booking platform with two backend implementations (Laravel legacy + FastAPI new), a Nuxt.js frontend, and a Socket.io chat service. The system uses Docker for containerization with separate dev and production configurations.

## Repository Structure

- `backend/` - FastAPI Python backend (current/preferred)
- `laravel/` - Laravel 9 PHP backend (legacy)
- `frontend/client/` - Nuxt 3 client application
- `frontend/chat/` - Socket.io chat service (Express.js)
- `caddy/` - Caddy reverse proxy configuration

## Development Commands

### Root-Level Commands (Multi-Service)

All root-level commands use the main `Makefile` and affect multiple services:

```bash
# Initial setup
make build              # Build all containers
make start              # Start all services (dev.yml)
make update-dev-container  # Full rebuild: stop, build, composer install, start

# Service management
make stop               # Stop all services
make status             # Show container status
make logs container=<name>  # View specific container logs
make logs-all           # View all container logs

# Laravel backend (backend/)
make composer           # Install PHP dependencies
make migrate            # Run Laravel migrations
make rollback           # Rollback last migration
make seeds              # Run database seeders
make db                 # Full reset: drop, migrate, seed
make swagger            # Generate Swagger documentation
make artisan c="<command>"  # Run artisan command
make queue              # Run queue worker
make optimize           # Clear Laravel caches

# Nginx
make nginx-reload       # Reload nginx configuration

# Frontend (frontend/client/)
make update-frontend    # Restart frontend container
make npm-install        # Install npm dependencies
make npm-install-package p=<package>  # Install specific package
```

### FastAPI Backend (backend/)

Commands are run from the root directory using Docker Compose:

```bash
# Development
make dev-build          # Build and start all services with hot reload
make dev-detach         # Run development in background
make logs               # View API logs
make logs-all           # View all service logs
make restart            # Restart API container

# Database migrations
make migrate            # Apply migrations (alembic upgrade head)
make migrate-create message="description"  # Create new migration
make migrate-down       # Rollback last migration
make migrate-history    # Show migration history

# Testing
make test               # Run tests with coverage
make test-verbose       # Run with verbose output

# Code quality
make format             # Format with black and ruff
make lint               # Run linting checks

# Utilities
make db-shell           # Open PostgreSQL shell
make shell              # Open Python shell
make clean              # Remove all containers and volumes
```

### Frontend Client (frontend/client/)

The Nuxt 3 frontend runs in Docker, but you can also develop locally:

```bash
# Inside container (via Docker)
npm run dev             # Development server (runs automatically)
npm run build           # Build for production
npm run preview         # Preview production build

# Update from root directory
make update-frontend    # Restart frontend container
```

### Production Deployment

```bash
# Using prod.yml
docker compose -f prod.yml up -d --build
docker compose -f prod.yml exec api alembic upgrade head
```

## Architecture

### FastAPI Backend (backend/) - Module-Functionality Pattern

The backend follows a layered architecture with clear separation of concerns:

**Layer Flow:** Router → Service → Repository → Models

**Module Structure:**
```
backend/src/{domain}/
├── router.py          # API endpoints, HTTP handling
├── schemas.py         # Pydantic request/response models
├── models.py          # SQLAlchemy database models
├── service.py         # Business logic
├── repository.py      # Data access layer
└── dependencies.py    # FastAPI dependencies
```

**Key Modules:**
- `auth/` - Authentication & user management (JWT, Google OAuth)
- `users/` - User profile management
- `companies/` - Studio/business entities
- `addresses/` - Studio locations with geolocation and operating hours
- `rooms/` - Bookable spaces with pricing
- `bookings/` - Reservation system with availability checking
- `operating_hours/` - Studio operating hours management (modes: 24/7, fixed, variable)
- `payments/` - Multi-gateway (Stripe, Square) payment processing
- `messages/` - Direct messaging between users and studio owners
- `geographic/` - Countries, cities reference data
- `tasks/` - Celery background tasks (email, bookings, payments)
- `teams/` - Studio team members/engineers

**Important Patterns:**
- Services contain all business logic (slug generation, validation)
- Repositories only handle database queries (no business logic)
- Never access repositories directly from routers
- Use dependency injection for all dependencies
- Routers should be thin - delegate to services

**Database:**
- PostgreSQL 15+ with asyncpg
- SQLAlchemy 2.0 async ORM
- Alembic migrations
- Use `IDMixin` and `TimestampMixin` from `src/models.py`

**Background Tasks:**
- Celery with RabbitMQ for async tasks
- Task modules in `src/tasks/`
- Email notifications, payment processing, booking cleanup

### Bookings Module - Availability System

The bookings module implements a sophisticated availability checking system:

**Key Components:**

1. **Operating Hours (3 Modes):**
   - **Mode 1 (24/7)**: Studio operates 24 hours, 7 days a week
   - **Mode 2 (Fixed)**: Same hours every day
   - **Mode 3 (Variable)**: Different hours per day of week (0=Sunday, 6=Saturday)

2. **Availability Logic:**
   - Checks room operating hours for selected date
   - Excludes existing bookings (except cancelled/expired)
   - Rounds current time up to next hour for today's bookings
   - Returns available slots in 1-hour increments
   - Handles timezone-aware datetime calculations using pytz

3. **API Endpoints:**
   ```
   GET /api/address/reservation/start-time?room_id={id}&date={YYYY-MM-DD}
   - Returns available start times for a room on a specific date
   - Response: {"available_times": [{"time": "10:00", "iso_string": "2025-10-31T10:00:00+01:00"}, ...]}

   GET /api/address/reservation/end-time?room_id={id}&date={YYYY-MM-DD}&start_time={HH:MM}
   - Returns available end times from a given start time
   - Checks for booking conflicts and respects operating hours
   - Response: {"available_times": [{"time": "11:00", "iso_string": "2025-10-31T11:00:00+01:00"}, ...]}
   ```

4. **Models:**
   - `Booking`: room_id, user_id, status_id, date, start_time, end_time, end_date (for multi-day)
   - `BookingStatus`: pending, confirmed, cancelled, expired, completed
   - `OperatingHour` (in addresses module): mode_id, day_of_week, open_time, close_time, is_closed

5. **Type Aliasing:**
   - Uses `from datetime import date as date_type, time as time_type` to avoid Pydantic field name conflicts

**Important Notes:**
- Always use `.path` for photo URLs in frontend, not `.url`
- Frontend TimeSelect component expects `{time, iso_string}` format from backend
- Operating hours are stored in `addresses.operating_hours` relationship
- Bookings exclude `cancelled` and `expired` statuses when checking availability

### Laravel Backend (laravel/) - Legacy

Standard Laravel 9 structure. Prefer using FastAPI backend for new features.

### Nuxt 3 Frontend (frontend/client/)

Follows Feature-Sliced Design (FSD) methodology:

```
src/
├── app/          # Application initialization, config
├── pages/        # Page components (used in pages/ at root)
├── widgets/      # Independent page blocks
├── features/     # Business scenarios (e.g., BookingForm)
├── entities/     # Business entities (e.g., User, Room)
└── shared/       # Reusable UI components (UI-kit)
```

**Environment Variables:**
- `AXIOS_BASEURL` - Internal Docker network URL (http://nginx)
- `AXIOS_BASEURL_CLIENT` - External client URL (http://127.0.0.1)
- `AXIOS_API_VERSION` - API version prefix (/api/v1)
- `NUXT_ENV_GOOGLE_MAPS_API` - Google Maps API key

### Chat Service (frontend/chat/)

Express.js with Socket.io for real-time messaging. Connects to Redis and PostgreSQL.

## Docker Services

**Current Setup (dev.yml):**
- `caddy` - Caddy reverse proxy (ports 80, 443)
- `api` - FastAPI application (internal port 8000)
- `frontend` - Nuxt 3 dev server (port 3000)
- `db` - PostgreSQL 16 (port 5432)
- `redis` - Redis 7.0 (port 6379)
- `rabbitmq` - RabbitMQ 3.13 with management UI
- `celery_worker` - Celery background worker
- `chat` - Socket.io server (port 6001)

## Key URLs

**Development:**
- Main app: http://127.0.0.1 or http://localhost
- FastAPI backend: http://127.0.0.1/api (proxied via Caddy)
- FastAPI docs: http://127.0.0.1/docs
- Frontend dev: http://localhost:3000
- Chat service: http://localhost:6001
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Important Notes

### Working with Migrations

**FastAPI (backend/):**
```bash
# Using Docker
docker compose -f dev.yml exec api alembic upgrade head
docker compose -f dev.yml exec api alembic revision --autogenerate -m "description"
docker compose -f dev.yml exec api alembic downgrade -1

# Or from root directory (if Make commands exist)
make migrate
make migrate-create message="description"
make migrate-down
```

**Laravel (laravel/):**
```bash
cd laravel
php artisan migrate
php artisan migrate:rollback
php artisan migrate:status
```

### Testing

**FastAPI:**
```bash
docker compose -f dev.yml exec api pytest
docker compose -f dev.yml exec api pytest -v  # Verbose
docker compose -f dev.yml exec api pytest --cov  # With coverage
```

### Code Quality (FastAPI)

```bash
docker compose -f dev.yml exec api black .
docker compose -f dev.yml exec api ruff check .
```

### Environment Configuration

- Root `.env` - Main configuration for all services
- `backend/.env` - FastAPI-specific configuration
- Copy from `.env.example` files when setting up

### Queue Workers

**FastAPI:** Celery worker runs automatically in `celery_worker` container
- Monitor tasks: `docker compose -f dev.yml logs -f celery_worker`

### Database Access

**PostgreSQL:**
```bash
docker compose -f dev.yml exec db psql -U postgres -d funny_db
# Or use direct connection: psql -h localhost -p 5432 -U postgres -d funny_db
```

## Creating New Features

### In FastAPI Backend:

1. Create module directory inside `backend/src/`:
   ```bash
   mkdir backend/src/my_module
   touch backend/src/my_module/__init__.py
   ```

2. Create module files:
   - `router.py` - API endpoints
   - `schemas.py` - Pydantic models (request/response)
   - `models.py` - SQLAlchemy database models
   - `service.py` - Business logic
   - `repository.py` - Data access layer
   - `dependencies.py` - FastAPI dependencies

3. Define models inheriting from `Base`, `IDMixin`, `TimestampMixin` from `src/models.py`

4. **Important**: Use type aliasing to avoid conflicts:
   ```python
   from datetime import date as date_type, time as time_type
   ```

5. Register router in `src/main.py`:
   ```python
   from src.my_module.router import router as my_module_router
   app.include_router(my_module_router)
   ```

6. Create and apply migration:
   ```bash
   docker compose -f dev.yml exec api alembic revision --autogenerate -m "add my_module"
   docker compose -f dev.yml exec api alembic upgrade head
   ```

### In Frontend:

Follow Feature-Sliced Design (FSD):
- `pages/` - Page routes
- `widgets/` - Complex UI blocks (TimeSelect, etc.)
- `features/` - Business scenarios (DatePicker, etc.)
- `entities/` - Business entities (Studio, Room, etc.)
- `shared/` - Reusable UI components

**Important**: Always use `.path` for photo/image URLs, not `.url`

## Common Workflows

**Start development:**
```bash
# Start all services
docker compose -f dev.yml up -d

# View logs
docker compose -f dev.yml logs -f

# Specific service logs
docker compose -f dev.yml logs -f api
docker compose -f dev.yml logs -f frontend
```

**Add new API endpoint (FastAPI):**
1. Add method to service layer
2. Add endpoint to router with proper type hints
3. Test the endpoint: `curl http://localhost/api/your-endpoint`
4. Format code: `docker compose -f dev.yml exec api black .`
5. Run tests: `docker compose -f dev.yml exec api pytest`

**Update database schema:**
1. Modify models in `backend/src/{module}/models.py`
2. Create migration: `docker compose -f dev.yml exec api alembic revision --autogenerate -m "description"`
3. Review generated migration in `backend/alembic/versions/`
4. Apply migration: `docker compose -f dev.yml exec api alembic upgrade head`
5. Update affected services/repositories

**Debug tips:**
```bash
# Check container status
docker compose -f dev.yml ps

# Access container shell
docker compose -f dev.yml exec api bash

# Database shell
docker compose -f dev.yml exec db psql -U postgres -d funny_db

# View all logs
docker compose -f dev.yml logs -f
```


# Claude Code Default Prompt

You are helping **Alex Khrishchatyi** rewrite the **Laravel backend (laravel/)** to **FastAPI (backend/)**.

## Architecture
Use **module-functionality structure** with separate layers:
`router`, `schemas`, `models`, `repository`, `service`, `dependencies`, `exceptions`, `constants`.

Example:
```
backend/src/
├── auth/
│   ├── router.py
│   ├── schemas.py
│   ├── models.py
│   ├── repository.py
│   ├── service.py
│   ├── exceptions.py
│   ├── constants.py
│   └── dependencies.py
├── bookings/
│   ├── router.py
│   ├── schemas.py
│   ├── models.py
│   ├── repository.py
│   ├── service.py
│   └── dependencies.py
├── config.py
├── database.py
├── exceptions.py
└── main.py
````

## Rules
1. When Alex sends a **Laravel `curl` example**, you must:
   - Recreate the **same endpoint** in FastAPI.
   - Implement identical **request params**, **validation**, and **responses**.
   - Analyze the provided `curl` and **infer logic and field meanings** automatically.
   - Replicate **Laravel Request validation** behavior using **Pydantic** models.
   - Return **Laravel-style responses**.

2. Validation error format (422):
   ```json
   {
     "message": "The email must be a valid email address.",
     "errors": { "email": ["The email must be a valid email address."] }
   }
````

3. Success response format:

   ```json
   {
     "message": "Registration successful, verify your email address",
     "token": "2|agh4OsOGU9S1Re3jfXLQXdJ27MVe8Heb8w6cB6sk6781cf9d",
     "role": "studio_owner"
   }
   ```

4. Follow this **example input request** pattern (analyze it for fields and logic):

   ```bash
   curl --location 'http://localhost:8888/api/v1/auth/register' \
   --header 'Accept: application/json' \
   --header 'Authorization: Bearer 1|9OsLgzPeYpknGHjUPJRrRrbN2oBeepkmODf8Vj7620410b4e' \
   --form 'email="khrischatyiis@gmail.com"' \
   --form 'password="berose50"' \
   --form 'name="alex"' \
   --form 'password_confirmation="berose50"' \
   --form 'role="studio_owner"'
   ```

## Standards

* Python 3.12+, FastAPI, SQLAlchemy 2.0
* Use **dependency injection** for DB and services.
* Code must be **typed, modular, clean, and production-grade**.
* `service` handles business logic, `repository` handles DB I/O only.
* Follow **SOLID** and **Laravel-equivalent validation**.

## Common Patterns and Best Practices

1. **Type Aliasing**: Always use type aliases to avoid Pydantic field name conflicts
   ```python
   from datetime import date as date_type, time as time_type
   ```

2. **Photo URLs**: Frontend always uses `.path` property, not `.url`
   ```python
   # Backend model
   photo.path  # ✓ Correct
   photo.url   # ✗ Wrong - will cause undefined errors
   ```

3. **Operating Hours Logic**:
   - Mode 1 (24/7): Returns first record
   - Mode 2 (Fixed): Returns first record
   - Mode 3 (Variable): Filter by `day_of_week` (0=Sunday, 6=Saturday)

4. **Timezone Handling**: Always use pytz for timezone-aware datetime
   ```python
   import pytz
   tz = pytz.timezone(address.timezone)  # e.g., "Europe/Belgrade"
   now = datetime.now(tz)
   ```

5. **Response Format**: TimeSelect expects `{time: "HH:MM", iso_string: "ISO8601"}`
   ```json
   {
     "available_times": [
       {"time": "10:00", "iso_string": "2025-10-31T10:00:00+01:00"}
     ]
   }
   ```

6. **Booking Exclusions**: Always exclude cancelled and expired bookings when checking availability
   ```python
   excluded_statuses=['cancelled', 'expired']
   ```

7. **Relationship Loading**: Use `selectinload()` for one-to-many, `joinedload()` for many-to-one
   ```python
   .options(
       selectinload(Room.address).selectinload(Address.operating_hours),
       selectinload(Room.prices)
   )
   ```