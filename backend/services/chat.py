"""Chat service with business logic."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.dependencies import get_llm_service
from backend.exceptions import UserNotFoundError
from backend.repositories.chat import ChatRepository
from backend.repositories.user import UserRepository
from backend.schemas.chat import (
    ChatMessageResponse,
    ChatMessagesListResponse,
    ChatResponse,
)
from backend.services.llm import LLMService


async def get_chat_repository(
    db: AsyncSession = Depends(get_db),
) -> ChatRepository:
    """Dependency provider for chat repository.

    Args:
        db: Database session from dependency injection

    Returns:
        ChatRepository instance with database session
    """
    return ChatRepository(db)


async def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> UserRepository:
    """Dependency provider for user repository.

    Args:
        db: Database session from dependency injection

    Returns:
        UserRepository instance with database session
    """
    return UserRepository(db)


class ChatService:
    """Service layer for chat operations."""

    def __init__(
        self,
        repository: ChatRepository = Depends(get_chat_repository),
        user_repository: UserRepository = Depends(get_user_repository),
        llm_service: LLMService = Depends(get_llm_service),
    ):
        """Initialize service with repositories.

        Args:
            repository: Chat repository instance
            user_repository: User repository instance
            llm_service: LLM service instance
        """
        self._repo = repository
        self._user_repo = user_repository
        self._llm_service = llm_service

    async def create_chat(self, user_id: int) -> ChatResponse:
        """Create a new chat with welcome message.

        Args:
            user_id: User identifier

        Returns:
            Created chat with welcome message

        Raises:
            UserNotFoundError: If user not found
        """
        # Verify user exists
        user = await self._user_repo.get(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Create chat
        chat = await self._repo.create_chat(user_id=user_id)

        # Add welcome message from assistant
        welcome_msg = (
            "Привет! Я бот для бронирования загородных домов. "
            "Просто напиши мне, что хочешь забронировать, и я всё устрою!"
        )
        await self._repo.add_message(
            chat_id=chat.id,
            role="assistant",
            content=welcome_msg,
        )

        return chat

    async def send_message(
        self,
        chat_id: int,
        content: str,
        user_id: int,
        context: str = "",
    ) -> ChatMessageResponse:
        """Send a message and get LLM response.

        Args:
            chat_id: Chat identifier
            content: User message content
            user_id: User identifier (for verification)
            context: Additional context about bookings

        Returns:
            Assistant message response

        Raises:
            ValueError: If chat not found or user doesn't own chat
        """
        # Verify chat exists and belongs to user
        chat = await self._repo.get_chat(chat_id)
        if not chat:
            raise ValueError(f"Chat {chat_id} not found")
        if chat.user_id != user_id:
            raise ValueError("User does not own this chat")

        # Save user message
        await self._repo.add_message(
            chat_id=chat_id,
            role="user",
            content=content,
        )

        # Get recent history (last 20 messages)
        history_messages = await self._repo.get_messages(chat_id, limit=20)
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in history_messages
            if msg.role in ("user", "assistant")
        ]

        # Get LLM response
        llm_response = await self._llm_service.process_message(
            history=history,
            user_message=content,
            context=context,
        )

        # Save assistant message
        assistant_msg = await self._repo.add_message(
            chat_id=chat_id,
            role="assistant",
            content=llm_response,
        )

        return assistant_msg

    async def get_messages(
        self,
        chat_id: int,
        user_id: int,
        cursor: str | None = None,
        limit: int = 50,
    ) -> ChatMessagesListResponse:
        """Get messages for a chat.

        Args:
            chat_id: Chat identifier
            user_id: User identifier (for verification)
            cursor: Cursor for pagination
            limit: Number of messages to return

        Returns:
            Paginated list of messages

        Raises:
            ValueError: If chat not found or user doesn't own chat
        """
        # Verify chat exists and belongs to user
        chat = await self._repo.get_chat(chat_id)
        if not chat:
            raise ValueError(f"Chat {chat_id} not found")
        if chat.user_id != user_id:
            raise ValueError("User does not own this chat")

        # Get messages
        messages = await self._repo.get_messages(chat_id, cursor=cursor, limit=limit)

        # Determine if there are more messages
        has_more = len(messages) == limit
        next_cursor = None
        if has_more and messages:
            next_cursor = str(messages[-1].id)

        return ChatMessagesListResponse(
            items=messages,
            cursor=next_cursor,
            has_more=has_more,
        )
