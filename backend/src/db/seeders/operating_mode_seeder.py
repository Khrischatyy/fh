"""Operating modes seeder."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.addresses.models import OperatingMode


async def seed_operating_modes(session: AsyncSession):
    """Seed operating modes reference data."""

    # Check if already seeded
    result = await session.execute(select(OperatingMode))
    if result.scalars().first():
        print("   ⏭️  Operating modes already seeded, skipping...")
        return

    operating_modes = [
        {
            "id": 1,
            "mode": "24_7",
            "label": "24/7",
            "description_registration": "Studio operates 24 hours a day, 7 days a week",
            "description_customer": "Available 24/7"
        },
        {
            "id": 2,
            "mode": "fixed",
            "label": "Fixed Hours",
            "description_registration": "Same hours every day of the week",
            "description_customer": "Same hours daily"
        },
        {
            "id": 3,
            "mode": "variable",
            "label": "Variable Hours",
            "description_registration": "Different hours for each day of the week",
            "description_customer": "Hours vary by day"
        }
    ]

    for mode_data in operating_modes:
        mode = OperatingMode(**mode_data)
        session.add(mode)

    await session.commit()
    print(f"   ✅ Seeded {len(operating_modes)} operating modes")
