"""Сервис взаимодействия с LLM через backend API.

Теперь LLM обрабатывается на backend, бот только проксирует запросы.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.services.backend_client import BackendClient

logger = logging.getLogger(__name__)

FALLBACK_RESPONSE = (
    '{"action": null, "reply": '
    '"Упс, мозги перегрелись. Попробуй ещё раз через минутку."}'
)


class LLMService:
    """Прокси-сервис для LLM через backend API.

    История сообщений хранится на backend, бот только передаёт запросы.
    """

    def __init__(self, backend: "BackendClient") -> None:
        """Initialize with backend client.

        Args:
            backend: Backend API client
        """
        self._backend = backend

    async def chat(
        self,
        chat_id: int,
        user_message: str,
        context: str = "",
    ) -> str:
        """Отправляет сообщение в чат через backend API.

        Args:
            chat_id: Backend chat ID
            user_message: User message text
            context: Additional context about bookings

        Returns:
            LLM response content
        """
        try:
            response = await self._backend.send_chat_message(
                chat_id=chat_id,
                content=user_message,
                context=context,
            )
            # Response is wrapped in {"message": {...}}
            message = response.get("message", {})
            if isinstance(message, dict):
                return message.get("content", FALLBACK_RESPONSE)
            return str(message) if message else FALLBACK_RESPONSE
        except Exception:
            logger.exception("Ошибка при отправке сообщения в чат")
            return FALLBACK_RESPONSE

    def clear_history(self, chat_id: int) -> None:
        """Очищает историю диалога для чата.

        Note: History is managed by backend, this is a no-op for compatibility.
        """
        # Backend manages history, nothing to do here
        pass
