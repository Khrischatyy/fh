"""
Authentication and User models.
Defines User, Role, and Permission models with relationships.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Table, Column, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from src.database import Base
from src.models import IDMixin, TimestampMixin

if TYPE_CHECKING:
    from src.companies.models import Company, AdminCompany
    from src.bookings.models import Booking
    from src.messages.models import Message
    from src.payments.models import Payout, SquareToken
    from src.addresses.models import Address


class UserRole(str, enum.Enum):
    """User role enumeration."""
    USER = "user"
    STUDIO_OWNER = "studio_owner"
    ADMIN = "admin"


class PaymentGateway(str, enum.Enum):
    """Payment gateway enumeration."""
    STRIPE = "stripe"
    SQUARE = "square"


# Association table for user favorite studios
favorite_studios = Table(
    "favorite_studios",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("address_id", Integer, ForeignKey("addresses.id", ondelete="CASCADE"), primary_key=True),
)

# Association table for engineer addresses (team members)
engineer_addresses = Table(
    "engineer_addresses",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("address_id", Integer, ForeignKey("addresses.id", ondelete="CASCADE"), primary_key=True),
)


class PasswordResetToken(Base):
    """Password reset token model (Laravel-compatible)."""

    __tablename__ = "password_reset_tokens"

    email: Mapped[str] = mapped_column(String(255), primary_key=True)
    token: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<PasswordResetToken(email={self.email})>"


class User(Base, IDMixin, TimestampMixin):
    """User model for authentication and profile."""

    __tablename__ = "users"

    # Basic info
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    firstname: Mapped[str] = mapped_column(String(100), nullable=False)
    lastname: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column("hashed_password", String(255), nullable=True)

    # Role (Laravel Spatie Permission compatible)
    role: Mapped[str] = mapped_column(String(15), nullable=False, default="user", server_default="user")

    # Contact
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Profile
    profile_photo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # OAuth
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)

    # Status
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Payment
    payment_gateway: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    stripe_account_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Laravel Cashier fields
    stripe_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    pm_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pm_last_four: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Laravel specific fields (for compatibility)
    remember_token: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    two_factor_secret: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    two_factor_recovery_codes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    two_factor_confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="user", lazy="select")
    sent_messages: Mapped[list["Message"]] = relationship("Message", back_populates="sender", lazy="select", foreign_keys="Message.sender_id")
    received_messages: Mapped[list["Message"]] = relationship("Message", back_populates="recipient", lazy="select", foreign_keys="Message.recipient_id")
    payouts: Mapped[list["Payout"]] = relationship("Payout", back_populates="user", lazy="select")
    admin_companies: Mapped[list["AdminCompany"]] = relationship("AdminCompany", back_populates="admin", lazy="select")
    square_tokens: Mapped[list["SquareToken"]] = relationship("SquareToken", back_populates="user", lazy="select")
    favorite_addresses: Mapped[list["Address"]] = relationship("Address", secondary=favorite_studios, lazy="select")
    engineer_addresses: Mapped[list["Address"]] = relationship("Address", secondary=engineer_addresses, lazy="select")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
