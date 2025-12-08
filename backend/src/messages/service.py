"""
Message service for business logic.
Handles message operations with validation and business rules.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.messages.repository import MessageRepository
from src.messages.models import Message
from src.messages import schemas
from src.auth.models import User
from src.addresses.models import Address
from src.exceptions import NotFoundException, BadRequestException


class MessageService:
    """Service for message business logic."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._repository = MessageRepository(session)

    async def store_message(
        self,
        sender_id: int,
        data: schemas.MessageCreateRequest
    ) -> Message:
        """
        Store a new message.

        Laravel equivalent: MessageController@store

        Args:
            sender_id: ID of authenticated user (sender)
            data: Message creation request data

        Returns:
            Created Message object

        Raises:
            NotFoundException: If recipient or address doesn't exist
            BadRequestException: If sender tries to message themselves
        """
        # Validate sender is not messaging themselves
        if sender_id == data.recipient_id:
            raise BadRequestException("Cannot send message to yourself")

        # Validate recipient exists
        recipient = await self._session.get(User, data.recipient_id)
        if not recipient:
            raise NotFoundException(f"Recipient with ID {data.recipient_id} not found")

        # Validate address exists
        address = await self._session.get(Address, data.address_id)
        if not address:
            raise NotFoundException(f"Address with ID {data.address_id} not found")

        # Create message
        message = await self._repository.create_message(
            sender_id=sender_id,
            recipient_id=data.recipient_id,
            address_id=data.address_id,
            content=data.content
        )

        return message

    async def get_message_history(
        self,
        user_id: int,
        recipient_id: int,
        address_id: int
    ) -> List[Message]:
        """
        Get message history between two users for a specific studio.
        Returns bidirectional messages ordered by created_at ASC.

        Laravel equivalent: MessageController@history

        Args:
            user_id: Authenticated user ID
            recipient_id: Other user ID
            address_id: Studio/address ID

        Returns:
            List of Message objects ordered chronologically

        Raises:
            BadRequestException: If user tries to view history with themselves
        """
        if user_id == recipient_id:
            raise BadRequestException("Cannot view message history with yourself")

        messages = await self._repository.get_messages_between_users(
            user1_id=user_id,
            user2_id=recipient_id,
            address_id=address_id
        )

        return messages

    async def get_user_chats(self, user_id: int) -> List[schemas.ChatSummary]:
        """
        Get all chat threads for a user with metadata.

        Laravel equivalent: MessageController@chats

        Returns grouped chats with:
        - customer_id: Other user's ID
        - customer_name: Other user's full name
        - address_id, address_name: Studio info
        - last_message: Preview text
        - last_message_time: Timestamp
        - unread_count: Number of unread messages

        Args:
            user_id: User ID to get chats for

        Returns:
            List of ChatSummary objects
        """
        chat_rows = await self._repository.get_chats_for_user(user_id)

        chat_summaries = []
        for row in chat_rows:
            customer_id, customer_name, address_id, address_name, \
                last_message, last_message_time, message_id, customer_photo = row

            # Get unread count for this chat
            unread_count = await self._repository.count_unread_messages(
                recipient_id=user_id,
                sender_id=customer_id,
                address_id=address_id
            )

            chat_summary = schemas.ChatSummary(
                id=message_id,  # Use last message ID as chat identifier
                customer_id=customer_id,
                customer_name=customer_name or "Unknown",
                customer_photo=customer_photo,
                address_id=address_id,
                address_name=address_name or "Unknown Studio",
                last_message=last_message,
                last_message_time=last_message_time,
                unread_count=unread_count
            )
            chat_summaries.append(chat_summary)

        return chat_summaries

    async def get_chat_details(
        self,
        current_user_id: int,
        id_param: int,
        address_id: Optional[int] = None
    ) -> schemas.ChatDetailsResponse:
        """
        Get detailed chat view with all messages.
        Smart ID resolution: can be message ID or user ID.

        Laravel equivalent: MessageController@chatDetails

        Logic:
        1. Try to find message with id_param
        2. If found: extract address_id and determine chat partner
        3. If not found: treat id_param as user_id
        4. If no address_id provided: find first message between users
        5. Load all messages for that chat thread

        Args:
            current_user_id: Authenticated user ID
            id_param: Can be either message ID or user ID
            address_id: Optional studio/address ID

        Returns:
            ChatDetailsResponse with messages and metadata

        Raises:
            NotFoundException: If chat not found or invalid parameters
        """
        customer_id = None
        resolved_address_id = address_id

        # Try to resolve as message ID first
        message = await self._repository.get_message_by_id(id_param)

        if message:
            # It's a message ID - extract context
            resolved_address_id = message.address_id

            # Determine who the "customer" (other party) is
            if message.sender_id == current_user_id:
                customer_id = message.recipient_id
            else:
                customer_id = message.sender_id
        else:
            # Treat as user ID
            customer_id = id_param

            # If no address_id provided, find first message between users
            if not resolved_address_id:
                first_message = await self._repository.get_first_message_between_users(
                    user1_id=current_user_id,
                    user2_id=customer_id
                )

                if first_message:
                    resolved_address_id = first_message.address_id
                else:
                    # No existing messages - this would be a new chat
                    # For now, raise error (frontend should provide address_id for new chats)
                    raise NotFoundException(
                        "No existing chat found. Please provide address_id for new conversations."
                    )

        # Validate we have all required info
        if not customer_id or not resolved_address_id:
            raise NotFoundException("Could not resolve chat details")

        # Get customer (other user) info
        customer = await self._session.get(User, customer_id)
        if not customer:
            raise NotFoundException(f"User with ID {customer_id} not found")

        # Get address info
        address = await self._session.get(Address, resolved_address_id)
        if not address:
            raise NotFoundException(f"Address with ID {resolved_address_id} not found")

        # Load all messages for this chat
        messages = await self._repository.get_messages_between_users(
            user1_id=current_user_id,
            user2_id=customer_id,
            address_id=resolved_address_id
        )

        # Construct customer name
        customer_name = f"{customer.firstname or ''} {customer.lastname or ''}".strip()
        if not customer_name:
            customer_name = customer.username or customer.email or "Unknown"

        # Build response
        chat_details = schemas.ChatDetailsResponse(
            id=id_param,
            customer_id=customer_id,
            customer_name=customer_name,
            customer_photo=customer.profile_photo,
            address_id=resolved_address_id,
            address_name=address.name or "Unknown Studio",
            messages=[schemas.MessageResponse.model_validate(msg) for msg in messages]
        )

        return chat_details

    async def mark_message_as_read(
        self,
        message_id: int,
        user_id: int
    ) -> bool:
        """
        Mark a message as read (only if user is recipient).

        Args:
            message_id: Message ID to mark as read
            user_id: User attempting to mark as read

        Returns:
            True if successful, False otherwise
        """
        return await self._repository.mark_as_read(message_id, user_id)
