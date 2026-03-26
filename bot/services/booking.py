"""Сервис управления бронированиями (in-memory хранилище)."""

import logging
from datetime import date
from typing import Protocol

from bot.models.booking import Booking

logger = logging.getLogger(__name__)

IMMUTABLE_FIELDS = frozenset({"id", "created_by", "created_at"})


class BookingRepository(Protocol):
    """Протокол хранилища бронирований."""

    def create(
        self,
        house: str,
        check_in: date,
        check_out: date,
        guests: int,
        user_id: int,
    ) -> Booking: ...

    def cancel(self, booking_id: str) -> Booking | None: ...

    def update(self, booking_id: str, **fields: object) -> Booking | None: ...

    def get_by_user(self, user_id: int) -> list[Booking]: ...

    def get_for_date(self, target: date, house: str | None = None) -> list[Booking]: ...

    def get_guests_count(self, target: date, house: str) -> int: ...

    def get_all_active(self) -> list[Booking]: ...

    def format_context(self) -> str: ...


class BookingService:
    """CRUD-операции над бронированиями в оперативной памяти."""

    def __init__(self) -> None:
        self._bookings: dict[str, Booking] = {}

    def _active_bookings(self) -> list[Booking]:
        """Возвращает все неотменённые бронирования."""
        return [b for b in self._bookings.values() if b.is_active]

    def create(
        self,
        house: str,
        check_in: date,
        check_out: date,
        guests: int,
        user_id: int,
    ) -> Booking:
        """Создаёт и сохраняет новое бронирование."""
        booking = Booking(
            house=house,
            check_in=check_in,
            check_out=check_out,
            guests=guests,
            created_by=user_id,
        )
        self._bookings[booking.id] = booking
        logger.info("Создано бронирование %s", booking.id)
        return booking

    def cancel(self, booking_id: str) -> Booking | None:
        """Отменяет бронирование. Возвращает None если не найдено."""
        booking = self._bookings.get(booking_id)
        if not booking or not booking.is_active:
            return None
        cancelled = booking.with_status("cancelled")
        self._bookings[booking_id] = cancelled
        logger.info("Отменено бронирование %s", booking_id)
        return cancelled

    def update(self, booking_id: str, **fields: object) -> Booking | None:
        """Обновляет допустимые поля бронирования, создавая новый экземпляр."""
        booking = self._bookings.get(booking_id)
        if not booking or not booking.is_active:
            return None

        # Собираем обновлённые поля
        updated_fields: dict[str, object] = {
            "house": booking.house,
            "check_in": booking.check_in,
            "check_out": booking.check_out,
            "guests": booking.guests,
            "created_by": booking.created_by,
            "id": booking.id,
            "created_at": booking.created_at,
            "status": booking.status,
        }

        for key, value in fields.items():
            if key in updated_fields and key not in IMMUTABLE_FIELDS:
                updated_fields[key] = value

        updated = Booking(**updated_fields)
        self._bookings[booking_id] = updated
        logger.info("Обновлено бронирование %s", booking_id)
        return updated

    def get_by_user(self, user_id: int) -> list[Booking]:
        """Возвращает активные бронирования пользователя."""
        return [b for b in self._active_bookings() if b.created_by == user_id]

    def get_for_date(self, target: date, house: str | None = None) -> list[Booking]:
        """Возвращает бронирования, пересекающиеся с указанной датой."""
        return [
            b
            for b in self._active_bookings()
            if b.overlaps(target) and (house is None or b.house == house)
        ]

    def get_guests_count(self, target: date, house: str) -> int:
        """Считает общее количество гостей на дату в конкретном доме."""
        return sum(b.guests for b in self.get_for_date(target, house))

    def get_all_active(self) -> list[Booking]:
        """Возвращает все активные бронирования."""
        return self._active_bookings()

    def format_context(self) -> str:
        """Форматирует все активные бронирования для контекста LLM."""
        bookings = self._active_bookings()
        if not bookings:
            return "Нет активных бронирований."
        return "\n".join(b.format_line() for b in bookings)
