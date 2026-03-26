"""Сервис взаимодействия с LLM через OpenAI-compatible API."""

import logging
from dataclasses import dataclass, field
from datetime import date

from openai import APIError, AsyncOpenAI, RateLimitError

from bot.config import Settings

logger = logging.getLogger(__name__)

MAX_HISTORY_MESSAGES = 20
MAX_HISTORY_PAIRS = 50  # Максимум 50 пар сообщений (100 записей) на чат
FALLBACK_RESPONSE = (
    '{"action": null, "reply": '
    '"Упс, мозги перегрелись. Попробуй ещё раз через минутку."}'
)


@dataclass
class ChatHistory:
    """История диалога с ограничением размера."""

    messages: list[dict[str, str]] = field(default_factory=list)
    max_pairs: int = MAX_HISTORY_PAIRS

    def add_exchange(self, user_msg: str, assistant_msg: str) -> None:
        """Добавляет пару сообщений, удаляя старые при превышении лимита."""
        self.messages.append({"role": "user", "content": user_msg})
        self.messages.append({"role": "assistant", "content": assistant_msg})

        # Храним max_pairs * 2 записей (user + assistant)
        max_records = self.max_pairs * 2
        if len(self.messages) > max_records:
            self.messages = self.messages[-max_records:]

    def get_recent(self, limit: int = MAX_HISTORY_MESSAGES) -> list[dict[str, str]]:
        """Возвращает последние сообщения для контекста."""
        return self.messages[-limit:]


class LLMService:
    """Клиент LLM с поддержкой истории диалогов по чатам."""

    def __init__(self, settings: Settings) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.routerai_api_key,
            base_url=settings.routerai_base_url,
        )
        self._model = settings.llm_model
        self._system_prompt = settings.system_prompt
        self._history: dict[int, ChatHistory] = {}

    def _build_system_content(self, context: str) -> str:
        """Собирает системный промпт с текущей датой и контекстом бронирований."""
        content = self._system_prompt.format(today=date.today().isoformat())
        if context:
            content += f"\n\n## Текущие бронирования\n{context}"
        return content

    def _build_messages(
        self, chat_id: int, user_message: str, context: str
    ) -> list[dict[str, str]]:
        """Формирует список сообщений для запроса к LLM."""
        history = self._history.get(chat_id)
        history_slice = history.get_recent() if history else []
        return [
            {"role": "system", "content": self._build_system_content(context)},
            *history_slice,
            {"role": "user", "content": user_message},
        ]

    def _save_exchange(self, chat_id: int, user_msg: str, assistant_msg: str) -> None:
        """Сохраняет пару user/assistant в историю чата."""
        if chat_id not in self._history:
            self._history[chat_id] = ChatHistory()
        self._history[chat_id].add_exchange(user_msg, assistant_msg)

    async def chat(self, chat_id: int, user_message: str, context: str = "") -> str:
        """Отправляет сообщение в LLM и возвращает ответ."""
        messages = self._build_messages(chat_id, user_message, context)

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
            )
            content = response.choices[0].message.content or ""
        except RateLimitError:
            logger.warning("Rate limit exceeded для чата %s", chat_id)
            return '{"action": null, "reply": "Слишком много запросов. Подожди немного."}'
        except APIError as e:
            logger.error("API ошибка LLM: %s", e.message)
            return FALLBACK_RESPONSE
        except Exception:
            logger.exception("Неожиданная ошибка при вызове LLM API")
            return FALLBACK_RESPONSE

        self._save_exchange(chat_id, user_message, content)
        return content

    def clear_history(self, chat_id: int) -> None:
        """Очищает историю диалога для чата."""
        self._history.pop(chat_id, None)
