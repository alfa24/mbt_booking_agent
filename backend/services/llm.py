"""LLM service for backend."""

import logging
from datetime import date
from typing import Protocol

from openai import APIError, AsyncOpenAI, RateLimitError

from backend.config import settings

logger = logging.getLogger(__name__)

FALLBACK_RESPONSE = (
    '{"action": null, "reply": '
    '"Упс, мозги перегрелись. Попробуй ещё раз через минутку."}'
)


class LLMClient(Protocol):
    """Абстракция LLM-провайдера."""

    async def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """Send chat completion request to LLM.

        Args:
            messages: List of message dicts with role and content
            tools: Optional list of tool definitions

        Returns:
            LLM response as dict
        """
        ...


class RouterAIClient:
    """Реализация для RouterAI (OpenAI-compatible)."""

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        """Initialize RouterAI client.

        Args:
            api_key: API key for authentication
            base_url: Base URL for the API
            model: Model name to use
        """
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self._model = model

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict:
        """Send chat completion request to RouterAI.

        Args:
            messages: List of message dicts with role and content
            tools: Optional list of tool definitions

        Returns:
            LLM response content
        """
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                tools=tools,
            )
            return {"content": response.choices[0].message.content or ""}
        except RateLimitError:
            logger.warning("Rate limit exceeded")
            return {
                "content": '{"action": null, "reply": "Слишком много запросов. Подожди немного."}'
            }
        except APIError as e:
            logger.error("API ошибка LLM: %s", e.message)
            return {"content": FALLBACK_RESPONSE}
        except Exception:
            logger.exception("Неожиданная ошибка при вызове LLM API")
            return {"content": FALLBACK_RESPONSE}


class LLMService:
    """Бизнес-логика: system prompt, tools, history из БД."""

    def __init__(
        self,
        client: LLMClient | None = None,
        system_prompt: str | None = None,
    ) -> None:
        """Initialize LLM service.

        Args:
            client: LLM client implementation (defaults to RouterAI)
            system_prompt: System prompt template (defaults to config)
        """
        self._client = client or RouterAIClient(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            model=settings.llm_model,
        )
        self._system_prompt = system_prompt or settings.system_prompt

    @property
    def client(self) -> LLMClient:
        """Get LLM client instance.

        Returns:
            The underlying LLM client
        """
        return self._client

    def _build_system_content(self, context: str = "") -> str:
        """Собирает системный промпт с текущей датой и контекстом бронирований.

        Args:
            context: Additional context about bookings

        Returns:
            Formatted system prompt
        """
        content = self._system_prompt.format(today=date.today().isoformat())
        if context:
            content += f"\n\n## Текущие бронирования\n{context}"
        return content

    def _build_messages(
        self,
        history: list[dict[str, str]],
        user_message: str,
        context: str = "",
    ) -> list[dict[str, str]]:
        """Формирует список сообщений для запроса к LLM.

        Args:
            history: Previous chat messages
            user_message: Current user message
            context: Additional context about bookings

        Returns:
            List of messages for LLM
        """
        return [
            {"role": "system", "content": self._build_system_content(context)},
            *history,
            {"role": "user", "content": user_message},
        ]

    async def process_message(
        self,
        history: list[dict[str, str]],
        user_message: str,
        context: str = "",
    ) -> str:
        """Process a user message with LLM.

        Args:
            history: Previous chat messages
            user_message: Current user message
            context: Additional context about bookings

        Returns:
            LLM response content
        """
        messages = self._build_messages(history, user_message, context)
        response = await self._client.chat(messages)
        return response.get("content", FALLBACK_RESPONSE)
