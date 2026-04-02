"""Обработчики сообщений Telegram."""

import json
import logging
from datetime import date
from typing import Any

from aiogram import Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import Settings
from bot.services.backend_client import BackendAPIError, BackendClient
from bot.services.llm import LLMService

logger = logging.getLogger(__name__)
router = Router()


# ---------------------------------------------------------------------------
# Утилиты: фильтрация обращений
# ---------------------------------------------------------------------------


def _is_reply_to_bot(message: Message, bot_username: str) -> bool:
    """Сообщение является reply на сообщение бота."""
    reply = message.reply_to_message
    return bool(
        reply and reply.from_user and reply.from_user.username == bot_username
    )


def _has_bot_mention(message: Message, bot_username: str) -> bool:
    """Сообщение содержит @mention бота."""
    if not message.entities:
        return False
    target = f"@{bot_username.lower()}"
    return any(
        entity.type == "mention"
        and message.text[entity.offset : entity.offset + entity.length].lower()
        == target
        for entity in message.entities
    )


def _is_bot_addressed(message: Message, bot_username: str) -> bool:
    """Проверяет, обращаются ли к боту: личка, mention или reply."""
    if message.chat.type == ChatType.PRIVATE:
        return True
    return _is_reply_to_bot(message, bot_username) or _has_bot_mention(
        message, bot_username
    )


def _clean_mention(text: str, bot_username: str) -> str:
    """Убирает @bot_username из текста сообщения."""
    return text.replace(f"@{bot_username}", "").strip()


# ---------------------------------------------------------------------------
# Парсинг ответа LLM
# ---------------------------------------------------------------------------


def _extract_json(text: str) -> dict | None:
    """Извлекает первый JSON-объект из текста."""
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end <= start:
        return None
    try:
        data = json.loads(text[start:end])
        return data if isinstance(data, dict) and "reply" in data else None
    except json.JSONDecodeError:
        return None


def _parse_llm_response(text: str) -> dict:
    """Парсит JSON из ответа LLM. Fallback — raw-текст как reply."""
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "reply" in data:
            return data
    except json.JSONDecodeError:
        pass

    return _extract_json(text) or {"action": None, "params": {}, "reply": text}


# ---------------------------------------------------------------------------
# Исключения и валидация
# ---------------------------------------------------------------------------


class ActionError(Exception):
    """Ошибка выполнения действия."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def _validate_required(params: dict[str, Any], required: set[str]) -> None:
    """Проверяет наличие обязательных полей."""
    missing = required - set(params.keys())
    if missing:
        raise ActionError(f"Отсутствуют обязательные поля: {', '.join(missing)}")


def _parse_date(value: Any, field_name: str) -> date:
    """Парсит дату из строки ISO format."""
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError) as e:
        raise ActionError(f"Неверный формат даты в поле '{field_name}': {value}") from e


def _parse_int(value: Any, field_name: str) -> int:
    """Парсит целое число."""
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (ValueError, TypeError) as e:
        raise ActionError(f"Неверное число в поле '{field_name}': {value}") from e


# ---------------------------------------------------------------------------
# Форматирование контекста для LLM
# ---------------------------------------------------------------------------


def _format_booking_line(booking: dict[str, Any]) -> str:
    """Форматирует бронирование в одну строку для контекста."""
    guests = booking.get("guests_planned", [])
    total_guests = sum(g.get("count", 0) for g in guests)
    return (
        f"- [{booking['id']}] Дом {booking['house_id']}: "
        f"{booking['check_in']} — {booking['check_out']}, "
        f"{total_guests} чел., статус: {booking['status']}"
    )


async def _build_context(backend: BackendClient) -> str:
    """Собирает контекст бронирований для LLM."""
    try:
        bookings = await backend.get_bookings()
        active = [b for b in bookings if b.get("status") != "cancelled"]
        if not active:
            return "Нет активных бронирований."
        return "\n".join(_format_booking_line(b) for b in active)
    except BackendAPIError as e:
        logger.warning("Failed to build context: %s", e.message)
        return "Не удалось загрузить бронирования."


# ---------------------------------------------------------------------------
# Диспатч действий LLM → Backend API
# ---------------------------------------------------------------------------


async def _find_house_by_name(backend: BackendClient, name: str) -> dict[str, Any] | None:
    """Ищет дом по названию (частичное совпадение)."""
    houses = await backend.get_houses()
    name_lower = name.lower()
    for house in houses:
        if name_lower in house.get("name", "").lower():
            return house
    # Если не нашли — берем первый активный
    for house in houses:
        if house.get("is_active", True):
            return house
    return None


class BookingActionError(ActionError):
    """Ошибка при создании бронирования — требует отмены reply от LLM."""

    pass


async def _create_booking(
    params: dict[str, Any], user_id: int, backend: BackendClient
) -> str | None:
    """Создаёт бронирование через API."""
    _validate_required(params, {"house", "check_in", "check_out", "guests"})

    # Находим дом по названию
    house = await _find_house_by_name(backend, str(params["house"]))
    if not house:
        raise BookingActionError("Дом не найден.")

    # Получаем тарифы для формирования guests
    tariffs = await backend.get_tariffs()
    default_tariff = tariffs[0] if tariffs else {"id": 1}

    guests_count = _parse_int(params["guests"], "guests")
    guests = [{"tariff_id": default_tariff["id"], "count": guests_count}]

    try:
        await backend.create_booking(
            house_id=house["id"],
            check_in=_parse_date(params["check_in"], "check_in"),
            check_out=_parse_date(params["check_out"], "check_out"),
            guests=guests,
        )
        return None
    except BackendAPIError as e:
        raise BookingActionError(f"Ошибка при создании бронирования: {e.message}") from e


async def _cancel_booking(
    params: dict[str, Any], user_id: int, backend: BackendClient
) -> str | None:
    """Отменяет бронирование через API."""
    _validate_required(params, {"booking_id"})

    booking_id = str(params["booking_id"])
    # Пытаемся распарсить как число
    try:
        booking_id_int = int(booking_id)
    except ValueError:
        # Ищем по короткому ID в списке бронирований пользователя
        bookings = await backend.get_bookings(user_id=user_id)
        for b in bookings:
            if str(b["id"]) == booking_id:
                booking_id_int = b["id"]
                break
        else:
            return f"Бронирование с ID {booking_id} не найдено."

    try:
        await backend.cancel_booking(booking_id_int)
        return None
    except BackendAPIError as e:
        return f"Ошибка при отмене: {e.message}"


def _coerce_booking_fields(params: dict[str, Any]) -> dict[str, Any]:
    """Приводит типы полей бронирования из строк LLM."""
    coerced: dict[str, Any] = {}
    for key, value in params.items():
        if key in ("check_in", "check_out"):
            coerced[key] = _parse_date(value, key)
        elif key == "guests":
            coerced[key] = _parse_int(value, key)
        else:
            coerced[key] = value
    return coerced


async def _update_booking(
    params: dict[str, Any], user_id: int, backend: BackendClient
) -> str | None:
    """Обновляет бронирование через API."""
    _validate_required(params, {"booking_id"})

    booking_id = str(params.pop("booking_id"))
    # Пытаемся распарсить как число
    try:
        booking_id_int = int(booking_id)
    except ValueError:
        # Ищем по короткому ID в списке бронирований пользователя
        bookings = await backend.get_bookings(user_id=user_id)
        for b in bookings:
            if str(b["id"]) == booking_id:
                booking_id_int = b["id"]
                break
        else:
            return f"Бронирование с ID {booking_id} не найдено."

    fields = _coerce_booking_fields(params)
    logger.info(f"Update booking {booking_id_int} with fields: {fields}")

    try:
        await backend.update_booking(booking_id_int, **fields)
        return None
    except BackendAPIError as e:
        return f"Ошибка при обновлении: {e.message}"


ACTION_DISPATCH: dict[str, callable] = {
    "create_booking": _create_booking,
    "cancel_booking": _cancel_booking,
    "update_booking": _update_booking,
}


async def _execute_action(
    action: str | None,
    params: dict[str, Any],
    user_id: int,
    backend: BackendClient,
) -> tuple[str | None, bool]:
    """Выполняет действие из ответа LLM.

    Returns:
        tuple: (сообщение об ошибке или None, флаг отмены reply от LLM)
    """
    if not action or action == "null":
        return None, False

    handler = ACTION_DISPATCH.get(action)
    if not handler:
        logger.warning("Неизвестное действие: %s", action)
        return None, False

    try:
        error = await handler(params, user_id, backend)
        return error, False
    except BookingActionError as e:
        logger.warning("Ошибка бронирования %s: %s", action, e.message)
        return e.message, True
    except ActionError as e:
        logger.warning("Ошибка валидации действия %s: %s", action, e.message)
        return e.message, False
    except Exception:
        logger.exception("Неожиданная ошибка выполнения действия %s", action)
        return "Ошибка при выполнении действия.", False


# ---------------------------------------------------------------------------
# Хэндлеры aiogram
# ---------------------------------------------------------------------------


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Приветствие при первом запуске."""
    await message.answer(
        "Привет! Я бот для бронирования загородных домов.\n\n"
        "Просто напиши мне, что хочешь забронировать, "
        "и я всё устрою (с шутками и подколками, конечно).\n\n"
        "Команды:\n"
        "/bookings — мои бронирования\n"
        "/help — справка"
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Справка по использованию бота."""
    await message.answer(
        "Я понимаю естественный язык. Примеры:\n\n"
        '- "Забронируй старый дом на следующие выходные, 6 человек"\n'
        '- "Сколько народу будет 15 марта?"\n'
        '- "Отмени моё бронирование"\n\n'
        "В групповом чате обращайся через @mention или reply на моё сообщение."
    )


@router.message(Command("bookings"))
async def cmd_bookings(message: Message, backend: BackendClient) -> None:
    """Показывает бронирования текущего пользователя."""
    if not message.from_user:
        return

    # Получаем или создаем пользователя
    try:
        user = await backend.get_or_create_user_by_telegram(
            telegram_id=str(message.from_user.id),
            name=message.from_user.full_name or str(message.from_user.id),
        )
        bookings = await backend.get_bookings(user_id=user["id"])
    except BackendAPIError as e:
        await message.answer(f"Ошибка при загрузке бронирований: {e.message}")
        return

    if not bookings:
        await message.answer("У тебя пока нет бронирований.")
        return

    lines = []
    for b in bookings:
        guests = b.get("guests_planned", [])
        total = sum(g.get("count", 0) for g in guests)
        lines.append(
            f"- [{b['id']}] Дом {b['house_id']}: "
            f"{b['check_in']} — {b['check_out']}, {total} чел."
        )
    await message.answer("Твои бронирования:\n" + "\n".join(lines))


@router.message()
async def handle_message(
    message: Message,
    settings: Settings,
    backend: BackendClient,
    llm_service: LLMService,
) -> None:
    """Основной обработчик: фильтрация, LLM, диспатч действий."""
    if not message.text or not message.from_user:
        return

    if not _is_bot_addressed(message, settings.bot_username):
        return

    text = _clean_mention(message.text, settings.bot_username)
    if not text:
        return

    # Получаем или создаем пользователя
    try:
        user = await backend.get_or_create_user_by_telegram(
            telegram_id=str(message.from_user.id),
            name=message.from_user.full_name or str(message.from_user.id),
        )
    except BackendAPIError as e:
        await message.answer(f"Ошибка подключения к серверу: {e.message}")
        return

    # Собираем контекст и отправляем в LLM
    context = await _build_context(backend)
    llm_response = await llm_service.chat(message.chat.id, text, context)

    parsed = _parse_llm_response(llm_response)
    reply = parsed.get("reply", "")

    error, cancel_reply = await _execute_action(
        parsed.get("action"),
        parsed.get("params", {}),
        user["id"],
        backend,
    )
    if error:
        if cancel_reply:
            reply = error
        else:
            reply = f"{reply}\n\n{error}" if reply else error

    if reply:
        await message.answer(reply)
