# API Refactoring Guide

## Overview

This document outlines the systematic refactoring of the Laravel API (`backend/routes/api.php`) into a clean, maintainable FastAPI architecture following SOLID principles and Clean Architecture patterns.

## Refactoring Strategy

### 1. Domain Identification

From `api.php`, the following business domains have been identified:

- **Authentication** (✅ Completed with FastAPI Users)
- **Companies** - Business entities owning studios
- **Addresses (Studios)** (✅ Completed) - Physical studio locations
- **Rooms** - Individual rooms within studios
- **Bookings** - Reservation system
- **Payments** - Stripe/Square integration
- **Equipment & Badges** - Studio amenities
- **Operating Hours** - Availability management
- **Geographic** - Countries and Cities
- **Messages** - Chat system
- **Teams** - Team member management
- **Payouts** - Financial disbursements

### 2. Architecture Pattern Applied

Each domain follows this layered structure:

```
src/{domain}/
├── models.py          # SQLAlchemy entities (already exist)
├── schemas.py         # Pydantic DTOs for API contracts
├── repository.py      # Data access layer
├── service.py         # Business logic layer
├── dependencies.py    # Dependency injection
└── router.py          # HTTP endpoints
```

## Example: Address Domain (Reference Implementation)

### Repository Layer (`addresses/repository.py`)
```python
class AddressRepository:
    """Pure data access - no business logic."""

    async def create(self, address: Address) -> Address:
        self._session.add(address)
        await self._session.flush()
        return address

    async def find_by_slug(self, slug: str) -> Optional[Address]:
        stmt = select(Address).where(Address.slug == slug)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
```

**Principles:**
- Single Responsibility: Only database operations
- No business rules or validation
- Returns domain entities, not DTOs
- Explicit query optimization (eager loading)

### Service Layer (`addresses/service.py`)
```python
class AddressService:
    """Business logic orchestration."""

    async def create_address(self, data: AddressCreate) -> Address:
        # Business rule: Generate unique slug
        slug = self._generate_slug(data.name)
        slug = await self._ensure_unique_slug(slug)

        address = Address(
            name=data.name,
            slug=slug,
            timezone=data.timezone or "UTC",  # Default value
            is_published=False,  # Business rule: start unpublished
        )

        return await self._repository.create(address)

    async def publish_address(self, address_id: int) -> Address:
        # Business rule: Only active addresses can be published
        address = await self.get_address(address_id)
        if not address.is_active:
            raise ConflictException("Cannot publish inactive address")
        address.is_published = True
        return await self._repository.update(address)
```

**Principles:**
- Contains ALL business logic and rules
- Coordinates multiple repository operations
- Handles domain-specific validation
- Raises domain exceptions

### Router Layer (`addresses/router.py`)
```python
@router.post("/add-studio", response_model=AddressResponse, status_code=201)
async def create_address(
    data: AddressCreate,
    service: Annotated[AddressService, Depends(get_address_service)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    """Create new studio with automatic slug generation."""
    address = await service.create_address(data)
    return AddressResponse.model_validate(address)
```

**Principles:**
- Thin controllers - only HTTP concerns
- Dependency injection for all dependencies
- Schema validation via Pydantic
- Clear OpenAPI documentation

## Laravel to FastAPI Route Mapping

### Authentication Routes
| Laravel Route | FastAPI Equivalent | Status |
|--------------|-------------------|--------|
| `POST /auth/login` | `POST /api/auth/jwt/login` | ✅ |
| `POST /auth/register` | `POST /api/auth/register` | ✅ |
| `POST /auth/forgot-password` | `POST /api/auth/forgot-password` | ✅ |
| `POST /auth/reset-password` | `POST /api/auth/reset-password` | ✅ |
| `GET /user/me` | `GET /api/auth/me` | ✅ |

### Address (Studio) Routes
| Laravel Route | FastAPI Equivalent | Status |
|--------------|-------------------|--------|
| `POST /address/add-studio` | `POST /api/addresses/add-studio` | ✅ |
| `POST /address/delete-studio` | `DELETE /api/addresses/{id}` | ✅ |
| `GET /address/studio/{slug}` | `GET /api/addresses/slug/{slug}` | ✅ |
| `GET /address/list` | `GET /api/addresses/company/{id}` | ✅ |
| `PUT /address/{slug}/update-slug` | `PATCH /api/addresses/{id}` | ✅ |
| `POST /address/toggle-favorite-studio` | `POST /api/addresses/{id}/favorite` | 🔄 |

### Room Routes
| Laravel Route | FastAPI Equivalent | Status |
|--------------|-------------------|--------|
| `POST /room/add-room` | `POST /api/rooms` | 📋 |
| `PUT /room/{id}/update-name` | `PATCH /api/rooms/{id}` | 📋 |
| `POST /room/{id}/prices` | `POST /api/rooms/{id}/prices` | 📋 |
| `GET /room/{id}/prices` | `GET /api/rooms/{id}/prices` | 📋 |
| `DELETE /room/prices` | `DELETE /api/rooms/prices/{id}` | 📋 |

### Booking Routes
| Laravel Route | FastAPI Equivalent | Status |
|--------------|-------------------|--------|
| `POST /room/reservation` | `POST /api/bookings` | 📋 |
| `POST /room/cancel-booking` | `POST /api/bookings/{id}/cancel` | 📋 |
| `POST /address/calculate-price` | `POST /api/bookings/calculate-price` | 📋 |
| `GET /address/reservation/start-time` | `GET /api/bookings/available-slots` | 📋 |
| `GET /history` | `GET /api/bookings/history` | 📋 |
| `GET /booking-management` | `GET /api/bookings/upcoming` | 📋 |

### Company Routes
| Laravel Route | FastAPI Equivalent | Status |
|--------------|-------------------|--------|
| `POST /brand` | `POST /api/companies` | 📋 |
| `GET /company/{slug}` | `GET /api/companies/{slug}` | 📋 |
| `GET /{slug}/studios` | `GET /api/companies/{slug}/studios` | 📋 |

**Legend:**
- ✅ Implemented
- 🔄 In Progress
- 📋 Planned

## Key Improvements Over Laravel Implementation

### 1. Type Safety
**Before (Laravel):**
```php
public function createAddress(Request $request) {
    $validated = $request->validate([...]);  // Runtime validation
    // $validated is array, no IDE support
}
```

**After (FastAPI):**
```python
async def create_address(
    data: AddressCreate,  # Compile-time type checking
    service: AddressService,  # Full IDE autocomplete
):
    # data.name, data.street are typed
```

### 2. Dependency Injection
**Before (Laravel):**
```php
class AddressController {
    public function createAddress(Request $request) {
        $service = app(AddressService::class);  // Service locator
        // Testing requires complex mocking
    }
}
```

**After (FastAPI):**
```python
async def create_address(
    service: Annotated[AddressService, Depends(get_address_service)],
    # Easily mockable for testing
):
    # Clear dependencies, testable
```

### 3. Business Logic Separation
**Before (Laravel):**
```php
class AddressController {
    public function createAddress(Request $request) {
        // Slug generation IN controller
        $slug = Str::slug($request->name);
        // Database access IN controller
        $address = Address::create([...]);
        // Mixed concerns
    }
}
```

**After (FastAPI):**
```python
# Router: Only HTTP
async def create_address(data: AddressCreate, service: AddressService):
    return await service.create_address(data)

# Service: Only business logic
async def create_address(self, data: AddressCreate):
    slug = self._generate_slug(data.name)
    return await self._repository.create(...)

# Repository: Only data access
async def create(self, address: Address):
    self._session.add(address)
```

### 4. Async/Await Throughout
**Before (Laravel):**
```php
$addresses = Address::with('city', 'company')->get();  // Blocking I/O
```

**After (FastAPI):**
```python
addresses = await repository.find_all_with_relations()  # Non-blocking
```

### 5. Explicit Error Handling
**Before (Laravel):**
```php
$address = Address::findOrFail($id);  // Throws generic 404
```

**After (FastAPI):**
```python
address = await repository.find_by_id(id)
if not address:
    raise NotFoundException(f"Address {id} not found")  # Domain exception
```

## Implementation Checklist

For each remaining domain, follow this process:

### Phase 1: Define Schemas (`{domain}/schemas.py`)
```python
class {Entity}Create(BaseModel): ...
class {Entity}Update(BaseModel): ...
class {Entity}Response(BaseModel): ...
```

### Phase 2: Implement Repository (`{domain}/repository.py`)
```python
class {Entity}Repository:
    async def create(...) -> {Entity}: ...
    async def find_by_id(...) -> Optional[{Entity}]: ...
    async def update(...) -> {Entity}: ...
    async def delete(...) -> None: ...
```

### Phase 3: Implement Service (`{domain}/service.py`)
```python
class {Entity}Service:
    def __init__(self, repository: {Entity}Repository): ...
    async def create_{entity}(...) -> {Entity}: ...
    # Business logic methods
```

### Phase 4: Configure Dependencies (`{domain}/dependencies.py`)
```python
async def get_{entity}_service(...) -> {Entity}Service:
    return {Entity}Service(repository)
```

### Phase 5: Create Router (`{domain}/router.py`)
```python
router = APIRouter(prefix="/{entities}", tags=["{Entities}"])

@router.post("/", response_model={Entity}Response)
async def create_{entity}(
    data: {Entity}Create,
    service: Annotated[{Entity}Service, Depends(get_{entity}_service)],
): ...
```

### Phase 6: Register in `main.py`
```python
from src.{domain}.router import router as {entity}_router
app.include_router({entity}_router, prefix=settings.api_prefix)
```

## Testing Strategy

### Unit Tests (Service Layer)
```python
async def test_create_address_generates_unique_slug():
    repo_mock = Mock(AddressRepository)
    repo_mock.exists_by_slug.return_value = False

    service = AddressService(repo_mock)
    address = await service.create_address(AddressCreate(...))

    assert address.slug == "expected-slug"
    repo_mock.create.assert_called_once()
```

### Integration Tests (Full Stack)
```python
async def test_create_address_endpoint(client: TestClient, auth_token):
    response = client.post(
        "/api/addresses/add-studio",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "Test Studio", ...}
    )
    assert response.status_code == 201
```

## Migration from Laravel Controllers

For each Laravel controller method, follow this transformation:

1. **Extract validation** → Pydantic schemas
2. **Extract business logic** → Service layer
3. **Extract queries** → Repository layer
4. **Keep HTTP handling** → Router layer

**Example:**

```php
// Laravel: AddressController.php
public function createAddress(Request $request) {
    $validated = $request->validate([...]);
    $slug = Str::slug($validated['name']);
    $address = Address::create([..., 'slug' => $slug]);
    return response()->json($address, 201);
}
```

Becomes:

```python
# schemas.py
class AddressCreate(BaseModel):
    name: str = Field(..., min_length=1)

# service.py
async def create_address(self, data: AddressCreate) -> Address:
    slug = self._generate_slug(data.name)
    return await self._repository.create(...)

# router.py
@router.post("/", response_model=AddressResponse, status_code=201)
async def create_address(
    data: AddressCreate,
    service: Annotated[AddressService, Depends(get_address_service)],
):
    return await service.create_address(data)
```

## Benefits Achieved

1. **Testability**: Each layer independently testable
2. **Maintainability**: Clear separation of concerns
3. **Scalability**: Services can be extracted to microservices
4. **Type Safety**: Compile-time error detection
5. **Performance**: Async I/O throughout
6. **Documentation**: Auto-generated OpenAPI specs
7. **Developer Experience**: IDE autocomplete and type hints

## Next Steps

1. Complete remaining domains using Address pattern
2. Implement comprehensive test suite
3. Add rate limiting and caching
4. Set up monitoring and logging
5. Performance optimization based on profiling

---

**Reference Implementation:** See `src/addresses/` for complete example following all principles outlined here.
