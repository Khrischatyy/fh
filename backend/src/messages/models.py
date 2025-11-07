"""
Message models.
Defines Message model for user-to-user messaging with studio context.
"""
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models import IDMixin, TimestampMixin

if TYPE_CHECKING:
    from src.auth.models import User
    from src.addresses.models import Address


class Message(Base, IDMixin, TimestampMixin):
    """Message model for communication between users about studios."""

    __tablename__ = "messages"

    # Foreign keys
    sender_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipient_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    address_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("addresses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Message content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    sender: Mapped["User"] = relationship(
        "User",
        back_populates="sent_messages",
        foreign_keys=[sender_id],
    )
    recipient: Mapped["User"] = relationship(
        "User",
        back_populates="received_messages",
        foreign_keys=[recipient_id],
    )
    address: Mapped[Optional["Address"]] = relationship(
        "Address",
        back_populates="messages",
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, sender_id={self.sender_id}, recipient_id={self.recipient_id}, is_read={self.is_read})>"
