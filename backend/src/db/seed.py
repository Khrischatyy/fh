"""Main database seeder script."""

import asyncio

# Import all models to ensure proper SQLAlchemy configuration
from src.auth.models import User, UserRole
from src.geographic.models import Country, City
from src.companies.models import Company, AdminCompany
from src.addresses.models import Address, Badge
from src.rooms.models import Room
from src.bookings.models import Booking
from src.messages.models import Message
from src.payments.models import Charge, Payout

from src.database import AsyncSessionLocal
from src.db.seeders.role_seeder import seed_roles
from src.db.seeders.badge_seeder import seed_badges
from src.db.seeders.operating_mode_seeder import seed_operating_modes
from src.db.seeders.booking_status_seeder import seed_booking_statuses


async def run_seeders():
    """Run all database seeders."""
    print("🌱 Seeding database...")
    print()

    async with AsyncSessionLocal() as session:
        print("📋 Seeding roles...")
        await seed_roles(session)
        print()

        print("🏷️  Seeding badges...")
        await seed_badges(session)
        print()

        print("⏰ Seeding operating modes...")
        await seed_operating_modes(session)
        print()

        print("📅 Seeding booking statuses...")
        await seed_booking_statuses(session)
        print()

    print("✅ Done!")


if __name__ == "__main__":
    asyncio.run(run_seeders())
