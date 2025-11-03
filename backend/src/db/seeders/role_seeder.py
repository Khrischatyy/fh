"""Role seeder - displays available user roles."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import UserRole


async def seed_roles(session: AsyncSession) -> None:
    """
    Display available user roles.

    UserRole is an Enum, not a table, so nothing to seed.
    Available roles:
    - user: Regular user
    - studio_owner: Studio owner who can manage their studios
    - admin: Administrator with full access
    """
    print(f"  Available roles (Enum):")
    for role in UserRole:
        print(f"    - {role.value}")
    print(f"  ✓ Roles are defined in UserRole enum")
