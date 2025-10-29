"""
Geographic models.
Defines Country and City models for location management.
"""
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models import IDMixin

if TYPE_CHECKING:
    from src.addresses.models import Address


class Country(Base, IDMixin):
    """Country model for geographic location - matches Laravel structure."""

    __tablename__ = "countries"

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # Relationships
    cities: Mapped[list["City"]] = relationship(
        "City",
        back_populates="country",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Country(id={self.id}, name={self.name})>"


class City(Base, IDMixin):
    """City model for geographic location - matches Laravel structure."""

    __tablename__ = "cities"

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Foreign keys
    country_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("countries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    country: Mapped["Country"] = relationship(
        "Country",
        back_populates="cities",
    )
    addresses: Mapped[list["Address"]] = relationship(
        "Address",
        back_populates="city",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<City(id={self.id}, name={self.name}, country_id={self.country_id})>"
