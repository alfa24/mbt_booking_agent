"""SQLAlchemy chat repository."""

from __future__ import annotations

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.chat import Chat, ChatMessage
from backend.schemas.chat import ChatResponse, ChatMessageResponse


class ChatRepository:
    """SQLAlchemy repository for chats and messages."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def create_chat(self, user_id: int, title: str | None = None) -> ChatResponse:
        """Create a new chat.

        Args:
            user_id: User identifier
            title: Optional chat title

        Returns:
            Created chat response
        """
        chat = Chat(user_id=user_id, title=title)
        self._session.add(chat)
        await self._session.flush()
        await self._session.refresh(chat)
        return ChatResponse.model_validate(chat)

    async def get_chat(self, chat_id: int) -> Chat | None:
        """Get chat by ID.

        Args:
            chat_id: Chat identifier

        Returns:
            Chat if found, None otherwise
        """
        result = await self._session.execute(
            select(Chat).where(Chat.id == chat_id)
        )
        return result.scalar_one_or_none()

    async def get_messages(
        self,
        chat_id: int,
        cursor: str | None = None,
        limit: int = 50,
    ) -> list[ChatMessageResponse]:
        """Get messages for a chat with cursor-based pagination.

        Args:
            chat_id: Chat identifier
            cursor: Cursor for pagination (message ID to start before)
            limit: Number of messages to return

        Returns:
            List of chat messages
        """
        query = (
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat_id)
            .order_by(desc(ChatMessage.id))
            .limit(limit)
        )

        if cursor:
            # Cursor is the last message ID seen, get messages before it
            cursor_id = int(cursor)
            query = query.where(ChatMessage.id < cursor_id)

        result = await self._session.execute(query)
        messages = result.scalars().all()
        # Return in chronological order (oldest first)
        return [ChatMessageResponse.model_validate(m) for m in reversed(messages)]

    async def add_message(
        self,
        chat_id: int,
        role: str,
        content: str,
    ) -> ChatMessageResponse:
        """Add a message to a chat.

        Args:
            chat_id: Chat identifier
            role: Message role (user, assistant, system)
            content: Message content

        Returns:
            Created message response
        """
        message = ChatMessage(chat_id=chat_id, role=role, content=content)
        self._session.add(message)
        await self._session.flush()
        await self._session.refresh(message)
        return ChatMessageResponse.model_validate(message)

    async def get_message_count(self, chat_id: int) -> int:
        """Get total message count for a chat.

        Args:
            chat_id: Chat identifier

        Returns:
            Number of messages
        """
        from sqlalchemy import func
        result = await self._session.execute(
            select(func.count()).where(ChatMessage.chat_id == chat_id)
        )
        return result.scalar() or 0
