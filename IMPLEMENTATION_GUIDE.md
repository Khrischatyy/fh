# FastAPI Backend Implementation Guide

This guide provides detailed instructions for completing the remaining module implementations.

## Table of Contents

1. [Overview](#overview)
2. [What's Already Implemented](#whats-already-implemented)
3. [Implementation Roadmap](#implementation-roadmap)
4. [Module Implementation Templates](#module-implementation-templates)
5. [Next Steps](#next-steps)

## Overview

The FastAPI backend structure is fully set up with:
- ✅ All database models (7 modules, 20+ models)
- ✅ Authentication module (complete with router, service, schemas)
- ✅ Docker setup (dev and prod)
- ✅ Alembic migrations
- ✅ Celery tasks for emails
- ✅ Configuration and exception handling
- ✅ Makefile for automation

**What remains**: Implement routers, services, and schemas for the remaining 8 modules.

## What's Already Implemented

### ✅ Core Infrastructure

1. **Database Layer** (`src/database.py`)
   - Async SQLAlchemy engine
   - Session management
   - Connection pooling

2. **Models** - All SQLAlchemy models are complete:
   - `src/auth/models.py` - User model with roles and OAuth
   - `src/companies/models.py` - Company and AdminCompany
   - `src/geographic/models.py` - Country and City
   - `src/addresses/models.py` - Address (Studio), Equipment, Badges, OperatingHours
   - `src/rooms/models.py` - Room, RoomPhoto, RoomPrice
   - `src/bookings/models.py` - Booking, BookingStatus
   - `src/payments/models.py` - Charge, Payout, SquareToken, SquareLocation
   - `src/messages/models.py` - Message

3. **Auth Module** - Fully implemented:
   - Registration and login
   - JWT token generation
   - Google OAuth integration
   - Password reset flow (structure in place)
   - Email verification (structure in place)
   - Auth dependencies for route protection

4. **Background Tasks**
   - Celery configuration
   - Email tasks (verification, welcome, booking confirmations, etc.)

5. **DevOps**
   - Docker Compose (dev and prod)
   - Makefile for common operations
   - Alembic for migrations
   - Logging configuration

### 📋 To Be Implemented

Routers, services, and schemas for:
1. Users module
2. Companies module
3. Geographic module (Countries, Cities)
4. Addresses module (Studios)
5. Rooms module
6. Bookings module
7. Payments module
8. Messages module
9. Teams module

## Implementation Roadmap

### Phase 1: Simple Modules (1-2 hours)

Start with simpler modules to build momentum:

1. **Geographic Module** (Countries, Cities)
   - Mostly read-only
   - Simple CRUD operations
   - No complex business logic

2. **Users Module**
   - Profile management
   - Update user details
   - Photo uploads (S3)

3. **Companies Module**
   - Company CRUD
   - Admin assignment

### Phase 2: Core Business Logic (3-4 hours)

4. **Addresses Module** (Studios)
   - Studio CRUD
   - Operating hours management
   - Equipment and badge management
   - Favorite studios
   - Search and filtering

5. **Rooms Module**
   - Room CRUD within studios
   - Photo management
   - Price tiers

### Phase 3: Complex Features (4-5 hours)

6. **Bookings Module**
   - Availability checking
   - Price calculation
   - Booking creation
   - Cancellation with refunds
   - Temporary payment links

7. **Payments Module**
   - Stripe integration
   - Square integration
   - Payment session creation
   - Payout management
   - Refunds

8. **Messages Module**
   - Direct messaging
   - Chat history
   - Read status

9. **Teams Module**
   - Team member management
   - Invitations

## Module Implementation Templates

### Template 1: Simple CRUD Module (Geographic)

#### Step 1: Create `schemas.py`

```python
# src/geographic/schemas.py
from pydantic import BaseModel
from typing import Optional

class CountryBase(BaseModel):
    name: str
    code: str

class CountryCreate(CountryBase):
    pass

class CountryResponse(CountryBase):
    id: int
    model_config = {"from_attributes": True}

class CityBase(BaseModel):
    name: str
    country_id: int

class CityCreate(CityBase):
    pass

class CityResponse(CityBase):
    id: int
    model_config = {"from_attributes": True}
```

#### Step 2: Create `service.py`

```python
# src/geographic/service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.geographic.models import Country, City
from src.exceptions import NotFoundException

class GeographicService:
    async def get_countries(self, db: AsyncSession):
        result = await db.execute(select(Country))
        return result.scalars().all()

    async def get_country(self, db: AsyncSession, country_id: int):
        result = await db.execute(
            select(Country).filter(Country.id == country_id)
        )
        country = result.scalar_one_or_none()
        if not country:
            raise NotFoundException("Country not found")
        return country

    async def get_cities_by_country(self, db: AsyncSession, country_id: int):
        result = await db.execute(
            select(City).filter(City.country_id == country_id)
        )
        return result.scalars().all()

geographic_service = GeographicService()
```

#### Step 3: Create `router.py`

```python
# src/geographic/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.geographic import schemas
from src.geographic.service import geographic_service

router = APIRouter(prefix="/geographic", tags=["Geographic"])

@router.get("/countries", response_model=list[schemas.CountryResponse])
async def get_countries(db: AsyncSession = Depends(get_db)):
    """Get all countries."""
    return await geographic_service.get_countries(db)

@router.get("/countries/{country_id}/cities", response_model=list[schemas.CityResponse])
async def get_cities(
    country_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all cities in a country."""
    return await geographic_service.get_cities_by_country(db, country_id)
```

#### Step 4: Register router in `main.py`

```python
from src.geographic.router import router as geographic_router
app.include_router(geographic_router, prefix=settings.api_prefix)
```

### Template 2: Module with Authentication (Users)

#### `router.py` with auth

```python
from fastapi import APIRouter, Depends, UploadFile, File
from src.auth.dependencies import get_current_user
from src.auth.models import User

router = APIRouter(prefix="/user", tags=["Users"])

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user

@router.put("/update")
async def update_profile(
    data: schemas.UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user profile."""
    return await user_service.update_user(db, current_user, data)

@router.post("/upload-photo")
async def upload_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload profile photo to S3."""
    # TODO: Implement S3 upload
    # photo_url = await upload_to_s3(file)
    # current_user.profile_photo = photo_url
    # await db.commit()
    return {"photo_url": "placeholder"}
```

### Template 3: Complex Service (Bookings)

#### `service.py` with business logic

```python
# src/bookings/service.py
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from src.bookings.models import Booking, BookingStatus
from src.rooms.models import Room, RoomPrice
from src.exceptions import BookingException
from src.config import settings

class BookingService:
    async def calculate_price(
        self,
        db: AsyncSession,
        room_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> float:
        """Calculate booking price based on duration and room pricing."""
        duration = (end_time - start_time).total_seconds() / 3600  # hours

        # Get room prices
        result = await db.execute(
            select(RoomPrice)
            .filter(
                and_(
                    RoomPrice.room_id == room_id,
                    RoomPrice.min_duration <= duration,
                    RoomPrice.max_duration >= duration,
                    RoomPrice.is_enabled == True,
                )
            )
        )
        price_tier = result.scalar_one_or_none()

        if not price_tier:
            raise BookingException("No pricing available for this duration")

        # Calculate price (base price * hours)
        total = price_tier.price * duration

        # Add service fee
        service_fee = total * (settings.service_fee_percentage / 100)
        total_with_fee = total + service_fee

        return round(total_with_fee, 2)

    async def check_availability(
        self,
        db: AsyncSession,
        room_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: int = None,
    ) -> bool:
        """Check if room is available for the given time slot."""
        query = select(Booking).filter(
            and_(
                Booking.room_id == room_id,
                Booking.start_time < end_time,
                Booking.end_time > start_time,
                Booking.status_id.in_([1, 2]),  # pending or confirmed
            )
        )

        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)

        result = await db.execute(query)
        conflicting_bookings = result.scalars().all()

        return len(conflicting_bookings) == 0

    async def create_booking(
        self,
        db: AsyncSession,
        user_id: int,
        room_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> Booking:
        """Create a new booking."""
        # Check availability
        is_available = await self.check_availability(db, room_id, start_time, end_time)
        if not is_available:
            raise BookingException("Room is not available for selected time")

        # Calculate price
        price = await self.calculate_price(db, room_id, start_time, end_time)

        # Create booking
        booking = Booking(
            user_id=user_id,
            room_id=room_id,
            start_time=start_time,
            end_time=end_time,
            status_id=1,  # pending
            temporary_payment_link=generate_payment_link(),
            temporary_payment_link_expires_at=datetime.utcnow() + timedelta(
                minutes=settings.temporary_payment_link_expiry_minutes
            ),
        )

        db.add(booking)
        await db.commit()
        await db.refresh(booking)

        # Send notification email
        # await send_booking_pending_email.delay(booking.id)

        return booking

booking_service = BookingService()
```

### Template 4: File Upload (Rooms)

```python
# src/rooms/utils.py
import boto3
from uuid import uuid4
from src.config import settings

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region,
)

async def upload_photo_to_s3(file, folder: str = "rooms") -> str:
    """Upload file to S3 and return URL."""
    file_extension = file.filename.split(".")[-1]
    file_name = f"{folder}/{uuid4()}.{file_extension}"

    # Upload to S3
    s3_client.upload_fileobj(
        file.file,
        settings.aws_bucket_name,
        file_name,
        ExtraArgs={"ACL": "public-read", "ContentType": file.content_type}
    )

    # Return URL
    return f"https://{settings.aws_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{file_name}"
```

## Next Steps

### 1. Create Database Migrations

```bash
cd new_backend
make migrate message="initial migration"
make upgrade
```

### 2. Implement Modules in Order

Follow the roadmap above, implementing modules from simple to complex.

### 3. Test Each Module

Create tests as you implement:

```python
# tests/geographic/test_service.py
import pytest
from src.geographic.service import geographic_service

@pytest.mark.asyncio
async def test_get_countries(db_session):
    countries = await geographic_service.get_countries(db_session)
    assert isinstance(countries, list)
```

### 4. Update main.py

Register each router as you complete it:

```python
from src.users.router import router as users_router
app.include_router(users_router, prefix=settings.api_prefix)
```

### 5. Document Endpoints

FastAPI auto-generates docs at `/docs`, but add docstrings:

```python
@router.post("/book")
async def create_booking(data: schemas.BookingCreate):
    """
    Create a new booking.

    - **room_id**: ID of the room to book
    - **start_time**: Booking start time (ISO 8601)
    - **end_time**: Booking end time (ISO 8601)

    Returns the created booking with payment link.
    """
    pass
```

### 6. Integration Testing

Test complete workflows:
1. Register user → Login → Create studio → Create room → Book room
2. Payment flow → Booking confirmation → Email notifications
3. Booking cancellation → Refund processing

### 7. Add Missing Features

Once core modules are done, implement:
- Email verification tokens (store in Redis or database)
- Password reset tokens (store in Redis or database)
- Rate limiting (slowapi)
- Pagination helpers
- Search filters
- File validation
- Image resizing (Pillow)

## Quick Reference

### Common Patterns

#### Query with Pagination

```python
from sqlalchemy import select

async def get_paginated(db: AsyncSession, page: int = 1, size: int = 20):
    offset = (page - 1) * size
    query = select(Model).offset(offset).limit(size)
    result = await db.execute(query)
    return result.scalars().all()
```

#### Query with Filters

```python
from sqlalchemy import and_, or_

query = select(Studio).filter(
    and_(
        Studio.city_id == city_id,
        Studio.is_active == True,
        or_(
            Studio.name.ilike(f"%{search}%"),
            Studio.description.ilike(f"%{search}%"),
        )
    )
)
```

#### Eager Loading Relationships

```python
from sqlalchemy.orm import selectinload

query = select(Booking).options(
    selectinload(Booking.room),
    selectinload(Booking.user),
)
```

#### Transactions

```python
async with db.begin():
    # Multiple operations
    db.add(booking)
    charge = Charge(...)
    db.add(charge)
    # Auto-commits if no exception
```

## Additional Resources

- FastAPI Docs: https://fastapi.tiangolo.com/
- SQLAlchemy 2.0 Docs: https://docs.sqlalchemy.org/en/20/
- Pydantic Docs: https://docs.pydantic.dev/
- Alembic Docs: https://alembic.sqlalchemy.org/
- Celery Docs: https://docs.celeryq.dev/

## Support

For questions during implementation:
1. Check existing `auth` module as reference
2. Review SQLAlchemy models for relationships
3. Refer to Laravel project for business logic
4. Test endpoints using `/docs` interface

---

Happy coding! 🚀
