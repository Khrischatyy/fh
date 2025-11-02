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
- `locker/` - macOS device locker application (see `locker/CLAUDE.md` for details)

## FunnyHow Locker - macOS Device Management App

**Full Documentation**: See `/locker/CLAUDE.md` for complete details.

**Quick Start:**
```bash
cd /Users/alexkhrishchatyi/www/funny-how/locker

# First time setup
make setup          # Setup virtual environment and install dependencies

# Build the app
make build          # Build the .app bundle

# Launch
make test-app       # Test the built app
```

**Common Commands:**
```bash
make run            # Run from source (development)
make rebuild        # Clean and rebuild
make dmg            # Create DMG installer
make help           # Show all available commands
```

**Key Features:**
- ✅ Token-based device registration (no email/password)
- ✅ Automatic screen locking when outside booking times
- ✅ Menu bar app with custom FunnyHow branding
- ✅ Dock icon with custom logo
- ✅ Multi-method screen locking (pmset, CGSession, AppleScript)

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
- `auth/` - Authentication & user management (JWT, Google OAuth, Laravel Sanctum-compatible tokens)
- `users/` - User profile management with payment gateway info (Stripe, Square)
- `companies/` - Studio/business entities linked to owners via `admin_company`
- `addresses/` - Studio locations with geolocation, operating hours, and completion status
  - `utils.py` - Reusable utility functions for studio visibility, completion checks, data transformation
- `rooms/` - Bookable spaces with pricing and photo galleries
- `bookings/` - Reservation system with availability checking
- `operating_hours/` - Studio operating hours management (modes: 24/7, fixed, variable)
- `payments/` - Multi-gateway (Stripe, Square) payment processing with payout verification
- `messages/` - Direct messaging between users and studio owners
- `geographic/` - Countries, cities reference data with studio filtering
- `my_studios/` - Studio owner's studio management (list, filter, with completion status)
- `tasks/` - Celery background tasks (email, bookings, payments)
- `teams/` - Studio team members/engineers management (add, list, remove)
- `storage.py` - Google Cloud Storage integration for media uploads
- `gcs_utils.py` - GCS utility functions for generating proxy URLs

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

### Studio Visibility and Completion Logic

The platform implements sophisticated studio visibility rules to ensure only properly configured studios appear in public search results.

**Key Module:** `backend/src/addresses/utils.py`

**Studio Completion (`is_complete`) Requirements:**

A studio is considered "complete" and ready for public visibility when ALL of the following are met:

1. **Operating Hours Configured**
   - At least one operating hours record exists
   - Can be Mode 1 (24/7), Mode 2 (Fixed), or Mode 3 (Variable)

2. **Payment Gateway with Payouts Enabled**
   - **Stripe**: `stripe_account_id` exists AND `payouts_enabled = true` (verified via Stripe API)
   - **Square**: `payment_gateway = 'square'` (assumes ready if configured)

**Utility Functions (`addresses/utils.py`):**

```python
# Check if studio setup is complete
is_studio_complete(address: Address) -> bool

# Check if payment gateway is properly connected
has_payment_gateway_connected(address: Address) -> bool

# Get studio owner (admin user)
get_studio_owner(address: Address) -> Optional[User]

# Verify Stripe payouts enabled (with caching)
check_stripe_payouts_enabled(stripe_account_id: str) -> bool

# Build standardized studio dictionary
build_studio_dict(
    address: Address,
    include_is_complete: bool = True,
    include_payment_status: bool = False,
    stripe_cache: Optional[dict] = None
) -> dict

# Determine if studio should be visible in public search
should_show_in_public_search(address: Address, stripe_cache: Optional[dict] = None) -> bool
```

**Public vs Owner View Filtering:**

- **Public Endpoints** (`/api/city/{city_id}/studios`, `/api/map/studios`):
  - Filter: Only show studios where `should_show_in_public_search()` returns `True`
  - Requires: Operating hours + payment gateway with payouts enabled

- **Owner Endpoints** (`/api/my-studios/filter`):
  - No filtering: Show all studios owned by the user
  - Includes: `is_complete` status to guide setup completion
  - Includes: `stripe_account_id` for payment gateway info

**Stripe API Caching:**

To avoid repeated API calls, implementations use caching:
```python
stripe_cache = {}  # {stripe_account_id: payouts_enabled}
# Reused across all studios in a single request
```

**Data Relationships:**

Studios connect to payment gateways through this chain:
```
Address → Company → AdminCompany → User (admin)
                                    ↓
                            stripe_account_id
                            payment_gateway
```

### Media/Asset Management (Photos & Badges)

The platform uses Google Cloud Storage (GCS) with proxy endpoints to serve media privately.

**Storage Architecture:**

1. **Google Cloud Storage**: Primary storage for all media files
   - Photos: `studio/photos/{uuid}.jpg`
   - Badges: `public/badges/{name}.svg`

2. **Proxy Endpoints**: Backend serves files to keep GCS private
   - Photos: `/api/photos/image/{path}`
   - Badges: `/api/badges/image/{path}`

**Photo Path Transformation:**

Photos must be transformed from GCS paths to proxy URLs:

```python
# Raw path from database
"studio/photos/de1b2f25.jpg"

# Transformed for frontend (via _transform_photo_path)
"/api/photos/image/studio/photos/de1b2f25.jpg"
```

**Badge Image Transformation:**

Badges must be transformed using `get_public_url()`:

```python
from src.gcs_utils import get_public_url

# Raw path from database
"public/badges/rent.svg"

# Transformed for frontend
get_public_url("public/badges/rent.svg")
# Returns: "/api/badges/image/public/badges/rent.svg"
```

**Frontend Expectations:**

- **PhotoSwipe Component**: Expects `photo.path` with full URL
- **BadgesList Component**: Expects `badge.image` with full URL
- Both use proxy URLs that route through the backend

**Pydantic Schema Transformations:**

Schemas automatically transform paths when using `model_validator`:

```python
@model_validator(mode='after')
def transform_photo_path(self) -> 'MapRoomPhotoResponse':
    """Transform photo path to proxy URL."""
    if self.path and not self.path.startswith('http') and not self.path.startswith('/api/'):
        self.path = f"/api/photos/image/{self.path}"
    return self
```

**Important:** When using `build_studio_dict()` utility (which returns raw dicts), transformations are applied automatically.

### My Studios Module - Studio Owner Management

Owner-specific endpoints for managing their own studios.

**Endpoints:**

```
GET  /api/my-studios/cities         # Get cities where user has studios
GET  /api/my-studios/                # Get all user's studios
POST /api/my-studios/filter          # Filter user's studios (by city)
```

**Key Features:**

1. **No Public Filtering**: Shows ALL studios owned by the user, regardless of completion status
2. **Completion Status**: Returns `is_complete` to guide setup
3. **Payment Gateway Info**: Includes `stripe_account_id` in response
4. **Photo Aggregation**: Flattens all photos from all rooms to top level
5. **Price Aggregation**: Flattens all prices from all rooms to top level

**Response Structure:**

```json
{
  "success": true,
  "data": [{
    "id": 18,
    "slug": "section-los-angeles-2",
    "street": "435 Arden Avenue",
    "stripe_account_id": "acct_1SPYMgRoNlrpg5Us",
    "is_complete": true,
    "operating_hours": [...],
    "rooms": [...],
    "photos": [...],  // Aggregated from all rooms
    "prices": [...],  // Aggregated from all rooms
    "badges": [...],
    "company": {...}
  }],
  "message": "Studios retrieved successfully",
  "code": 200
}
```

**Data Loading:**

Repository loads full relationship chain:
```python
.options(
    joinedload(Address.city),
    joinedload(Address.company).selectinload(Company.admin_companies).joinedload(AdminCompany.admin),
    selectinload(Address.operating_hours),
    selectinload(Address.badges),
    selectinload(Address.rooms).selectinload(Room.photos),
    selectinload(Address.rooms).selectinload(Room.prices),
)
```

**Photo URL Transformation:**

Uses Pydantic schema with `model_validator` for automatic transformation:
```python
from src.my_studios.schemas import RoomPhotoResponse

# Convert and transform photos
for photo in room.photos:
    photo_response = RoomPhotoResponse.model_validate(photo)
    all_photos.append(photo_response)
```

### Payment Gateway Integration

Multi-gateway support with real-time payout verification.

**Supported Gateways:**

1. **Stripe Connect**
   - Account linking via OAuth
   - Real-time payout verification via Stripe API
   - Fields: `stripe_account_id` (on User model)
   - Verification: `account.payouts_enabled` must be `True`

2. **Square**
   - Simplified integration
   - Fields: `payment_gateway = 'square'` (on User model)
   - Assumption: If configured, considered ready

**Payout Verification Flow:**

```python
# 1. Get studio owner
studio_owner = get_studio_owner(address)

# 2. Check payment gateway type
if studio_owner.stripe_account_id:
    # Stripe: Verify via API
    account = stripe.Account.retrieve(studio_owner.stripe_account_id)
    payouts_ready = account.payouts_enabled

elif studio_owner.payment_gateway == 'square':
    # Square: Assume ready
    payouts_ready = True
```

**Caching Strategy:**

Avoid repeated Stripe API calls within a single request:

```python
stripe_cache = {}

for studio in studios:
    studio_owner = get_studio_owner(studio)

    if studio_owner.stripe_account_id in stripe_cache:
        # Use cached result
        payouts_ready = stripe_cache[studio_owner.stripe_account_id]
    else:
        # Query Stripe API once
        payouts_ready = check_stripe_payouts_enabled(studio_owner.stripe_account_id)
        stripe_cache[studio_owner.stripe_account_id] = payouts_ready
```

**Database Structure:**

```sql
-- User has payment gateway info
users:
  - stripe_account_id: VARCHAR (Stripe Connect account)
  - payment_gateway: VARCHAR ('stripe' or 'square')

-- User linked to Company via AdminCompany
admin_company:
  - admin_id: INT (references users.id)
  - company_id: INT (references companies.id)

-- Company has Addresses (studios)
addresses:
  - company_id: INT (references companies.id)
  - operating_hours: relationship
```

**Configuration:**

Environment variables in `.env`:
```bash
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Teams Module - Studio Team Management

Manages studio team members (engineers and managers) with roles and hourly rates.

**User Roles:**
- `studio_engineer` - Regular team member who can be assigned to bookings
- `studio_manager` - Manager role with elevated permissions

**Database Structure:**

```sql
-- Engineer hourly rates
engineer_rates:
  - id: BIGINT (PRIMARY KEY)
  - user_id: BIGINT (references users.id, CASCADE)
  - rate_per_hour: NUMERIC(8, 2)

-- Many-to-many: Engineers assigned to studios
engineer_addresses:
  - id: BIGINT (PRIMARY KEY)
  - user_id: BIGINT (references users.id, CASCADE)
  - address_id: BIGINT (references addresses.id, CASCADE)
  - created_at, updated_at: TIMESTAMP
```

**Key Models:**

```python
# backend/src/auth/models.py
class EngineerRate(Base, IDMixin):
    user_id: Mapped[int]
    rate_per_hour: Mapped[float]  # Numeric(8,2)
    user: Mapped["User"] = relationship("User", back_populates="engineer_rate")

class User(Base, IDMixin, TimestampMixin):
    role: Mapped[str]  # 'studio_engineer' or 'studio_manager'
    engineer_rate: Mapped[Optional["EngineerRate"]] = relationship(...)
    engineer_addresses: Mapped[list["Address"]] = relationship(...)

# backend/src/addresses/models.py
class Address(Base, IDMixin, TimestampMixin):
    engineers: Mapped[list["User"]] = relationship(
        "User",
        secondary="engineer_addresses",
        lazy="select",
    )
```

**API Endpoints:**

```http
# List all team members for user's company
GET /api/team/member
Authorization: Bearer {token}
Response: {
  "success": true,
  "data": [
    {
      "id": 18,
      "username": "John Engineer",
      "email": "john.engineer@example.com",
      "role": "studio_engineer",
      "roles": [{"name": "studio_engineer"}],  # Laravel Spatie format
      "pivot": {"address_id": 16, "user_id": 18},
      "engineerRate": {"rate_per_hour": 50.0},
      "booking_count": 0
    }
  ]
}

# Add new team member
POST /api/team/member
Authorization: Bearer {token}
Body: {
  "name": "John Engineer",
  "email": "john.engineer@example.com",
  "address_id": 16,
  "role": "studio_engineer",
  "rate_per_hour": 50.00
}

# Remove team member from studio
DELETE /api/team/member
Authorization: Bearer {token}
Body: {
  "address_id": 16,
  "member_id": 18
}

# Search engineers by email (autocomplete)
GET /api/team/email/check?q={query}
Authorization: Bearer {token}
```

**Team Member Creation Flow:**

1. **Validation**: Email must be unique, role must be `studio_engineer` or `studio_manager`
2. **User Creation**: Creates user with random 12-character password
3. **Role Assignment**: Sets `user.role` field
4. **Rate Storage**: Creates `EngineerRate` record with hourly rate
5. **Studio Assignment**: Links user to address via `engineer_addresses` pivot table
6. **TODO**: Send invitation email with password reset link

**Authorization:**

Team members can only be managed by the studio owner (user who owns the company that owns the address):
```python
# Check authorization
company_id = address.company_id
is_admin = await company_service.is_admin(company_id, current_user_id)
```

**Studio Detail with Engineers:**

The `/api/address/studio/{slug}` endpoint includes engineers data:
```json
{
  "id": 16,
  "slug": "section-los-angeles-1",
  "engineers": [
    {
      "id": 18,
      "username": "John Engineer",
      "role": "studio_engineer",
      "engineer_rate": {
        "rate_per_hour": 50.0
      }
    }
  ]
}
```

**Frontend Integration:**

Engineers appear in booking forms on studio detail pages:
```javascript
// frontend/client/src/pages/@[slug_address]/index.vue
const teammatesOptions = computed(() => {
  // Filter only studio_engineer role (exclude managers)
  const studioEngineers = address.value.engineers.filter(
    (teammate) => teammate.role === 'studio_engineer'
  );

  // Map to FSelect options (username only, no price)
  return [
    { id: null, name: "No Engineer", label: "No Engineer" },
    ...studioEngineers.map((eng) => ({
      id: eng.id,
      name: eng.username,
      label: eng.username,
    }))
  ];
});
```

**Important Notes:**
- Engineers are filtered by role in frontend (`studio_engineer` only for bookings)
- Hourly rate is stored but NOT displayed in booking dropdown
- Team member list shows both engineers and managers
- Removing a team member detaches from address but does NOT delete the user account

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
- **Admin panel**: http://127.0.0.1/admin (username: `admin`, password from `.env`)
- Frontend dev: http://localhost:3000
- Chat service: http://localhost:6001
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- **MCP Server**: http://127.0.0.1/mcp (internal network: http://api:8000/mcp)

## MCP Server Integration

The FastAPI backend includes an integrated MCP (Model Context Protocol) server that automatically exposes all API endpoints as MCP tools for AI agent integration.

### Overview

- **Library**: FastMCP (Python MCP server library)
- **Location**: Mounted at `/mcp` endpoint
- **Purpose**: Enable AI agents (Twilio SMS campaigns, LLM integrations) to interact with the API
- **Auto-exposure**: All FastAPI routes are automatically available as MCP tools

### Implementation

The MCP server is implemented in the `backend/src/mcp/` module:

```
backend/src/mcp/
├── __init__.py
├── server.py          # FastMCP server setup and configuration
```

Integration happens automatically in `main.py` via `setup_mcp(app)` after middleware and exception handlers are registered.

### Security

- **Internal-only**: MCP endpoint is NOT exposed via Caddy reverse proxy
- **Network**: Accessible only within Docker internal network
- **Usage**: Intended for server-to-server communication (Twilio, internal services)
- **Authentication**: Currently no authentication (internal service)

**Important**: If you need to expose MCP externally in the future, add API key authentication first.

### Usage Example (Internal Services)

```python
# Internal service connecting to MCP
import httpx

async def call_mcp_tool():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://api:8000/mcp",
            json={
                "tool": "auth/register",
                "parameters": {...}
            }
        )
        return response.json()
```

### Testing MCP

Once containers are running:

```bash
# From within Docker network (e.g., another container)
curl http://api:8000/mcp

# Via Caddy proxy (if enabled)
curl http://localhost/mcp
```

### Adding Custom MCP Tools

FastMCP automatically discovers all FastAPI routes. To add custom MCP-specific tools:

1. Add new FastAPI endpoints to any router
2. The MCP server will automatically expose them as tools
3. No additional configuration needed

### Testing with Pydantic AI Chat Agent

A simple terminal chat agent is provided to test the MCP server integration:

**Location**: `backend/mcp_chat.py`

**Dependencies**: Automatically installed in Docker image (included in `pyproject.toml` optional dependencies)

**Run the chat agent**:
```bash
# Make sure the API server is running first
docker compose -f dev.yml up -d

# Start the chat agent (no installation needed!)
docker compose -f dev.yml exec api python mcp_chat.py
```

**Note**: If you rebuild the Docker image, dependencies are automatically installed. No manual `pip install` needed!

**Features**:
- Interactive terminal chat with Claude Sonnet 4.0
- Access to all 88 FastAPI endpoints as MCP tools
- Streaming responses for better UX
- Message history for contextual conversations
- Automatic connection testing

**Example conversation**:
```
🧑 You: What tools do you have access to?
🤖 Assistant: I have access to 88 tools from the FastAPI backend...

🧑 You: Can you help me create a new user?
🤖 Assistant: [Uses auth/register endpoint via MCP]

🧑 You: Show me all companies
🤖 Assistant: [Uses companies endpoint via MCP]
```

**Environment Variables** (already in root `.env`):
```bash
ANTHROPIC_API_KEY=your-api-key-here  # Required
MCP_SERVER_URL=http://localhost:8000/mcp/mcp  # Optional (default shown)
CHAT_MODEL=anthropic:claude-sonnet-4-0  # Optional (default shown)
```

**Admin Panel:**
- SQLAdmin interface for managing all database models (27 models)
- Secured with basic HTTP auth (credentials in `.env`: `ADMIN_USERNAME`, `ADMIN_PASSWORD`)
- Production: https://funny-how.com/admin
- **Important**: Change default credentials in production!

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

### 1. Type Aliasing
Always use type aliases to avoid Pydantic field name conflicts:
```python
from datetime import date as date_type, time as time_type
```

### 2. Media URL Handling

**Photos:**
```python
# Frontend always uses .path property
photo.path  # ✓ Correct - transformed to proxy URL
photo.url   # ✗ Wrong - will cause undefined errors

# Transform raw paths to proxy URLs
from src.addresses.utils import _transform_photo_path
proxy_url = _transform_photo_path("studio/photos/abc123.jpg")
# Returns: "/api/photos/image/studio/photos/abc123.jpg"
```

**Badges:**
```python
# Transform badge images to proxy URLs
from src.gcs_utils import get_public_url
proxy_url = get_public_url("public/badges/mixing.svg")
# Returns: "/api/badges/image/public/badges/mixing.svg"
```

### 3. Studio Completion and Visibility

**Check if studio is complete:**
```python
from src.addresses.utils import is_studio_complete, should_show_in_public_search

# For displaying completion status
if is_studio_complete(address):
    print("Studio setup is complete")

# For filtering public search results
if should_show_in_public_search(address, stripe_cache):
    # Include in search results
    pass
```

**Build standardized studio response:**
```python
from src.addresses.utils import build_studio_dict

# Use Stripe cache to avoid repeated API calls
stripe_cache = {}

for address in addresses:
    studio_dict = build_studio_dict(
        address,
        include_is_complete=True,      # Include is_complete field
        include_payment_status=False,   # Include payouts_ready field
        stripe_cache=stripe_cache       # Reuse cache
    )
```

### 4. Operating Hours Logic
- **Mode 1 (24/7)**: Returns first record
- **Mode 2 (Fixed)**: Returns first record (same hours daily)
- **Mode 3 (Variable)**: Filter by `day_of_week` (0=Sunday, 6=Saturday)

### 5. Timezone Handling
Always use pytz for timezone-aware datetime:
```python
import pytz
tz = pytz.timezone(address.timezone)  # e.g., "America/Los_Angeles"
now = datetime.now(tz)
```

### 6. Response Formats

**TimeSelect (availability endpoints):**
```json
{
  "available_times": [
    {"time": "10:00", "iso_string": "2025-10-31T10:00:00+01:00"}
  ]
}
```

**Laravel-compatible responses:**
```json
{
  "success": true,
  "data": [...],
  "message": "Operation successful",
  "code": 200
}
```

### 7. Booking Exclusions
Always exclude cancelled and expired bookings when checking availability:
```python
excluded_statuses = ['cancelled', 'expired']
```

### 8. SQLAlchemy Relationship Loading

**Use appropriate loading strategies:**
```python
# One-to-many: Use selectinload()
.options(selectinload(Address.rooms).selectinload(Room.photos))

# Many-to-one: Use joinedload()
.options(joinedload(Address.company))

# Complex chains: Mix both
.options(
    joinedload(Address.company)
        .selectinload(Company.admin_companies)
        .joinedload(AdminCompany.admin),
    selectinload(Address.operating_hours),
    selectinload(Address.badges),
)
```

### 9. Payment Gateway Verification

**Always verify payouts are enabled:**
```python
from src.addresses.utils import get_studio_owner, check_stripe_payouts_enabled

studio_owner = get_studio_owner(address)

if studio_owner.stripe_account_id:
    # Verify Stripe payouts
    if check_stripe_payouts_enabled(studio_owner.stripe_account_id):
        print("Stripe payouts enabled")

elif studio_owner.payment_gateway == 'square':
    # Square assumed ready if configured
    print("Square configured")
```

### 10. Authentication Patterns

**Token format (Laravel Sanctum-compatible):**
```bash
# Format: {user_id}|{jwt_token}
Authorization: Bearer 15|eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Dependencies:**
```python
from src.auth.dependencies import get_current_user

# Extracts user from token automatically
async def my_endpoint(current_user: User = Depends(get_current_user)):
    print(f"Authenticated as: {current_user.email}")
```

### 11. Code Organization

**Always delegate to utility functions:**
```python
# ✓ Good: Use centralized utilities
from src.addresses.utils import build_studio_dict

studio_dict = build_studio_dict(address)

# ✗ Bad: Duplicate logic in routers
studio_dict = {
    "id": address.id,
    "badges": [...],  # Manually building...
}
```

**Keep routers thin:**
```python
# ✓ Good: Router delegates to service
@router.get("/studios")
async def get_studios(service: MyService = Depends()):
    return await service.get_studios()

# ✗ Bad: Business logic in router
@router.get("/studios")
async def get_studios():
    # Complex queries and transformations here...
    pass
```

### 12. Error Handling

**Use custom exceptions:**
```python
from src.exceptions import NotFoundException, ConflictException

# Not found
if not studio:
    raise NotFoundException("Studio not found")

# Business logic conflict
if not has_operating_hours:
    raise ConflictException("Operating hours must be configured first")
```

**Laravel-compatible validation errors:**
```python
# Automatically handled by Pydantic
# Returns 422 with:
{
  "message": "Validation error",
  "errors": {
    "email": ["Email is required"]
  }
}
```

## Key API Endpoints Reference

### Public Studio Endpoints

**Search studios by city:**
```http
GET /api/city/{city_id}/studios
Authorization: Bearer {token} (optional)
```
- Filters: Only complete studios (has operating hours + payment gateway)
- Returns: Studios with `is_complete: true` and `payouts_ready: true`
- Use case: Public studio search, map markers

**Get studio by slug:**
```http
GET /api/address/studio/{slug}
```
- Filters: None (shows incomplete studios too)
- Returns: Full studio details with `is_complete` status
- Use case: Studio detail page, owner preview

**Map view studios:**
```http
GET /api/map/studios
```
- Filters: Only complete studios
- Returns: Studios optimized for map display
- Use case: Interactive map view

### Studio Owner Endpoints

**List owner's studios:**
```http
POST /api/my-studios/filter
Authorization: Bearer {token}
Body: { "city_id": 11 } (optional)
```
- Filters: None (shows all owner's studios)
- Returns: All studios with `is_complete` and `stripe_account_id`
- Use case: Studio management dashboard

**Get owner's cities:**
```http
GET /api/my-studios/cities
Authorization: Bearer {token}
```
- Returns: Cities where owner has studios
- Use case: City filter dropdown

### Operating Hours Endpoints

**Get operating hours:**
```http
GET /api/address/operating-hours?address_id={id}
Authorization: Bearer {token}
```

**Set operating hours:**
```http
POST /api/address/operating-hours
Authorization: Bearer {token}
Body: {
  "address_id": 18,
  "mode_id": 1,  // 1=24/7, 2=Fixed, 3=Variable
  "open_time": "09:00",    // Required for mode 2
  "close_time": "17:00",   // Required for mode 2
  "hours": [...]           // Required for mode 3
}
```

### Booking/Availability Endpoints

**Get available start times:**
```http
GET /api/address/reservation/start-time?room_id={id}&date=2025-11-04
```

**Get available end times:**
```http
GET /api/address/reservation/end-time?room_id={id}&date=2025-11-04&start_time=10:00
```

### Badge/Amenity Endpoints

**Get all badges:**
```http
GET /api/address/{address_id}/badges
Authorization: Bearer {token}
```
- Returns: `all_badges` and `taken_badges` arrays

**Toggle badge:**
```http
POST /api/address/{address_id}/badge
Authorization: Bearer {token}
Body: { "badge_id": 3 }
```

### Team Management Endpoints

**List team members:**
```http
GET /api/team/member
Authorization: Bearer {token}
```
- Returns: All team members (engineers + managers) for user's company
- Includes: `roles`, `pivot`, `engineerRate` data
- Use case: Team management page

**Add team member:**
```http
POST /api/team/member
Authorization: Bearer {token}
Body: {
  "name": "John Engineer",
  "email": "john.engineer@example.com",
  "address_id": 16,
  "role": "studio_engineer",
  "rate_per_hour": 50.00
}
```
- Creates user account with random password
- Assigns to studio via engineer_addresses
- Stores hourly rate in engineer_rates

**Remove team member:**
```http
DELETE /api/team/member
Authorization: Bearer {token}
Body: { "address_id": 16, "member_id": 18 }
```
- Detaches user from studio (doesn't delete account)

**Search engineers:**
```http
GET /api/team/email/check?q=john
Authorization: Bearer {token}
```
- Autocomplete search for studio_engineer role users

### Media Proxy Endpoints

**Photo proxy:**
```http
GET /api/photos/image/{path}
Example: /api/photos/image/studio/photos/abc123.jpg
```

**Badge proxy:**
```http
GET /api/badges/image/{path}
Example: /api/badges/image/public/badges/mixing.svg
```

## Troubleshooting Common Issues

### Issue: Studios not showing in public search

**Check:**
1. Operating hours configured? `len(address.operating_hours) > 0`
2. Payment gateway connected? `user.stripe_account_id` or `user.payment_gateway == 'square'`
3. Stripe payouts enabled? `stripe.Account.retrieve(account_id).payouts_enabled == True`

**Solution:**
```python
from src.addresses.utils import should_show_in_public_search
if not should_show_in_public_search(address):
    print("Studio not ready for public display")
```

### Issue: Images not loading (broken badges/photos)

**Check:**
1. Are paths transformed? Should start with `/api/photos/image/` or `/api/badges/image/`
2. Using `build_studio_dict()`? It auto-transforms paths
3. Using Pydantic schemas? They have `model_validator` for transformation

**Solution:**
```python
# For badges
from src.gcs_utils import get_public_url
badge_image = get_public_url(badge.image)

# For photos
from src.addresses.utils import _transform_photo_path
photo_path = _transform_photo_path(photo.path)
```

### Issue: `is_complete` showing false incorrectly

**Check:**
1. User's `stripe_account_id` not null?
2. Stripe API returning `payouts_enabled = true`?
3. Operating hours exist for the studio?

**Debug:**
```python
from src.addresses.utils import get_studio_owner, check_stripe_payouts_enabled

owner = get_studio_owner(address)
print(f"Stripe ID: {owner.stripe_account_id}")
print(f"Payouts: {check_stripe_payouts_enabled(owner.stripe_account_id)}")
print(f"Op Hours: {len(address.operating_hours)}")
```

### Issue: Duplicate Stripe API calls

**Solution:** Always use caching within request scope:
```python
stripe_cache = {}
for studio in studios:
    studio_dict = build_studio_dict(studio, stripe_cache=stripe_cache)
```

### Issue: Frontend component works in one page but not another

**Check:**
1. API responses have same structure? Use `build_studio_dict()`
2. Photos have `.path`? Not `.url`
3. Badges have `.image` with proxy URL?
4. Response includes all required fields?

**Consistency pattern:**
```python
# All public endpoints should use the same utility
from src.addresses.utils import build_studio_dict

# This ensures consistent structure everywhere
studio_dict = build_studio_dict(address, ...)
```
