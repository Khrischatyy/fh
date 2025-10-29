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

from src.auth.models import User, UserRole, PasswordResetToken
from src.auth.schemas import UserRegister, UserUpdate, ProfileInformationUpdate
from src.config import settings
from src.exceptions import UnauthorizedException, NotFoundException, ConflictException, BadRequestException
import hashlib


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
        """Register a new user - Laravel compatible."""
        # Check if email already exists
        existing_user = await self.get_user_by_email(db, user_data.email)
        if existing_user:
            raise ConflictException("The email has already been taken.")

        # Hash password
        hashed_password = self.hash_password(user_data.password)

        # Create user with name and role (Laravel style)
        user = User(
            name=user_data.name,
            firstname=user_data.name.split()[0] if user_data.name else "User",
            lastname=" ".join(user_data.name.split()[1:]) if len(user_data.name.split()) > 1 else "",
            email=user_data.email,
            password_hash=hashed_password,
            role=user_data.role,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        # TODO: Generate email verification URL and dispatch email job
        # verification_url = generate_signed_url(user.id, user.email, expires_minutes=60)
        # await dispatch_email_verification_job(user, verification_url)

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
                existing_user.profile_photo = avatar
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

    async def create_password_reset_token(self, db: AsyncSession, email: str) -> str:
        """Create and store a password reset token (Laravel-compatible)."""
        # Generate random token
        token = secrets.token_urlsafe(32)

        # Hash the token for storage (Laravel uses bcrypt for tokens)
        hashed_token = self.hash_password(token)

        # Delete any existing tokens for this email
        await db.execute(
            select(PasswordResetToken).filter(PasswordResetToken.email == email)
        )
        existing = await db.execute(
            select(PasswordResetToken).filter(PasswordResetToken.email == email)
        )
        existing_token = existing.scalar_one_or_none()
        if existing_token:
            await db.delete(existing_token)

        # Create new token
        reset_token = PasswordResetToken(
            email=email,
            token=hashed_token,
            created_at=datetime.utcnow()
        )
        db.add(reset_token)
        await db.commit()

        # Return unhashed token to send to user
        return token

    async def verify_password_reset_token(self, db: AsyncSession, email: str, token: str) -> Optional[PasswordResetToken]:
        """Verify a password reset token."""
        result = await db.execute(
            select(PasswordResetToken).filter(PasswordResetToken.email == email)
        )
        reset_token = result.scalar_one_or_none()

        if not reset_token:
            return None

        # Check if token has expired (60 minutes)
        if datetime.utcnow() - reset_token.created_at > timedelta(minutes=60):
            await db.delete(reset_token)
            await db.commit()
            return None

        # Verify token
        if not self.verify_password(token, reset_token.token):
            return None

        return reset_token

    async def delete_password_reset_token(self, db: AsyncSession, email: str) -> None:
        """Delete password reset token after use."""
        result = await db.execute(
            select(PasswordResetToken).filter(PasswordResetToken.email == email)
        )
        token = result.scalar_one_or_none()
        if token:
            await db.delete(token)
            await db.commit()

    async def verify_email_by_hash(self, db: AsyncSession, user_id: int, hash: str) -> Optional[User]:
        """Verify email using Laravel-style id/hash verification. Returns user on success."""
        user = await self.get_user_by_id(db, user_id)
        if not user:
            return None

        # Generate hash from email (Laravel uses sha1)
        expected_hash = hashlib.sha1(user.email.encode()).hexdigest()

        # Compare hashes
        if expected_hash != hash:
            return None

        # Mark email as verified
        user.email_verified_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)

        return user

    async def update_profile_information(
        self,
        db: AsyncSession,
        user: User,
        profile_data: ProfileInformationUpdate
    ) -> User:
        """Update user profile information (Fortify compatible)."""
        update_data = profile_data.model_dump(exclude_unset=True)

        # Handle email change
        if "email" in update_data and update_data["email"] != user.email:
            # Check if email is already taken
            existing = await self.get_user_by_email(db, update_data["email"])
            if existing and existing.id != user.id:
                raise ConflictException("The email has already been taken.")

            # Reset email verification if email changed
            user.email_verified_at = None

        # Handle name field (split into firstname/lastname if provided)
        if "name" in update_data:
            name = update_data.pop("name")
            parts = name.split(maxsplit=1)
            update_data["firstname"] = parts[0] if parts else ""
            update_data["lastname"] = parts[1] if len(parts) > 1 else ""

        # Update user fields
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user

    async def update_password(
        self,
        db: AsyncSession,
        user: User,
        current_password: str,
        new_password: str
    ) -> User:
        """Update user password with current password verification."""
        # Verify current password
        if not user.password_hash or not self.verify_password(current_password, user.password_hash):
            raise BadRequestException("The provided password does not match your current password.")

        # Update password
        user.password_hash = self.hash_password(new_password)
        await db.commit()
        await db.refresh(user)
        return user

    async def confirm_password(self, db: AsyncSession, user: User, password: str) -> bool:
        """Confirm user's password (Fortify compatible)."""
        if not user.password_hash:
            return False
        return self.verify_password(password, user.password_hash)


# Service instance
auth_service = AuthService()
