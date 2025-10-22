# Address Domain Implementation

## Overview

The Address domain has been implemented following clean architecture and SOLID principles, demonstrating production-ready patterns for the entire codebase.

## Implementation Structure

```
src/addresses/
├── models.py          # Domain entities (Address, OperatingHour, etc.)
├── schemas.py         # API contracts (Create, Update, Response DTOs)
├── repository.py      # Data access layer
├── service.py         # Business logic layer
├── dependencies.py    # Dependency injection configuration
└── router.py          # HTTP API endpoints
```

## Key Features

### Repository Layer (`repository.py`)
- **Purpose:** Abstracts database operations
- **Pattern:** Collection-like interface for Address entities
- **Optimizations:** 
  - Eager loading via `selectinload()` to prevent N+1 queries
  - Explicit query methods for common access patterns
- **Methods:**
  - `create()` - Persist new address
  - `find_by_id()` - Retrieve with related entities
  - `find_by_slug()` - URL-based lookups
  - `find_by_company()` - List all company addresses
  - `exists_by_slug()` - Uniqueness validation

### Service Layer (`service.py`)
- **Purpose:** Orchestrates business logic
- **Responsibilities:**
  - Slug generation from names
  - Uniqueness enforcement
  - Business rule validation (e.g., only active addresses can be published)
  - State transitions (publish/unpublish)
- **Key Methods:**
  - `create_address()` - Creates address with auto-generated unique slug
  - `update_address()` - Updates with slug regeneration when name changes
  - `publish_address()` - Business rule: only active addresses publishable
  - `_ensure_unique_slug()` - Private method ensuring slug uniqueness

### API Layer (`router.py`)
- **Endpoints:**
  - `POST /api/addresses/add-studio` - Create studio
  - `GET /api/addresses/{id}` - Get by ID
  - `GET /api/addresses/slug/{slug}` - Get by slug
  - `GET /api/addresses/company/{company_id}` - List company studios
  - `PATCH /api/addresses/{id}` - Update studio
  - `DELETE /api/addresses/{id}` - Delete studio
  - `POST /api/addresses/{id}/publish` - Publish studio
  - `POST /api/addresses/{id}/unpublish` - Unpublish studio
- **Security:** All mutating operations require authentication
- **Documentation:** Full OpenAPI specs with descriptions

## Architecture Principles Applied

### Single Responsibility Principle (SRP)
- **Router:** HTTP handling only
- **Service:** Business logic only
- **Repository:** Data access only

### Dependency Inversion Principle (DIP)
```python
# Router depends on service abstraction
service: Annotated[AddressService, Depends(get_address_service)]

# Service depends on repository abstraction
def __init__(self, repository: AddressRepository)
```

### Open/Closed Principle (OCP)
- New endpoints added without modifying service
- New business rules added to service without changing repository
- Testable via dependency injection

## Usage Examples

### Create Address
```bash
curl -X POST http://localhost/api/addresses/add-studio \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Downtown Recording Studio",
    "street": "123 Main St",
    "city_id": 1,
    "company_id": 1,
    "description": "Professional recording studio in downtown",
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
```

**Business Logic Applied:**
- Slug auto-generated: `downtown-recording-studio`
- If slug exists, appends counter: `downtown-recording-studio-2`
- Initializes as inactive/unpublished
- Sets available_balance to 0.00

### Publish Address
```bash
curl -X POST http://localhost/api/addresses/1/publish \
  -H "Authorization: Bearer <token>"
```

**Business Rule:** Fails if address is inactive

## Testing Approach

### Unit Tests (Service Layer)
```python
async def test_create_address_generates_unique_slug():
    # Mock repository
    repo_mock = Mock(AddressRepository)
    repo_mock.exists_by_slug.side_effect = [True, False]  # First exists, second doesn't
    
    service = AddressService(repo_mock)
    
    # Create address
    data = AddressCreate(name="Test Studio", ...)
    address = await service.create_address(data)
    
    # Assert slug uniqueness logic
    assert address.slug == "test-studio-1"
```

### Integration Tests (Full Stack)
```python
async def test_create_address_endpoint(client: TestClient, auth_token: str):
    response = client.post(
        "/api/addresses/add-studio",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "Test Studio", ...}
    )
    
    assert response.status_code == 201
    assert response.json()["slug"] == "test-studio"
```

## Extending This Pattern

To implement another domain (e.g., Rooms), follow the same structure:

1. **Repository** - Define data access methods
2. **Service** - Implement business logic
3. **Schemas** - Create API contracts (Create, Update, Response)
4. **Dependencies** - Configure DI
5. **Router** - Define HTTP endpoints
6. **Register** - Add to `main.py`

See `ARCHITECTURE.md` for comprehensive guidelines.

## Benefits

✅ **Maintainability:** Clear boundaries make changes isolated  
✅ **Testability:** Each layer testable independently  
✅ **Scalability:** Service layer can be extracted to microservices  
✅ **Readability:** Consistent patterns across domains  
✅ **Performance:** Optimized queries with eager loading  

## Next Steps

Apply this pattern to remaining domains:
- Companies
- Rooms
- Bookings
- Payments
- Messages

Each should follow the same layered architecture for consistency.
