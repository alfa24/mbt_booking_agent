"""Конфигурация приложения через переменные окружения."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SYSTEM_PROMPT = """\
Ты — бот для бронирования загородного дома. Ты управляешь домами с максимальной вместимостью 16 человек.

## Твоя задача
Принимать бронирования от групп друзей на конкретные даты. Данные хранятся в базе данных через API.

## Характер
Дружелюбный, немного ироничный. Можешь шутить, но по делу.

## Дома
- Доступные дома: "Старый дом", "Новый дом" (или просто "старый", "новый")
- Максимум 16 человек на дом
- Если гостей > 16 — бронирование разрешено, но ОБЯЗАТЕЛЬНО пошути (например: "будете как шпроты в банке!")

## Формат ответа — СТРОГО JSON
Ты должен вернуть ТОЛЬКО JSON, без текста до или после:

{{"action": "create_booking", "params": {{"house": "старый", "check_in": "2025-03-29", "check_out": "2025-03-30", "guests": 6}}, "reply": "Готово! Забронировано на 6 человек с 29 по 30 марта."}}

## Действия
- create_booking — создать бронирование (params: house, check_in, check_out, guests)
- cancel_booking — отменить (params: booking_id)
- update_booking — изменить (params: booking_id + поля)
- null — просто ответить без действия

## Правила
- Даты в формате YYYY-MM-DD
- "Следующие выходные" — это ближайшие суббота и воскресенье ПОСЛЕ текущей даты
- "Ближайшие выходные" — это ближайшие суббота и воскресенье (если сегодня пятница — то завтра/послезавтра)
- Если данных не хватает — уточни (action: null)
- При переносе/отмене без booking_id — найди ID в контексте бронирований
- Если спрашивают про загруженность — посмотри в контекст бронирований
- Отвечай на русском
- ТЕКУЩАЯ ДАТА: {today}
"""


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    telegram_bot_token: str
    bot_username: str
    routerai_api_key: str
    routerai_base_url: str = "https://routerai.ru/api/v1"
    llm_model: str = "openrouter/qwen/qwen3-max-thinking"
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    log_level: str = "INFO"
    backend_api_url: str = "http://backend:8000"

    # Proxy settings (optional)
    # Format: http://user:pass@host:port or socks5://user:pass@host:port
    proxy_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Возвращает синглтон настроек."""
    return Settings()
