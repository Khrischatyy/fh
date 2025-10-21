"""
Company models.
Defines Company and AdminCompany models for managing studio companies and their administrators.
"""
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models import IDMixin, TimestampMixin

if TYPE_CHECKING:
    from src.auth.models import User
    from src.addresses.models import Address


class Company(Base, IDMixin, TimestampMixin):
    """Company model representing a studio business entity."""

    __tablename__ = "companies"

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    logo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    # Relationships
    addresses: Mapped[list["Address"]] = relationship(
        "Address",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    admin_companies: Mapped[list["AdminCompany"]] = relationship(
        "AdminCompany",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name={self.name}, slug={self.slug})>"


class AdminCompany(Base, IDMixin, TimestampMixin):
    """Join table between User and Company for company administrators."""

    __tablename__ = "admin_companies"

    # Foreign keys
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    # Temporarily disabled User relationship until properly configured
    # admin: Mapped["User"] = relationship(
    #     "User",
    #     back_populates="admin_companies",
    # )
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="admin_companies",
    )

    def __repr__(self) -> str:
        return f"<AdminCompany(id={self.id}, user_id={self.user_id}, company_id={self.company_id})>"
