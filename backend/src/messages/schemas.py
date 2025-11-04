"""
Message schemas for request/response validation.
Laravel-compatible Pydantic models for messages/chat system.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class MessageCreateRequest(BaseModel):
    """
    Schema for creating a new message.
    Laravel compatible: POST /api/v1/messages
    """
    recipient_id: int = Field(..., gt=0, description="Recipient user ID")
    address_id: int = Field(..., gt=0, description="Studio/address ID")
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate message content is not just whitespace."""
        if not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()


class MessageResponse(BaseModel):
    """
    Schema for message response.
    Laravel compatible response format.
    """
    id: int
    sender_id: int
    recipient_id: int
    address_id: Optional[int] = None
    content: str
    is_read: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageHistoryRequest(BaseModel):
    """
    Schema for getting message history between two users.
    Laravel compatible: POST /api/v1/messages/history
    """
    recipient_id: int = Field(..., gt=0, description="Other user ID")
    address_id: int = Field(..., gt=0, description="Studio/address ID")


class ChatSummary(BaseModel):
    """
    Schema for chat list item with metadata.
    Laravel compatible: GET /api/v1/messages/chats
    """
    id: int = Field(..., description="Last message ID or chat identifier")
    customer_id: int = Field(..., description="Other user's ID")
    customer_name: str = Field(..., description="Other user's full name")
    address_id: int = Field(..., description="Studio/address ID")
    address_name: Optional[str] = Field(None, description="Studio name")
    last_message: str = Field(..., description="Preview of last message")
    last_message_time: datetime = Field(..., description="Timestamp of last message")
    unread_count: int = Field(default=0, description="Number of unread messages")


class ChatDetailsRequest(BaseModel):
    """
    Schema for getting chat details.
    Laravel compatible: POST /api/v1/messages/chats/{id}
    """
    address_id: Optional[int] = Field(None, gt=0, description="Studio/address ID (optional)")


class ChatDetailsResponse(BaseModel):
    """
    Schema for detailed chat view with all messages.
    Laravel compatible response.
    """
    id: int = Field(..., description="Chat identifier")
    customer_id: int = Field(..., description="Other user's ID")
    customer_name: str = Field(..., description="Other user's full name")
    address_id: int = Field(..., description="Studio/address ID")
    address_name: Optional[str] = Field(None, description="Studio name")
    messages: List[MessageResponse] = Field(default_factory=list, description="All messages in chat")


class LaravelMessageResponse(BaseModel):
    """
    Laravel-style wrapper for message responses.
    Format: {"data": {...}, "message": "..."}
    """
    data: MessageResponse
    message: str = "Message saved"


class LaravelMessagesResponse(BaseModel):
    """
    Laravel-style wrapper for multiple messages.
    Format: {"data": [...], "message": "..."}
    """
    data: List[MessageResponse]
    message: str = "Message history"


class LaravelChatsResponse(BaseModel):
    """
    Laravel-style wrapper for chats list.
    Format: {"data": [...]}
    """
    data: List[ChatSummary]


class LaravelChatDetailsResponse(BaseModel):
    """
    Laravel-style wrapper for chat details.
    Format: {"data": {...}}
    """
    data: ChatDetailsResponse
