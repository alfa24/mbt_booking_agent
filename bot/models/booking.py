"""Модель данных бронирования."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal
from uuid import uuid4


def _generate_id() -> str:
    """Генерирует короткий UUID для бронирования."""
    return uuid4().hex[:8]


@dataclass(frozen=True, slots=True)
class Booking:
    """Бронирование загородного дома.

    Неизменяемая модель. Для изменения статуса создавайте новый экземпляр
    через `with_status()`.
    """

    house: str
    check_in: date
    check_out: date
    guests: int
    created_by: int
    id: str = field(default_factory=_generate_id)
    created_at: datetime = field(default_factory=datetime.now)
    status: Literal["pending", "confirmed", "cancelled"] = "pending"

    def __post_init__(self) -> None:
        """Валидация после создания."""
        if self.guests <= 0:
            raise ValueError("Количество гостей должно быть положительным")
        if self.check_out <= self.check_in:
            raise ValueError("Дата выезда должна быть позже даты заезда")

    @property
    def is_active(self) -> bool:
        """Бронирование не отменено."""
        return self.status != "cancelled"

    def overlaps(self, target: date) -> bool:
        """Проверяет, попадает ли дата в период бронирования."""
        return self.check_in <= target < self.check_out

    def with_status(self, status: Literal["pending", "confirmed", "cancelled"]) -> "Booking":
        """Создаёт копию бронирования с новым статусом."""
        return Booking(
            house=self.house,
            check_in=self.check_in,
            check_out=self.check_out,
            guests=self.guests,
            created_by=self.created_by,
            id=self.id,
            created_at=self.created_at,
            status=status,
        )

    def format_line(self) -> str:
        """Однострочное представление для контекста LLM."""
        return (
            f"- [{self.id}] {self.house}: {self.check_in} — {self.check_out}, "
            f"{self.guests} чел., статус: {self.status}"
        )
