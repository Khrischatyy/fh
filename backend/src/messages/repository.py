"""
Message repository for database operations.
Handles all database queries for messages and chats.
"""
from typing import List, Optional, Tuple
from sqlalchemy import select, and_, or_, func, case, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.messages.models import Message
from src.auth.models import User
from src.addresses.models import Address


class MessageRepository:
    """Repository for message data access operations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_message(
        self,
        sender_id: int,
        recipient_id: int,
        address_id: int,
        content: str
    ) -> Message:
        """
        Create a new message.

        Args:
            sender_id: ID of message sender
            recipient_id: ID of message recipient
            address_id: ID of studio/address
            content: Message text content

        Returns:
            Created Message object
        """
        message = Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            address_id=address_id,
            content=content,
            is_read=False
        )

        self._session.add(message)
        await self._session.commit()
        await self._session.refresh(message)

        return message

    async def get_messages_between_users(
        self,
        user1_id: int,
        user2_id: int,
        address_id: int
    ) -> List[Message]:
        """
        Get all messages between two users for a specific address (bidirectional).

        Laravel equivalent:
        Message::where(function($q) use ($senderId, $recipientId) {
            $q->where('sender_id', $senderId)->where('recipient_id', $recipientId);
        })->orWhere(function($q) use ($senderId, $recipientId) {
            $q->where('sender_id', $recipientId)->where('recipient_id', $senderId);
        })->where('address_id', $addressId)->orderBy('created_at', 'asc')->get();

        Args:
            user1_id: First user ID
            user2_id: Second user ID
            address_id: Studio/address ID

        Returns:
            List of Message objects ordered by created_at ASC
        """
        stmt = (
            select(Message)
            .where(
                and_(
                    Message.address_id == address_id,
                    or_(
                        and_(
                            Message.sender_id == user1_id,
                            Message.recipient_id == user2_id
                        ),
                        and_(
                            Message.sender_id == user2_id,
                            Message.recipient_id == user1_id
                        )
                    )
                )
            )
            .order_by(Message.created_at.asc())
        )

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_chats_for_user(self, user_id: int) -> List[Tuple]:
        """
        Get all chat threads for a user with last message preview.
        Groups by address_id and other user (customer_id).

        Laravel equivalent (MessageService@chatsForOwner):
        - Groups messages by address_id and customer_id (other party)
        - Returns last message, timestamp, customer info

        Args:
            user_id: User ID to get chats for

        Returns:
            List of tuples: (customer_id, customer_name, address_id, address_name,
                            last_message, last_message_time, message_id, customer_photo)
        """
        # Subquery to get last message per chat thread
        # A chat thread is identified by (address_id, customer_id)
        # customer_id is the "other person" in the conversation

        # Determine customer_id: if user is sender, customer is recipient, and vice versa
        customer_id_case = case(
            (Message.sender_id == user_id, Message.recipient_id),
            else_=Message.sender_id
        ).label('customer_id')

        # Subquery to get last message timestamp per chat
        last_message_subq = (
            select(
                Message.address_id,
                customer_id_case.label('customer_id'),
                func.max(Message.created_at).label('last_time')
            )
            .where(
                or_(
                    Message.sender_id == user_id,
                    Message.recipient_id == user_id
                )
            )
            .group_by(Message.address_id, customer_id_case)
            .subquery()
        )

        # Main query to get chat details
        stmt = (
            select(
                last_message_subq.c.customer_id,
                func.concat(User.firstname, ' ', User.lastname).label('customer_name'),
                last_message_subq.c.address_id,
                Address.name.label('address_name'),
                Message.content.label('last_message'),
                Message.created_at.label('last_message_time'),
                Message.id.label('message_id'),
                User.profile_photo.label('customer_photo')
            )
            .select_from(last_message_subq)
            .join(
                Message,
                and_(
                    Message.address_id == last_message_subq.c.address_id,
                    or_(
                        and_(
                            Message.sender_id == user_id,
                            Message.recipient_id == last_message_subq.c.customer_id
                        ),
                        and_(
                            Message.sender_id == last_message_subq.c.customer_id,
                            Message.recipient_id == user_id
                        )
                    ),
                    Message.created_at == last_message_subq.c.last_time
                )
            )
            .join(User, User.id == last_message_subq.c.customer_id)
            .join(Address, Address.id == last_message_subq.c.address_id)
            .order_by(desc('last_message_time'))
        )

        result = await self._session.execute(stmt)
        return list(result.all())

    async def get_message_by_id(self, message_id: int) -> Optional[Message]:
        """
        Get a specific message by ID with relationships loaded.

        Args:
            message_id: Message ID

        Returns:
            Message object or None
        """
        stmt = (
            select(Message)
            .options(
                selectinload(Message.sender),
                selectinload(Message.recipient),
                selectinload(Message.address)
            )
            .where(Message.id == message_id)
        )

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_first_message_between_users(
        self,
        user1_id: int,
        user2_id: int
    ) -> Optional[Message]:
        """
        Get the first message between two users (any address).
        Used to discover chat context when address_id not provided.

        Args:
            user1_id: First user ID
            user2_id: Second user ID

        Returns:
            First Message object or None
        """
        stmt = (
            select(Message)
            .where(
                or_(
                    and_(
                        Message.sender_id == user1_id,
                        Message.recipient_id == user2_id
                    ),
                    and_(
                        Message.sender_id == user2_id,
                        Message.recipient_id == user1_id
                    )
                )
            )
            .order_by(Message.created_at.asc())
            .limit(1)
        )

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_unread_messages(
        self,
        recipient_id: int,
        sender_id: int,
        address_id: int
    ) -> int:
        """
        Count unread messages for a specific chat thread.

        Args:
            recipient_id: User who should read the messages
            sender_id: User who sent the messages
            address_id: Studio/address ID

        Returns:
            Number of unread messages
        """
        stmt = (
            select(func.count(Message.id))
            .where(
                and_(
                    Message.recipient_id == recipient_id,
                    Message.sender_id == sender_id,
                    Message.address_id == address_id,
                    Message.is_read == False
                )
            )
        )

        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def mark_as_read(
        self,
        message_id: int,
        user_id: int
    ) -> bool:
        """
        Mark a message as read (only if user is the recipient).

        Args:
            message_id: Message ID to mark as read
            user_id: User ID attempting to mark as read

        Returns:
            True if marked as read, False if not found or not recipient
        """
        message = await self.get_message_by_id(message_id)

        if not message or message.recipient_id != user_id:
            return False

        message.is_read = True
        await self._session.commit()
        return True
