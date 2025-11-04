"""
Message router for chat/messaging endpoints.
Laravel-compatible API endpoints for real-time messaging system.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.messages import schemas, service


router = APIRouter(prefix="/messages", tags=["messages"])


@router.post(
    "",
    status_code=status.HTTP_200_OK,
    response_model=schemas.LaravelMessageResponse,
    summary="Store a new message",
    description="Send a new message to another user about a specific studio. Laravel compatible: POST /api/v1/messages"
)
async def store_message(
    data: Annotated[schemas.MessageCreateRequest, Body(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Store a new message.

    Laravel equivalent: POST /api/v1/messages

    Request body:
    - recipient_id: User ID to send message to
    - address_id: Studio/address ID context
    - content: Message text (max 2000 chars)

    Returns:
    - Message object with id, timestamps, etc.
    """
    message_service = service.MessageService(db)

    message = await message_service.store_message(
        sender_id=current_user.id,
        data=data
    )

    return schemas.LaravelMessageResponse(
        data=schemas.MessageResponse.model_validate(message),
        message="Message saved"
    )


@router.post(
    "/history",
    status_code=status.HTTP_200_OK,
    response_model=schemas.LaravelMessagesResponse,
    summary="Get message history",
    description="Get all messages between two users for a specific studio. Laravel compatible: POST /api/v1/messages/history"
)
async def get_message_history(
    data: Annotated[schemas.MessageHistoryRequest, Body(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get message history between current user and another user.

    Laravel equivalent: POST /api/v1/messages/history

    Request body:
    - recipient_id: Other user's ID
    - address_id: Studio/address ID to filter messages

    Returns:
    - List of messages ordered by created_at ASC (oldest first)
    - Bidirectional: shows messages sent and received
    """
    message_service = service.MessageService(db)

    messages = await message_service.get_message_history(
        user_id=current_user.id,
        recipient_id=data.recipient_id,
        address_id=data.address_id
    )

    return schemas.LaravelMessagesResponse(
        data=[schemas.MessageResponse.model_validate(msg) for msg in messages],
        message="Message history"
    )


@router.get(
    "/chats",
    status_code=status.HTTP_200_OK,
    response_model=schemas.LaravelChatsResponse,
    summary="Get all chats",
    description="Get list of all chat threads for current user with last message preview. Laravel compatible: GET /api/v1/messages/chats"
)
async def get_chats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get all chat threads for the authenticated user.

    Laravel equivalent: GET /api/v1/messages/chats

    Returns grouped chats with:
    - customer_id, customer_name: Other user info
    - address_id, address_name: Studio info
    - last_message: Preview of most recent message
    - last_message_time: Timestamp of last message
    - unread_count: Number of unread messages in this thread

    Ordered by last_message_time DESC (most recent first)
    """
    message_service = service.MessageService(db)

    chats = await message_service.get_user_chats(user_id=current_user.id)

    return schemas.LaravelChatsResponse(data=chats)


@router.post(
    "/chats/{id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.LaravelChatDetailsResponse,
    summary="Get chat details",
    description="Get detailed chat view with all messages. Smart ID resolution: can be message ID or user ID. Laravel compatible: POST /api/v1/messages/chats/{id}"
)
async def get_chat_details(
    id: int,
    data: Annotated[schemas.ChatDetailsRequest, Body(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get detailed chat view with all messages.

    Laravel equivalent: POST /api/v1/messages/chats/{id}

    Smart ID resolution:
    - If {id} is a message ID: extracts address_id and chat partner automatically
    - If {id} is a user ID: uses provided address_id or finds first chat

    Request body:
    - address_id: (optional) Studio/address ID

    Returns:
    - Chat metadata (customer name, address name)
    - Complete message history for this chat thread
    """
    message_service = service.MessageService(db)

    chat_details = await message_service.get_chat_details(
        current_user_id=current_user.id,
        id_param=id,
        address_id=data.address_id
    )

    return schemas.LaravelChatDetailsResponse(data=chat_details)


@router.post(
    "/{message_id}/read",
    status_code=status.HTTP_200_OK,
    summary="Mark message as read",
    description="Mark a specific message as read. Only recipient can mark messages as read."
)
async def mark_message_as_read(
    message_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Mark a message as read.

    Only the recipient of the message can mark it as read.

    Returns:
    - success: True if marked as read, False if not found or not recipient
    """
    message_service = service.MessageService(db)

    success = await message_service.mark_message_as_read(
        message_id=message_id,
        user_id=current_user.id
    )

    return {
        "success": success,
        "message": "Message marked as read" if success else "Could not mark message as read"
    }
