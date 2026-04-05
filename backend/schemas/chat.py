"""Pydantic schemas for Chat resource."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CreateChatRequest(BaseModel):
    """Request schema for creating a new chat."""

    user_id: int = Field(..., ge=1, description="User ID who owns the chat")


class ChatResponse(BaseModel):
    """Chat response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique chat identifier")
    user_id: int = Field(..., description="ID of the chat owner")
    title: Optional[str] = Field(None, description="Chat title")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class SendMessageRequest(BaseModel):
    """Request schema for sending a message to chat."""

    content: str = Field(..., min_length=1, description="Message content")


class ChatMessageResponse(BaseModel):
    """Chat message response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique message identifier")
    chat_id: int = Field(..., description="ID of the chat")
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    created_at: datetime = Field(..., description="Creation timestamp")


class ChatMessagesListResponse(BaseModel):
    """Response schema for paginated chat messages."""

    items: list[ChatMessageResponse] = Field(default_factory=list, description="List of messages")
    cursor: Optional[str] = Field(None, description="Cursor for next page")
    has_more: bool = Field(False, description="Whether there are more messages")


class SendMessageResponse(BaseModel):
    """Response schema for sending a message to chat."""

    message: ChatMessageResponse = Field(..., description="The assistant's response message")


class AudioTranscriptionResponse(BaseModel):
    """Response schema for audio transcription."""

    text: str = Field(..., description="Transcribed text from audio")
