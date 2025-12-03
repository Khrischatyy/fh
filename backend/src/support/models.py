"""
Support ticket models.
Defines SupportTicket model for customer support requests.
"""
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from src.database import Base
from src.models import IDMixin, TimestampMixin

if TYPE_CHECKING:
    from src.auth.models import User


class TicketStatus(str, enum.Enum):
    """Support ticket status enum."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    """Support ticket priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class SupportTicket(Base, IDMixin, TimestampMixin):
    """Support ticket model for customer support requests."""

    __tablename__ = "support_tickets"

    # User who created the ticket (optional for anonymous)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Contact info (for anonymous users or override)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Ticket content
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    # Status and priority
    status: Mapped[TicketStatus] = mapped_column(
        SQLEnum(TicketStatus, native_enum=False),
        default=TicketStatus.OPEN,
        nullable=False,
        index=True,
    )
    priority: Mapped[TicketPriority] = mapped_column(
        SQLEnum(TicketPriority, native_enum=False),
        default=TicketPriority.MEDIUM,
        nullable=False,
    )

    # Assigned support team member (optional)
    assigned_to_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Admin notes (internal)
    admin_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="support_tickets",
        foreign_keys=[user_id],
    )
    assigned_to: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[assigned_to_id],
    )

    def __repr__(self) -> str:
        return f"<SupportTicket(id={self.id}, subject='{self.subject}', status={self.status})>"
