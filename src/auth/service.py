"""
Authentication business logic and user management.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import secrets

from src.auth.models import User, UserRole
from src.auth.schemas import UserRegister, UserUpdate
from src.config import settings
from src.exceptions import UnauthorizedException, NotFoundException, ConflictException


# Password hashing - configure bcrypt to not enforce truncation
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b",
    bcrypt__truncate_error=False
)


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        # Use bcrypt directly to avoid truncation issues
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> dict:
        """Decode a JWT access token."""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            raise UnauthorizedException("Could not validate credentials")

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_google_id(db: AsyncSession, google_id: str) -> Optional[User]:
        """Get user by Google ID."""
        result = await db.execute(select(User).filter(User.google_id == google_id))
        return result.scalar_one_or_none()

    async def register_user(self, db: AsyncSession, user_data: UserRegister) -> User:
        """Register a new user."""
        # Check if email already exists
        existing_user = await self.get_user_by_email(db, user_data.email)
        if existing_user:
            raise ConflictException("Email already registered")

        # Create user
        hashed_password = self.hash_password(user_data.password)
        user = User(
            email=user_data.email,
            firstname=user_data.firstname,
            lastname=user_data.lastname,
            username=user_data.username,
            phone=user_data.phone,
            password_hash=hashed_password,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = await self.get_user_by_email(db, email)
        if not user:
            return None
        if not user.password_hash:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        # Note: is_active check removed since field doesn't exist in Laravel schema
        return user

    async def create_google_user(
        self,
        db: AsyncSession,
        google_id: str,
        email: str,
        firstname: str,
        lastname: str,
        avatar: Optional[str] = None,
    ) -> User:
        """Create user from Google OAuth."""
        # Check if user with email exists
        existing_user = await self.get_user_by_email(db, email)
        if existing_user:
            # Link Google ID to existing user
            existing_user.google_id = google_id
            if avatar:
                existing_user.avatar = avatar
            existing_user.is_verified = True
            existing_user.email_verified_at = datetime.utcnow()
            await db.commit()
            await db.refresh(existing_user)
            return existing_user

        # Create new user
        user = User(
            google_id=google_id,
            email=email,
            firstname=firstname,
            lastname=lastname,
            email_verified_at=datetime.utcnow(),
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    async def update_user(self, db: AsyncSession, user: User, user_data: UserUpdate) -> User:
        """Update user profile."""
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user

    async def set_user_role(self, db: AsyncSession, user: User, role: str) -> User:
        """Set user role."""
        user.role = UserRole(role)
        await db.commit()
        await db.refresh(user)
        return user

    async def verify_email(self, db: AsyncSession, user: User) -> User:
        """Mark user email as verified."""
        user.is_verified = True
        user.email_verified_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    def generate_verification_token() -> str:
        """Generate a secure verification token."""
        return secrets.token_urlsafe(32)

    async def change_password(self, db: AsyncSession, user: User, new_password: str) -> User:
        """Change user password."""
        user.password_hash = self.hash_password(new_password)
        await db.commit()
        await db.refresh(user)
        return user


# Service instance
auth_service = AuthService()
