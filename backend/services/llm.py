"""LLM service for backend."""

import json
import logging
from datetime import date
from typing import Protocol

from openai import APIError, AsyncOpenAI, RateLimitError

from backend.config import settings
from backend.services.llm_tools import (
    BOOKING_TOOLS,
    BookingToolExecutor,
    execute_tool_call,
)

logger = logging.getLogger(__name__)

FALLBACK_RESPONSE = "Упс, мозги перегрелись. Попробуй ещё раз через минутку."

MAX_TOOL_ITERATIONS = 10


class LLMClient(Protocol):
    """Абстракция LLM-провайдера."""

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict:
        """Send chat completion request to LLM.

        Args:
            messages: List of message dicts with role and content
            tools: Optional list of tool definitions

        Returns:
            LLM response as dict with content, tool_calls, and finish_reason
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
            LLM response dict with:
                - content: text content or None
                - tool_calls: list of tool calls or None
                - finish_reason: "stop", "tool_calls", or other
        """
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                tools=tools,
            )
            message = response.choices[0].message

            # Extract tool calls if present
            tool_calls = None
            if message.tool_calls:
                tool_calls = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ]

            return {
                "content": message.content,
                "tool_calls": tool_calls,
                "finish_reason": response.choices[0].finish_reason,
            }
        except RateLimitError:
            logger.warning("Rate limit exceeded")
            return {
                "content": "Слишком много запросов. Подожди немного.",
                "tool_calls": None,
                "finish_reason": "stop",
            }
        except APIError as e:
            logger.error("API ошибка LLM: %s", e.message)
            return {"content": FALLBACK_RESPONSE, "tool_calls": None, "finish_reason": "stop"}
        except Exception:
            logger.exception("Неожиданная ошибка при вызове LLM API")
            return {"content": FALLBACK_RESPONSE, "tool_calls": None, "finish_reason": "stop"}


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
        """Собирает системный промпт с текущей датой и контекстом.

        Args:
            context: Additional context about bookings

        Returns:
            Formatted system prompt
        """
        content = self._system_prompt.format(today=date.today().isoformat())
        if context:
            content += f"\n\n## Контекст\n{context}"
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
            context: Additional context

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
        tool_executor: BookingToolExecutor | None = None,
    ) -> str:
        """Process a user message with LLM and optional tool calling.

        Args:
            history: Previous chat messages
            user_message: Current user message
            context: Additional context
            tool_executor: Optional executor for tool calls

        Returns:
            LLM response content
        """
        messages = self._build_messages(history, user_message, context)

        # Use tools if executor is provided
        tools = BOOKING_TOOLS if tool_executor else None

        # Tool calling loop
        iteration = 0
        while iteration < MAX_TOOL_ITERATIONS:
            iteration += 1
            response = await self._client.chat(messages, tools=tools)

            # If no tool calls, return content
            if not response.get("tool_calls"):
                return response.get("content") or FALLBACK_RESPONSE

            # Process tool calls
            tool_calls = response["tool_calls"]

            # Add assistant message with tool calls to history
            messages.append({
                "role": "assistant",
                "content": response.get("content"),
                "tool_calls": tool_calls,
            })

            # Execute each tool call
            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                tool_args_str = tool_call["function"]["arguments"]

                try:
                    tool_args = json.loads(tool_args_str)
                except json.JSONDecodeError:
                    tool_args = {}

                logger.info("Executing tool: %s with args: %s", tool_name, tool_args)

                # Execute tool
                if tool_executor:
                    result = await execute_tool_call(tool_executor, tool_name, tool_args)
                else:
                    result = json.dumps({"error": "Tool executor not available"})

                logger.info("Tool %s result: %s", tool_name, result)

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": result,
                })

        # Max iterations reached
        logger.warning("Max tool iterations reached")
        return FALLBACK_RESPONSE

    async def process_message_simple(
        self,
        history: list[dict[str, str]],
        user_message: str,
        context: str = "",
    ) -> str:
        """Process message without tool calling (backward compatibility).

        Args:
            history: Previous chat messages
            user_message: Current user message
            context: Additional context

        Returns:
            LLM response content
        """
        messages = self._build_messages(history, user_message, context)
        response = await self._client.chat(messages)
        return response.get("content") or FALLBACK_RESPONSE
