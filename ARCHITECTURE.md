# Clean Architecture & SOLID Principles

## Architecture Overview

This codebase follows a layered architecture with clear separation of concerns, enabling maintainability, testability, and scalability.

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (Router)                      │
│  • HTTP handling, request/response transformation           │
│  • Authentication/authorization enforcement                  │
│  • OpenAPI documentation                                     │
└─────────────────┬───────────────────────────────────────────┘
                  │ depends on
┌─────────────────▼───────────────────────────────────────────┐
│                    Service Layer (Business Logic)            │
│  • Domain rules and workflows                                │
│  • Cross-entity operations                                   │
│  • Transaction boundaries                                    │
└─────────────────┬───────────────────────────────────────────┘
                  │ depends on
┌─────────────────▼───────────────────────────────────────────┐
│                  Repository Layer (Data Access)              │
│  • Database queries and persistence                          │
│  • Query optimization and eager loading                      │
│  • Data access abstraction                                   │
└─────────────────┬───────────────────────────────────────────┘
                  │ depends on
┌─────────────────▼───────────────────────────────────────────┐
│                      Models (Entities)                       │
│  • Database schema definitions                               │
│  • ORM mappings and relationships                            │
│  • Domain constraints                                        │
└─────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### 1. Router (API Layer)
**Location:** `src/{domain}/router.py`

**Responsibilities:**
- Define HTTP endpoints and route handlers
- Validate request data via Pydantic schemas
- Enforce authentication and authorization
- Transform domain entities to API responses
- Handle HTTP-specific concerns (status codes, headers)

**Example:**
```python
@router.post("/add-studio", response_model=AddressResponse, status_code=201)
async def create_address(
    data: AddressCreate,
    service: Annotated[AddressService, Depends(get_address_service)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    address = await service.create_address(data)
    return AddressResponse.model_validate(address)
```

**Guidelines:**
- Keep handlers thin—delegate to service layer
- Never access repositories directly
- Use dependency injection for all dependencies
- Document endpoints with OpenAPI metadata

---

### 2. Service (Business Logic Layer)
**Location:** `src/{domain}/service.py`

**Responsibilities:**
- Implement domain business rules and workflows
- Coordinate operations across multiple repositories
- Define transaction boundaries
- Execute domain-specific validation
- Handle business exceptions

**Example:**
```python
class AddressService:
    def __init__(self, repository: AddressRepository):
        self._repository = repository

    async def create_address(self, data: AddressCreate) -> Address:
        slug = self._generate_slug(data.name)
        slug = await self._ensure_unique_slug(slug)

        address = Address(name=data.name, slug=slug, ...)
        return await self._repository.create(address)
```

**Guidelines:**
- Single Responsibility: One service per domain aggregate
- Depend on abstractions (repository interfaces), not implementations
- Keep business logic out of repositories and routers
- Make methods atomic and focused

---

### 3. Repository (Data Access Layer)
**Location:** `src/{domain}/repository.py`

**Responsibilities:**
- Encapsulate database queries
- Provide a collection-like interface for entities
- Handle eager loading and query optimization
- Abstract database implementation details

**Example:**
```python
class AddressRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, address: Address) -> Address:
        self._session.add(address)
        await self._session.flush()
        await self._session.refresh(address)
        return address

    async def find_by_id(self, address_id: int) -> Optional[Address]:
        stmt = select(Address).where(Address.id == address_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
```

**Guidelines:**
- Pure data access—no business logic
- Return domain entities, not DTOs or dicts
- Use explicit loading strategies to avoid N+1 queries
- Keep queries focused and reusable

---

### 4. Schemas (API Contracts)
**Location:** `src/{domain}/schemas.py`

**Responsibilities:**
- Define API request/response contracts
- Validate incoming data
- Document field constraints and types
- Serialize domain entities for API responses

**Example:**
```python
class AddressCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    street: str = Field(..., min_length=1, max_length=500)
    city_id: int = Field(..., gt=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
```

**Guidelines:**
- Separate schemas for Create, Update, and Response
- Use Pydantic validators for input sanitization
- Never expose internal domain models directly
- Keep schemas flat and focused

---

### 5. Dependencies (Dependency Injection)
**Location:** `src/{domain}/dependencies.py`

**Responsibilities:**
- Provide configured service and repository instances
- Manage dependency lifecycles
- Enable testing via dependency substitution

**Example:**
```python
async def get_address_service(
    repository: Annotated[AddressRepository, Depends(get_address_repository)]
) -> AddressService:
    return AddressService(repository)
```

**Guidelines:**
- Use FastAPI's `Depends()` for all dependencies
- Keep dependency chains shallow
- Avoid circular dependencies
- Enable easy mocking for tests

---

## SOLID Principles in Practice

### Single Responsibility Principle (SRP)
Each class has one reason to change:
- **Router:** HTTP concerns change
- **Service:** Business rules change
- **Repository:** Data access patterns change
- **Model:** Database schema changes

### Open/Closed Principle (OCP)
Extend behavior without modifying existing code:
- Add new endpoints without changing service logic
- Add new repositories without changing services
- Swap implementations via dependency injection

### Liskov Substitution Principle (LSP)
Depend on abstractions, not implementations:
- Services depend on repository protocols, not concrete classes
- Mock repositories in tests without breaking services

### Interface Segregation Principle (ISP)
Keep interfaces focused:
- Repositories expose only necessary query methods
- Services provide cohesive, domain-specific operations

### Dependency Inversion Principle (DIP)
High-level modules don't depend on low-level modules:
- Routers depend on services, not repositories
- Services depend on repository abstractions
- Both depend on domain models

---

## Best Practices

### Transactions
- Let the database session context manager handle commits/rollbacks
- Service methods define transaction boundaries
- Repositories never commit—services do

### Error Handling
- Raise domain-specific exceptions in services (e.g., `NotFoundException`)
- Let global exception handlers translate to HTTP responses
- Never catch exceptions in repositories

### Testing Strategy
- **Unit tests:** Service layer with mocked repositories
- **Integration tests:** Full stack with test database
- **Contract tests:** Schema validation and serialization

### Code Organization
```
src/
├── {domain}/
│   ├── __init__.py
│   ├── models.py          # Database entities
│   ├── schemas.py         # API contracts
│   ├── repository.py      # Data access
│   ├── service.py         # Business logic
│   ├── dependencies.py    # DI configuration
│   └── router.py          # API endpoints
```

---

## Anti-Patterns to Avoid

❌ **Business logic in routers**
```python
# Bad
@router.post("/addresses")
async def create_address(data: AddressCreate, db: AsyncSession):
    slug = data.name.lower().replace(" ", "-")  # Business logic
    address = Address(slug=slug, ...)
    db.add(address)
```

✅ **Business logic in services**
```python
# Good
@router.post("/addresses")
async def create_address(data: AddressCreate, service: AddressService):
    return await service.create_address(data)
```

---

❌ **Database queries in services**
```python
# Bad
class AddressService:
    async def get_address(self, session: AsyncSession, id: int):
        stmt = select(Address).where(Address.id == id)
        return await session.execute(stmt)
```

✅ **Repositories handle queries**
```python
# Good
class AddressService:
    async def get_address(self, id: int):
        return await self._repository.find_by_id(id)
```

---

❌ **Direct model exposure in APIs**
```python
# Bad
@router.get("/addresses/{id}", response_model=Address)
async def get_address(id: int):
    ...
```

✅ **DTOs for API contracts**
```python
# Good
@router.get("/addresses/{id}", response_model=AddressResponse)
async def get_address(id: int):
    ...
```

---

## When to Create New Layers

- **Add a new aggregate:** Create new domain folder with full layer stack
- **Cross-domain operations:** Create orchestration service
- **Shared utilities:** Place in `src/common/` or `src/utils/`
- **Third-party integrations:** Create adapter services (e.g., `PaymentGatewayService`)

---

## Summary

This architecture prioritizes:
1. **Maintainability:** Clear boundaries make changes predictable
2. **Testability:** Dependency injection enables isolated testing
3. **Scalability:** Services can be extracted into microservices
4. **Developer experience:** Consistent patterns reduce cognitive load

Follow these patterns, and the codebase will remain clean as complexity grows.
