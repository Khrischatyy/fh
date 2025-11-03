"""Badge seeder for populating badges table."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from src.addresses.models import Badge


async def seed_badges(session: AsyncSession) -> None:
    """
    Seed badges table with initial data.

    Only 3 badges: mixing, record, rent
    Images are stored in Google Cloud Storage and served via backend proxy.
    """
    badges_data = [
        {
            "id": 1,
            "name": "mixing",
            "image": "public/badges/mixing.svg",
            "description": "This studio provide sound engineering service"
        },
        {
            "id": 2,
            "name": "record",
            "image": "public/badges/record.svg",
            "description": "They can help to record your stuff"
        },
        {
            "id": 3,
            "name": "rent",
            "image": "public/badges/rent.svg",
            "description": "You can rent whole thing without any escort"
        }
    ]

    for badge_data in badges_data:
        # Check if badge already exists
        result = await session.execute(
            select(Badge).where(Badge.id == badge_data["id"])
        )
        existing_badge = result.scalar_one_or_none()

        if existing_badge:
            # Update existing badge
            existing_badge.name = badge_data["name"]
            existing_badge.image = badge_data["image"]
            existing_badge.description = badge_data["description"]
            print(f"  ✓ Updated badge: {badge_data['name']}")
        else:
            # Create new badge
            badge = Badge(
                id=badge_data["id"],
                name=badge_data["name"],
                image=badge_data["image"],
                description=badge_data["description"]
            )
            session.add(badge)
            print(f"  ✓ Created badge: {badge_data['name']}")

    await session.commit()

    # Delete any badges with ID > 3
    await session.execute(text("DELETE FROM address_badge WHERE badge_id > 3"))
    await session.execute(text("DELETE FROM badges WHERE id > 3"))
    await session.commit()
    print(f"  ✓ Removed extra badges (kept only IDs 1-3)")

    # Reset sequence
    await session.execute(
        text("SELECT setval(pg_get_serial_sequence('badges', 'id'), "
             "coalesce(max(id)+1, 1), false) FROM badges")
    )
    await session.commit()

    print(f"  Seeded {len(badges_data)} badges")
