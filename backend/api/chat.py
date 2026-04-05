"""Chat API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.schemas.chat import (
    ChatMessagesListResponse,
    ChatResponse,
    CreateChatRequest,
    SendMessageRequest,
    SendMessageResponse,
)
from backend.schemas.common import ErrorResponse
from backend.services.chat import ChatService

chat_router = APIRouter(prefix="/chats", tags=["chats"])


@chat_router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create chat",
    description="Create a new chat conversation.",
    responses={
        201: {"description": "Chat created successfully"},
        404: {
            "description": "User not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def create_chat(
    request: CreateChatRequest,
    service: Annotated[ChatService, Depends(ChatService)],
) -> ChatResponse:
    """Create a new chat.

    Args:
        request: Chat creation data
        service: Chat service instance

    Returns:
        Created chat with generated ID

    Raises:
        HTTPException: 404 if user not found, 422 if validation fails
    """
    return await service.create_chat(user_id=request.user_id)


@chat_router.get(
    "/{chat_id}/messages",
    response_model=ChatMessagesListResponse,
    summary="Get chat messages",
    description="Get messages for a chat with cursor-based pagination.",
    responses={
        200: {"description": "Messages returned successfully"},
        404: {
            "description": "Chat not found",
            "model": ErrorResponse,
        },
    },
)
async def get_messages(
    chat_id: int,
    service: Annotated[ChatService, Depends(ChatService)],
    # TODO: Replace with actual auth when implementing authentication
    user_id: int = 1,
    cursor: str | None = None,
    limit: int = 50,
) -> ChatMessagesListResponse:
    """Get messages for a chat.

    Args:
        chat_id: Chat identifier
        service: Chat service instance
        user_id: User identifier (from auth)
        cursor: Cursor for pagination
        limit: Number of messages to return

    Returns:
        Paginated list of messages

    Raises:
        HTTPException: 404 if chat not found
    """
    try:
        return await service.get_messages(
            chat_id=chat_id,
            user_id=user_id,
            cursor=cursor,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@chat_router.post(
    "/{chat_id}/messages",
    response_model=SendMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send message",
    description="Send a message to the chat and get LLM response.",
    responses={
        201: {"description": "Message sent successfully"},
        404: {
            "description": "Chat not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def send_message(
    chat_id: int,
    request: SendMessageRequest,
    service: Annotated[ChatService, Depends(ChatService)],
    # TODO: Replace with actual auth when implementing authentication
    user_id: int = 1,
    context: str = "",
) -> SendMessageResponse:
    """Send a message to the chat.

    Args:
        chat_id: Chat identifier
        request: Message data
        service: Chat service instance
        user_id: User identifier (from auth)
        context: Additional context about bookings

    Returns:
        Assistant response message

    Raises:
        HTTPException: 404 if chat not found, 422 if validation fails
    """
    try:
        message = await service.send_message(
            chat_id=chat_id,
            content=request.content,
            user_id=user_id,
            context=context,
        )
        return SendMessageResponse(message=message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
