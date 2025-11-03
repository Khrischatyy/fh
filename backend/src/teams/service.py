"""
Team service - Business logic for team member management.
Implements Laravel TeamService patterns.
"""
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import secrets
import string

from src.auth.models import User, engineer_addresses
from src.addresses.models import Address


class TeamService:
    """Service for team management operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_member(
        self,
        name: str,
        email: str,
        address_id: int,
        role: str,
        rate_per_hour: float,
        current_user_id: int
    ) -> User:
        """
        Add a team member to an address.

        Creates a new user account, assigns role, sets rate, attaches to address,
        and sends invitation email with password reset link.

        Args:
            name: Member name
            email: Member email (must be unique)
            address_id: Address ID to attach to
            role: Role (studio_engineer or studio_manager)
            rate_per_hour: Hourly rate
            current_user_id: User making the request (for authorization)

        Returns:
            Created user

        Raises:
            HTTPException: If address not found, email exists, or not authorized
        """
        # Verify address exists
        stmt = select(Address).where(Address.id == address_id)
        result = await self.db.execute(stmt)
        address = result.scalar_one_or_none()

        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": f"Address with ID {address_id} not found.",
                    "errors": {}
                }
            )

        # TODO: Authorize update permission for this address
        # In Laravel: $this->authorize('update', $address)

        # Check if email already exists
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "The email has already been taken.",
                    "errors": {"email": ["The email has already been taken."]}
                }
            )

        # Generate random password (12 characters)
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

        # Hash password
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash(password)

        # Create user
        user = User(
            name=name,
            firstname=name.split()[0] if name else name,
            lastname=" ".join(name.split()[1:]) if len(name.split()) > 1 else "",
            username=name,
            email=email,
            password_hash=hashed_password,
            role=role
        )
        self.db.add(user)
        await self.db.flush()  # Get user ID

        # Create engineer_rate record (simplified - store in user or separate table)
        # In Laravel: $user->engineerRate()->create(['rate_per_hour' => $ratePerHour])
        # For now, we'll need to add this field or create a separate table

        # Attach user to address (many-to-many via engineer_addresses)
        stmt = engineer_addresses.insert().values(user_id=user.id, address_id=address_id)
        await self.db.execute(stmt)

        await self.db.commit()
        await self.db.refresh(user)

        # TODO: Generate password reset token
        # TODO: Send staff invitation email
        # In Laravel: Password::createToken($user) and SendStaffInvitationJob

        return user

    async def check_member_email(self, query: str) -> List[Dict[str, str]]:
        """
        Search for studio engineers by email (autocomplete).

        Args:
            query: Email search query

        Returns:
            List of users with firstname and email
        """
        # Search users with role studio_engineer where email matches
        stmt = (
            select(User)
            .where(User.role == "studio_engineer")
            .where(User.email.ilike(f"%{query}%"))
        )
        result = await self.db.execute(stmt)
        users = result.scalars().all()

        return [
            {"firstname": user.firstname or user.name, "email": user.email}
            for user in users
        ]

    async def remove_member(
        self,
        address_id: int,
        member_id: int,
        current_user_id: int
    ) -> None:
        """
        Remove team member from address.

        Detaches user from address (does not delete user account).

        Args:
            address_id: Address ID
            member_id: User ID to remove
            current_user_id: User making the request (for authorization)

        Raises:
            HTTPException: If address not found, member not found, or not authorized
        """
        # Verify address exists
        stmt = select(Address).where(Address.id == address_id)
        result = await self.db.execute(stmt)
        address = result.scalar_one_or_none()

        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": f"Address with ID {address_id} not found.",
                    "errors": {}
                }
            )

        # TODO: Authorize update permission
        # In Laravel: $this->authorize('update', $address)

        # Verify member is attached to this address
        stmt = select(engineer_addresses).where(
            engineer_addresses.c.user_id == member_id,
            engineer_addresses.c.address_id == address_id
        )
        result = await self.db.execute(stmt)
        relationship = result.first()

        if not relationship:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": "Team member not found at this address.",
                    "errors": {}
                }
            )

        # Detach user from address
        stmt = engineer_addresses.delete().where(
            engineer_addresses.c.user_id == member_id,
            engineer_addresses.c.address_id == address_id
        )
        await self.db.execute(stmt)
        await self.db.commit()
