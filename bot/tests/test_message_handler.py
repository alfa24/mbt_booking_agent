"""Tests for bot message handler."""

import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock

from bot.handlers.message import (
    _create_booking,
    _execute_action,
    BookingActionError,
    ActionError,
)


class TestCreateBooking:
    """Tests for _create_booking function."""

    @pytest.mark.asyncio
    async def test_create_booking_raises_error_when_house_not_found(self):
        """Test that BookingActionError is raised when house is not found."""
        backend = AsyncMock()
        backend.get_houses.return_value = []  # No houses available
        backend.get_tariffs.return_value = [{"id": 1}]

        params = {
            "house": "несуществующий дом",
            "check_in": "2025-04-05",
            "check_out": "2025-04-06",
            "guests": 5,
        }

        with pytest.raises(BookingActionError) as exc_info:
            await _create_booking(params, user_id=123, backend=backend)

        assert "Дом не найден" in str(exc_info.value.message)

    @pytest.mark.asyncio
    async def test_create_booking_success(self):
        """Test successful booking creation."""
        backend = AsyncMock()
        backend.get_houses.return_value = [{"id": 1, "name": "Старый дом", "is_active": True}]
        backend.get_tariffs.return_value = [{"id": 1}]
        backend.create_booking.return_value = {"id": 42}

        params = {
            "house": "старый",
            "check_in": "2025-04-05",
            "check_out": "2025-04-06",
            "guests": 5,
        }

        result = await _create_booking(params, user_id=123, backend=backend)

        assert result is None  # No error
        backend.create_booking.assert_called_once()
        call_kwargs = backend.create_booking.call_args.kwargs
        assert call_kwargs["house_id"] == 1
        assert call_kwargs["check_in"] == date(2025, 4, 5)
        assert call_kwargs["check_out"] == date(2025, 4, 6)
        assert call_kwargs["guests"] == [{"tariff_id": 1, "count": 5}]

    @pytest.mark.asyncio
    async def test_create_booking_raises_error_on_api_failure(self):
        """Test that BookingActionError is raised when API call fails."""
        from bot.services.backend_client import BackendAPIError

        backend = AsyncMock()
        backend.get_houses.return_value = [{"id": 1, "name": "Старый дом", "is_active": True}]
        backend.get_tariffs.return_value = [{"id": 1}]
        backend.create_booking.side_effect = BackendAPIError("House is not available", 400)

        params = {
            "house": "старый",
            "check_in": "2025-04-05",
            "check_out": "2025-04-06",
            "guests": 5,
        }

        with pytest.raises(BookingActionError) as exc_info:
            await _create_booking(params, user_id=123, backend=backend)

        assert "Ошибка при создании бронирования" in str(exc_info.value.message)


class TestExecuteAction:
    """Tests for _execute_action function."""

    @pytest.mark.asyncio
    async def test_execute_action_returns_cancel_reply_true_on_booking_error(self):
        """Test that cancel_reply=True is returned when BookingActionError occurs."""
        backend = AsyncMock()
        backend.get_houses.return_value = []  # No houses
        backend.get_tariffs.return_value = [{"id": 1}]

        error, cancel_reply = await _execute_action(
            action="create_booking",
            params={
                "house": "несуществующий",
                "check_in": "2025-04-05",
                "check_out": "2025-04-06",
                "guests": 5,
            },
            user_id=123,
            backend=backend,
        )

        assert error == "Дом не найден."
        assert cancel_reply is True  # Should cancel LLM reply

    @pytest.mark.asyncio
    async def test_execute_action_returns_cancel_reply_false_on_validation_error(self):
        """Test that cancel_reply=False is returned on regular ActionError."""
        backend = AsyncMock()

        error, cancel_reply = await _execute_action(
            action="create_booking",
            params={"house": "старый"},  # Missing required fields
            user_id=123,
            backend=backend,
        )

        assert "Отсутствуют обязательные поля" in error
        assert cancel_reply is False  # Should NOT cancel LLM reply

    @pytest.mark.asyncio
    async def test_execute_action_returns_none_on_success(self):
        """Test that no error is returned on successful action execution."""
        backend = AsyncMock()
        backend.get_houses.return_value = [{"id": 1, "name": "Старый дом", "is_active": True}]
        backend.get_tariffs.return_value = [{"id": 1}]
        backend.create_booking.return_value = {"id": 42}

        error, cancel_reply = await _execute_action(
            action="create_booking",
            params={
                "house": "старый",
                "check_in": "2025-04-05",
                "check_out": "2025-04-06",
                "guests": 5,
            },
            user_id=123,
            backend=backend,
        )

        assert error is None
        assert cancel_reply is False

    @pytest.mark.asyncio
    async def test_execute_action_handles_null_action(self):
        """Test that null action returns no error."""
        backend = AsyncMock()

        error, cancel_reply = await _execute_action(
            action=None,
            params={},
            user_id=123,
            backend=backend,
        )

        assert error is None
        assert cancel_reply is False

    @pytest.mark.asyncio
    async def test_execute_action_handles_unknown_action(self):
        """Test that unknown action returns no error."""
        backend = AsyncMock()

        error, cancel_reply = await _execute_action(
            action="unknown_action",
            params={},
            user_id=123,
            backend=backend,
        )

        assert error is None
        assert cancel_reply is False
