"""HTTP-клиент для взаимодействия с backend API."""

import logging
from datetime import date
from typing import Any

import httpx

from bot.config import Settings

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3


class BackendAPIError(Exception):
    """Ошибка при обращении к backend API."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class BackendClient:
    """Async HTTP-клиент для backend API."""

    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.backend_api_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy initialization of HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(DEFAULT_TIMEOUT),
                follow_redirects=True,
            )
        return self._client

    async def __aenter__(self) -> "BackendClient":
        """Async context manager entry."""
        await self._get_client()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Выполняет HTTP-запрос с retry-логикой."""
        url = f"{self._base_url}{path}"
        last_error: Exception | None = None

        client = await self._get_client()
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                detail = ""
                try:
                    error_data = e.response.json()
                    detail = error_data.get("message", "")
                except Exception:
                    detail = e.response.text

                if status_code == 404:
                    raise BackendAPIError(f"Не найдено: {detail}", status_code)
                elif status_code == 400:
                    raise BackendAPIError(f"Ошибка запроса: {detail}", status_code)
                elif status_code == 403:
                    raise BackendAPIError(f"Доступ запрещен: {detail}", status_code)
                elif status_code >= 500:
                    last_error = BackendAPIError(
                        f"Ошибка сервера ({status_code}): {detail}", status_code
                    )
                    if attempt < MAX_RETRIES - 1:
                        logger.warning(
                            "Server error, retrying (%d/%d)", attempt + 1, MAX_RETRIES
                        )
                        continue
                    raise last_error
                else:
                    raise BackendAPIError(f"Ошибка {status_code}: {detail}", status_code)
            except httpx.TimeoutException:
                last_error = BackendAPIError("Превышено время ожидания ответа от сервера")
                if attempt < MAX_RETRIES - 1:
                    logger.warning("Timeout, retrying (%d/%d)", attempt + 1, MAX_RETRIES)
                    continue
                raise last_error
            except httpx.ConnectError as e:
                last_error = BackendAPIError(f"Не удалось подключиться к серверу: {e}")
                if attempt < MAX_RETRIES - 1:
                    logger.warning(
                        "Connection error, retrying (%d/%d)", attempt + 1, MAX_RETRIES
                    )
                    continue
                raise last_error
            except Exception as e:
                logger.exception("Unexpected error during API request")
                raise BackendAPIError(f"Неожиданная ошибка: {e}")

        raise last_error or BackendAPIError("Неизвестная ошибка")

    async def close(self) -> None:
        """Закрывает HTTP-клиент."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # -------------------------------------------------------------------------
    # Users
    # -------------------------------------------------------------------------

    async def get_user(self, user_id: int) -> dict[str, Any]:
        """Получает информацию о пользователе."""
        return await self._request("GET", f"/api/v1/users/{user_id}")

    async def create_user(self, telegram_id: str, name: str, role: str = "tenant") -> dict[str, Any]:
        """Создает нового пользователя из Telegram."""
        data = {
            "telegram_id": telegram_id,
            "name": name,
            "role": role,
        }
        return await self._request("POST", "/api/v1/users", json=data)

    async def get_or_create_user_by_telegram(self, telegram_id: str, name: str) -> dict[str, Any]:
        """Получает или создает пользователя по telegram_id."""
        try:
            # Сначала ищем в списке по telegram_id
            users = await self._request(
                "GET", "/api/v1/users", params={"limit": 100}
            )
            for user in users.get("items", []):
                if user.get("telegram_id") == telegram_id:
                    return user
            # Не найден — создаем
            return await self.create_user(telegram_id, name)
        except BackendAPIError:
            # Если не удалось получить список — пробуем создать
            return await self.create_user(telegram_id, name)

    # -------------------------------------------------------------------------
    # Houses
    # -------------------------------------------------------------------------

    async def get_houses(self) -> list[dict[str, Any]]:
        """Получает список всех домов."""
        response = await self._request("GET", "/api/v1/houses")
        return response.get("items", [])

    async def get_house(self, house_id: int) -> dict[str, Any]:
        """Получает информацию о доме."""
        return await self._request("GET", f"/api/v1/houses/{house_id}")

    async def get_house_calendar(
        self, house_id: int, date_from: date | None = None, date_to: date | None = None
    ) -> dict[str, Any]:
        """Получает календарь занятости дома."""
        params: dict[str, Any] = {}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
        return await self._request(
            "GET", f"/api/v1/houses/{house_id}/calendar", params=params
        )

    # -------------------------------------------------------------------------
    # Bookings
    # -------------------------------------------------------------------------

    async def get_bookings(
        self, user_id: int | None = None, house_id: int | None = None
    ) -> list[dict[str, Any]]:
        """Получает список бронирований."""
        params: dict[str, Any] = {"limit": 100}
        if user_id:
            params["user_id"] = user_id
        if house_id:
            params["house_id"] = house_id
        response = await self._request("GET", "/api/v1/bookings", params=params)
        return response.get("items", [])

    async def get_booking(self, booking_id: int) -> dict[str, Any]:
        """Получает информацию о бронировании."""
        return await self._request("GET", f"/api/v1/bookings/{booking_id}")

    async def create_booking(
        self,
        house_id: int,
        check_in: date,
        check_out: date,
        guests: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Создает новое бронирование."""
        data = {
            "house_id": house_id,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "guests": guests,
        }
        return await self._request("POST", "/api/v1/bookings", json=data)

    async def update_booking(
        self, booking_id: int, **fields: Any
    ) -> dict[str, Any]:
        """Обновляет бронирование."""
        # Конвертируем даты в ISO формат
        if "check_in" in fields and isinstance(fields["check_in"], date):
            fields["check_in"] = fields["check_in"].isoformat()
        if "check_out" in fields and isinstance(fields["check_out"], date):
            fields["check_out"] = fields["check_out"].isoformat()
        return await self._request(
            "PATCH", f"/api/v1/bookings/{booking_id}", json=fields
        )

    async def cancel_booking(self, booking_id: int) -> dict[str, Any]:
        """Отменяет бронирование."""
        return await self._request("DELETE", f"/api/v1/bookings/{booking_id}")

    # -------------------------------------------------------------------------
    # Tariffs
    # -------------------------------------------------------------------------

    async def get_tariffs(self) -> list[dict[str, Any]]:
        """Получает список тарифов."""
        response = await self._request("GET", "/api/v1/tariffs")
        return response.get("items", [])

    async def get_tariff(self, tariff_id: int) -> dict[str, Any]:
        """Получает информацию о тарифе."""
        return await self._request("GET", f"/api/v1/tariffs/{tariff_id}")

    # -------------------------------------------------------------------------
    # Chat
    # -------------------------------------------------------------------------

    async def create_chat(self, user_id: int) -> dict[str, Any]:
        """Создаёт новый чат для пользователя."""
        data = {"user_id": user_id}
        return await self._request("POST", "/api/v1/chats", json=data)

    async def send_chat_message(
        self, chat_id: int, content: str, context: str = ""
    ) -> dict[str, Any]:
        """Отправляет сообщение в чат и получает ответ от LLM."""
        data = {"content": content}
        params = {}
        if context:
            params["context"] = context
        return await self._request(
            "POST", f"/api/v1/chats/{chat_id}/messages", json=data, params=params
        )

    async def get_chat_messages(
        self, chat_id: int, cursor: str | None = None, limit: int = 50
    ) -> dict[str, Any]:
        """Получает историю сообщений чата."""
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self._request("GET", f"/api/v1/chats/{chat_id}/messages", params=params)
