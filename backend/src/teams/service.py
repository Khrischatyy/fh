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

from src.auth.models import User, EngineerRate, engineer_addresses
from src.addresses.models import Address
from src.companies.repository import CompanyRepository
from src.companies.service import CompanyService
from src.exceptions import ForbiddenException


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

        # Authorization check: verify user is admin of the address's company
        if address.company_id:
            company_repo = CompanyRepository(self.db)
            company_service = CompanyService(company_repo)
            if not await company_service.is_admin(address.company_id, current_user_id):
                raise ForbiddenException("You are not authorized to manage team members for this address")

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

        # Create engineer_rate record
        # Laravel: $user->engineerRate()->create(['rate_per_hour' => $ratePerHour])
        engineer_rate = EngineerRate(
            user_id=user.id,
            rate_per_hour=rate_per_hour
        )
        self.db.add(engineer_rate)

        # Attach user to address (many-to-many via engineer_addresses)
        stmt = engineer_addresses.insert().values(user_id=user.id, address_id=address_id)
        await self.db.execute(stmt)

        await self.db.commit()
        await self.db.refresh(user)

        # TODO: Generate password reset token
        # TODO: Send staff invitation email
        # In Laravel: Password::createToken($user) and SendStaffInvitationJob

        return user

    async def list_members(self, company_id: int) -> List[Dict[str, Any]]:
        """
        List all team members for a company.

        Gets all addresses (studios) for the company and returns all team members
        attached to those addresses with their roles and rates.

        Args:
            company_id: Company ID

        Returns:
            List of team members with their details
        """
        from sqlalchemy.orm import selectinload

        # Get all address IDs for this company
        stmt = select(Address.id).where(Address.company_id == company_id)
        result = await self.db.execute(stmt)
        address_ids = [row[0] for row in result.all()]

        if not address_ids:
            return []

        # Get all unique users attached to these addresses via engineer_addresses
        stmt = (
            select(User)
            .join(engineer_addresses, User.id == engineer_addresses.c.user_id)
            .where(engineer_addresses.c.address_id.in_(address_ids))
            .options(selectinload(User.engineer_rate))
            .distinct()
        )
        result = await self.db.execute(stmt)
        users = result.scalars().all()

        # Format response - Laravel compatible with roles array
        staff_list = []
        for user in users:
            # Get the address_id for this user (get the first one for pivot data)
            stmt = (
                select(engineer_addresses.c.address_id)
                .where(engineer_addresses.c.user_id == user.id)
                .where(engineer_addresses.c.address_id.in_(address_ids))
                .limit(1)
            )
            result = await self.db.execute(stmt)
            address_id_row = result.first()
            address_id = address_id_row[0] if address_id_row else None

            staff_list.append({
                "id": user.id,
                "name": user.name,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "profile_photo": user.profile_photo,
                "booking_count": 0,  # TODO: Calculate actual booking count
                # Laravel Spatie Permission format: roles array with objects
                "roles": [{"name": user.role}],
                # Pivot data for address relationship
                "pivot": {
                    "address_id": address_id,
                    "user_id": user.id,
                },
                # Engineer rate (Laravel: engineerRate relationship)
                "engineerRate": {
                    "rate_per_hour": float(user.engineer_rate.rate_per_hour) if user.engineer_rate else None,
                } if user.engineer_rate else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            })

        return staff_list

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

        # Authorization check: verify user is admin of the address's company
        if address.company_id:
            company_repo = CompanyRepository(self.db)
            company_service = CompanyService(company_repo)
            if not await company_service.is_admin(address.company_id, current_user_id):
                raise ForbiddenException("You are not authorized to manage team members for this address")

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
