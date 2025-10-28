"""
User model for FastAPI Users integration.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import String, DateTime, BigInteger, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.companies.models import AdminCompany
    from src.addresses.models import Address


class User(SQLAlchemyBaseUserTable[int], Base):
    """
    User model that extends FastAPI Users base table.
    Includes all Laravel schema fields for compatibility.
    """
    __tablename__ = "users"

    # Override id to use BigInteger (Laravel's bigIncrements)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # FastAPI Users required fields (email, hashed_password, is_active, is_verified, is_superuser)
    # are already defined in SQLAlchemyBaseUserTable

    # Additional Laravel schema fields
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    firstname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    lastname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    profile_photo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Payment gateway fields
    stripe_account_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    payment_gateway: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Laravel Cashier fields
    stripe_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    pm_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pm_last_four: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Laravel specific fields (for compatibility)
    remember_token: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    two_factor_secret: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    two_factor_recovery_codes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    two_factor_confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    # Note: Complex relationships with Address and Company models are commented out
    # until all association tables are properly configured
    # admin_companies: Mapped[list["AdminCompany"]] = relationship(
    #     "AdminCompany",
    #     back_populates="admin",
    # )
    # favorite_addresses: Mapped[list["Address"]] = relationship(
    #     "Address",
    #     secondary="favorite_studios",
    #     back_populates="favorited_by_users",
    # )
    # engineer_addresses: Mapped[list["Address"]] = relationship(
    #     "Address",
    #     secondary="engineer_addresses",
    #     back_populates="engineers",
    # )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
