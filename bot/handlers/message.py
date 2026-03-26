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
from bot.services.booking import BookingService
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
# Диспатч действий LLM → BookingService
# ---------------------------------------------------------------------------


def _create_booking(params: dict[str, Any], user_id: int, svc: BookingService) -> str | None:
    """Создаёт бронирование из параметров LLM."""
    _validate_required(params, {"house", "check_in", "check_out", "guests"})

    try:
        svc.create(
            house=str(params["house"]),
            check_in=_parse_date(params["check_in"], "check_in"),
            check_out=_parse_date(params["check_out"], "check_out"),
            guests=_parse_int(params["guests"], "guests"),
            user_id=user_id,
        )
    except ValueError as e:
        raise ActionError(f"Ошибка в данных бронирования: {e}") from e
    return None


def _cancel_booking(params: dict[str, Any], _user_id: int, svc: BookingService) -> str | None:
    """Отменяет бронирование."""
    _validate_required(params, {"booking_id"})

    result = svc.cancel(str(params["booking_id"]))
    return None if result else "Бронирование не найдено или уже отменено."


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


def _update_booking(params: dict[str, Any], _user_id: int, svc: BookingService) -> str | None:
    """Обновляет поля бронирования."""
    _validate_required(params, {"booking_id"})

    booking_id = str(params.pop("booking_id"))
    fields = _coerce_booking_fields(params)
    logger.info(f"Update booking {booking_id} with fields: {fields}")
    result = svc.update(booking_id, **fields)
    if result:
        logger.info(f"Booking {booking_id} updated successfully")
        return None
    else:
        logger.warning(f"Booking {booking_id} not found for update")
        return "Бронирование не найдено."


ACTION_DISPATCH: dict[str, callable] = {
    "create_booking": _create_booking,
    "cancel_booking": _cancel_booking,
    "update_booking": _update_booking,
}


def _execute_action(
    action: str | None,
    params: dict[str, Any],
    user_id: int,
    booking_service: BookingService,
) -> str | None:
    """Выполняет действие из ответа LLM. Возвращает сообщение об ошибке или None."""
    # LLM может вернуть строку "null" вместо null
    if not action or action == "null":
        return None

    handler = ACTION_DISPATCH.get(action)
    if not handler:
        logger.warning("Неизвестное действие: %s", action)
        return None

    try:
        return handler(params, user_id, booking_service)
    except ActionError as e:
        logger.warning("Ошибка валидации действия %s: %s", action, e.message)
        return e.message
    except Exception:
        logger.exception("Неожиданная ошибка выполнения действия %s", action)
        return "Ошибка при выполнении действия."


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
async def cmd_bookings(message: Message, booking_service: BookingService) -> None:
    """Показывает бронирования текущего пользователя."""
    if not message.from_user:
        return
    bookings = booking_service.get_by_user(message.from_user.id)
    if not bookings:
        await message.answer("У тебя пока нет бронирований.")
        return
    lines = "\n".join(b.format_line() for b in bookings)
    await message.answer(f"Твои бронирования:\n{lines}")


@router.message()
async def handle_message(
    message: Message,
    settings: Settings,
    booking_service: BookingService,
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

    context = booking_service.format_context()
    llm_response = await llm_service.chat(message.chat.id, text, context)

    parsed = _parse_llm_response(llm_response)
    reply = parsed.get("reply", "")

    error = _execute_action(
        parsed.get("action"),
        parsed.get("params", {}),
        message.from_user.id,
        booking_service,
    )
    if error:
        reply = f"{reply}\n\n{error}" if reply else error

    if reply:
        await message.answer(reply)
