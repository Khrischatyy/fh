# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Funny-how is a studio booking platform with two backend implementations (Laravel legacy + FastAPI new), a Nuxt.js frontend, and a Socket.io chat service. The system uses Docker for containerization with separate dev and production configurations.

## Repository Structure

- `backend/` - Laravel 9 PHP backend (legacy)
- `new_backend/` - FastAPI Python backend (current/preferred)
- `frontend/client/` - Nuxt 3 client application
- `frontend/chat/` - Socket.io chat service (Express.js)
- `proxy/` - Nginx reverse proxy configuration

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

### FastAPI Backend (new_backend/)

Navigate to `new_backend/` directory first. Commands use `new_backend/Makefile`:

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
# Root level (prod.yml)
make build-prod
make start-prod
make migrate-prod
make optimize-prod
make seeds-prod

# FastAPI (new_backend/)
make prod-build
make prod-detach
```

## Architecture

### FastAPI Backend (new_backend/) - Module-Functionality Pattern

The new backend follows a layered architecture with clear separation of concerns:

**Layer Flow:** Router → Service → Repository → Models

**Module Structure:**
```
src/{domain}/
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
- `addresses/` - Studio locations with geolocation
- `rooms/` - Bookable spaces with pricing
- `bookings/` - Reservation system with availability checking
- `payments/` - Multi-gateway (Stripe, Square) payment processing
- `messages/` - Direct messaging between users and studio owners
- `geographic/` - Countries, cities reference data
- `tasks/` - Celery background tasks (email, bookings, payments)

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

### Laravel Backend (backend/) - Legacy

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

**Development (dev.yml):**
- `nginx` - Reverse proxy (port 8888)
- `db` - PostgreSQL 16 (port 5433)
- `backend` - Laravel PHP-FPM
- `frontend` - Nuxt 3 dev server (port 3000)
- `redis` - Redis 7.0 (port 6380)
- `rabbitmq` - RabbitMQ 3.13 with management (ports 5673, 15673)
- `queue-worker` - Laravel queue worker
- `scheduler` - Laravel task scheduler
- `chat` - Socket.io server (port 6001)
- `swagger` - Swagger UI (port 8080)

**FastAPI Services (new_backend/dev.yml):**
- `api` - FastAPI application (port 80 via nginx)
- `nginx` - Reverse proxy
- `db` - PostgreSQL
- `redis` - Redis
- `rabbitmq` - RabbitMQ
- `celery_worker` - Celery worker

## Key URLs

**Development:**
- Main app: http://127.0.0.1:8888 (or http://localhost:8888)
- Frontend dev: http://localhost:3000
- Swagger (Laravel): http://127.0.0.1:8080
- FastAPI docs: http://localhost/docs (when in new_backend)
- RabbitMQ Management: http://localhost:15673 (guest/guest)

## Important Notes

### Working with Migrations

**Laravel:**
```bash
make migrate              # Run migrations
make rollback             # Rollback
make artisan c="migrate:status"  # Check status
```

**FastAPI:**
```bash
cd new_backend
make migrate-create message="add users table"
make migrate              # Apply migrations
make migrate-down         # Rollback
```

### Testing

**FastAPI:**
```bash
cd new_backend
make test                 # Run with coverage
make test-verbose         # Detailed output
```

### Code Quality (FastAPI)

```bash
cd new_backend
make format               # Auto-format code
make lint                 # Check code style
```

### Environment Configuration

- Root `.env` - Main configuration for all services
- `new_backend/.env` - FastAPI-specific configuration
- Copy from `.env.example` files when setting up

### Queue Workers

**Laravel:** Queue worker runs automatically in `queue-worker` container
**FastAPI:** Celery worker runs automatically in `celery_worker` container

### Database Access

**Laravel DB:**
```bash
docker compose -f dev.yml exec db psql -U postgres -d funny_db
```

**FastAPI DB:**
```bash
cd new_backend
make db-shell
```

## Creating New Features

### In FastAPI Backend:

1. Create module directory: `mkdir src/my_module && touch src/my_module/__init__.py`
2. Create module files: `router.py`, `schemas.py`, `models.py`, `service.py`, `repository.py`, `dependencies.py`
3. Define models inheriting from `Base`, `IDMixin`, `TimestampMixin`
4. Create Pydantic schemas for validation
5. Implement repository for data access
6. Implement service for business logic
7. Create router with FastAPI endpoints
8. Register router in `src/main.py`
9. Create migration: `make migrate-create message="add my_module"`
10. Apply migration: `make migrate`

### In Laravel Backend:

Use standard Laravel conventions (controllers, models, migrations, routes).

### In Frontend:

Follow FSD methodology - place code in appropriate layer (features, entities, shared, etc.).

## Common Workflows

**Start development:**
```bash
# Terminal 1 - Root services
make build && make start

# Terminal 2 - FastAPI (optional)
cd new_backend && make dev-build
```

**Add new API endpoint (FastAPI):**
1. Add method to service
2. Add endpoint to router
3. Test with `make test`
4. Format with `make format`

**Update database schema:**
1. Modify models
2. Create migration
3. Apply migration
4. Update affected services/endpoints

**View logs:**
```bash
make logs-all                    # All services
make logs container=backend      # Specific service
cd new_backend && make logs      # FastAPI logs
```


# Claude Code Default Prompt

You are helping **Alex Khrishchatyi** rewrite the **Laravel backend (backend/)** to **FastAPI (new_backend/)**.

## Architecture
Use **module-functionality structure** with separate layers:
`router`, `schemas`, `models`, `repository`, `service`, `dependencies`, `exceptions`, `constants`.

Example:
```

new_backend/src/
├── auth/
│   ├── router.py
│   ├── schemas.py
│   ├── models.py
│   ├── repository.py
│   ├── service.py
│   ├── exceptions.py
│   ├── constants.py
│   └── dependencies.py
├── config.py
├── database.py
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