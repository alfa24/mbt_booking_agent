"""Tool definitions and execution for LLM function calling."""

import json
import logging
from datetime import date
from typing import Any, Protocol

from backend.schemas.booking import (
    BookingFilterParams,
    BookingStatus,
    CreateBookingRequest,
    GuestInfo,
)
from backend.schemas.house import HouseFilterParams

logger = logging.getLogger(__name__)


# Tool definitions for OpenAI-compatible API
BOOKING_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_available_houses",
            "description": "Получить список всех доступных для бронирования домов",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Проверить доступность дома на указанные даты",
            "parameters": {
                "type": "object",
                "properties": {
                    "house_id": {
                        "type": "integer",
                        "description": "ID дома для проверки",
                    },
                    "check_in": {
                        "type": "string",
                        "format": "date",
                        "description": "Дата заезда в формате YYYY-MM-DD",
                    },
                    "check_out": {
                        "type": "string",
                        "format": "date",
                        "description": "Дата выезда в формате YYYY-MM-DD",
                    },
                },
                "required": ["house_id", "check_in", "check_out"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_booking",
            "description": "Создать бронирование дома. Используй этот инструмент когда пользователь хочет забронировать дом.",
            "parameters": {
                "type": "object",
                "properties": {
                    "house_id": {
                        "type": "integer",
                        "description": "ID дома для бронирования",
                    },
                    "check_in": {
                        "type": "string",
                        "format": "date",
                        "description": "Дата заезда в формате YYYY-MM-DD",
                    },
                    "check_out": {
                        "type": "string",
                        "format": "date",
                        "description": "Дата выезда в формате YYYY-MM-DD",
                    },
                    "guests_count": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Количество гостей",
                    },
                },
                "required": ["house_id", "check_in", "check_out", "guests_count"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_booking",
            "description": "Отменить бронирование по ID. Используй когда пользователь хочет отменить своё бронирование.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_id": {
                        "type": "integer",
                        "description": "ID бронирования для отмены",
                    },
                },
                "required": ["booking_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_bookings",
            "description": "Получить список бронирований текущего пользователя. Используй когда пользователь спрашивает про свои бронирования.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]


class ToolExecutor(Protocol):
    """Protocol for tool execution context."""

    async def list_available_houses(self) -> list[dict[str, Any]]:
        """Get list of available houses."""
        ...

    async def check_availability(
        self,
        house_id: int,
        check_in: str,
        check_out: str,
    ) -> dict[str, Any]:
        """Check house availability for dates."""
        ...

    async def create_booking(
        self,
        house_id: int,
        check_in: str,
        check_out: str,
        guests_count: int,
    ) -> dict[str, Any]:
        """Create a new booking."""
        ...

    async def cancel_booking(self, booking_id: int) -> dict[str, Any]:
        """Cancel a booking."""
        ...

    async def get_my_bookings(self) -> list[dict[str, Any]]:
        """Get user's bookings."""
        ...


class BookingToolExecutor:
    """Execute booking tools using existing services."""

    def __init__(
        self,
        booking_service: Any,
        house_service: Any,
        tariff_repo: Any,
        user_id: int,
        default_tariff_id: int = 1,
    ):
        """Initialize executor with services.

        Args:
            booking_service: BookingService instance
            house_service: HouseService instance
            tariff_repo: TariffRepository instance
            user_id: Current user ID for booking operations
            default_tariff_id: Default tariff ID for bookings
        """
        self._booking_service = booking_service
        self._house_service = house_service
        self._tariff_repo = tariff_repo
        self._user_id = user_id
        self._default_tariff_id = default_tariff_id

    async def list_available_houses(self) -> list[dict[str, Any]]:
        """Get list of available houses.

        Returns:
            List of houses with id, name, capacity, description
        """
        filters = HouseFilterParams(is_active=True, limit=100)
        houses, _ = await self._house_service.list_houses(filters)
        return [
            {
                "id": h.id,
                "name": h.name,
                "capacity": h.capacity,
                "description": h.description,
            }
            for h in houses
        ]

    async def check_availability(
        self,
        house_id: int,
        check_in: str,
        check_out: str,
    ) -> dict[str, Any]:
        """Check house availability for dates.

        Args:
            house_id: House ID to check
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)

        Returns:
            Dict with available flag and occupied dates if not available
        """
        try:
            check_in_date = date.fromisoformat(check_in)
            check_out_date = date.fromisoformat(check_out)
        except ValueError as e:
            return {"available": False, "error": f"Invalid date format: {e}"}

        try:
            calendar = await self._house_service.get_house_calendar(
                house_id,
                check_in_date,
                check_out_date,
            )
        except Exception as e:
            return {"available": False, "error": str(e)}

        # Check if any occupied dates overlap
        for occupied in calendar.occupied_dates:
            if check_in_date < occupied.check_out and check_out_date > occupied.check_in:
                return {
                    "available": False,
                    "conflict": {
                        "check_in": str(occupied.check_in),
                        "check_out": str(occupied.check_out),
                        "booking_id": occupied.booking_id,
                    },
                }

        return {"available": True}

    async def create_booking(
        self,
        house_id: int,
        check_in: str,
        check_out: str,
        guests_count: int,
    ) -> dict[str, Any]:
        """Create a new booking.

        Args:
            house_id: House ID to book
            check_in: Check-in date (YYYY-MM-DD)
            check_out: Check-out date (YYYY-MM-DD)
            guests_count: Number of guests

        Returns:
            Created booking info or error
        """
        try:
            check_in_date = date.fromisoformat(check_in)
            check_out_date = date.fromisoformat(check_out)
        except ValueError as e:
            return {"success": False, "error": f"Invalid date format: {e}"}

        # Verify tariff exists
        tariff = await self._tariff_repo.get(self._default_tariff_id)
        if not tariff:
            return {"success": False, "error": "Default tariff not found"}

        try:
            request = CreateBookingRequest(
                house_id=house_id,
                check_in=check_in_date,
                check_out=check_out_date,
                guests=[GuestInfo(tariff_id=self._default_tariff_id, count=guests_count)],
            )
            booking = await self._booking_service.create_booking(
                tenant_id=self._user_id,
                request=request,
            )
            return {
                "success": True,
                "booking": {
                    "id": booking.id,
                    "house_id": booking.house_id,
                    "check_in": str(booking.check_in),
                    "check_out": str(booking.check_out),
                    "guests_count": guests_count,
                    "status": booking.status.value,
                },
            }
        except Exception as e:
            logger.exception("Failed to create booking")
            return {"success": False, "error": str(e)}

    async def cancel_booking(self, booking_id: int) -> dict[str, Any]:
        """Cancel a booking.

        Args:
            booking_id: Booking ID to cancel

        Returns:
            Success status or error
        """
        try:
            booking = await self._booking_service.cancel_booking(
                booking_id=booking_id,
                tenant_id=self._user_id,
            )
            return {
                "success": True,
                "booking": {
                    "id": booking.id,
                    "status": booking.status.value,
                },
            }
        except Exception as e:
            logger.exception("Failed to cancel booking")
            return {"success": False, "error": str(e)}

    async def get_my_bookings(self) -> list[dict[str, Any]]:
        """Get user's bookings.

        Returns:
            List of user's bookings
        """
        filters = BookingFilterParams(
            user_id=self._user_id,
            limit=50,
            sort="-created_at",
        )
        bookings, _ = await self._booking_service.list_bookings(filters)
        return [
            {
                "id": b.id,
                "house_id": b.house_id,
                "check_in": str(b.check_in),
                "check_out": str(b.check_out),
                "status": b.status.value,
                "guests_count": sum(g.count for g in b.guests_planned),
            }
            for b in bookings
            if b.status != BookingStatus.CANCELLED
        ]


async def execute_tool_call(
    executor: ToolExecutor,
    tool_name: str,
    tool_args: dict[str, Any],
) -> str:
    """Execute a tool call and return result as JSON string.

    Args:
        executor: Tool executor instance
        tool_name: Name of the tool to execute
        tool_args: Tool arguments

    Returns:
        JSON string result
    """
    try:
        # Support alternative tool names
        normalized_name = tool_name
        if tool_name in ("list_bookings", "get_bookings", "my_bookings"):
            normalized_name = "get_my_bookings"
        
        if normalized_name == "list_available_houses":
            result = await executor.list_available_houses()
        elif normalized_name == "check_availability":
            result = await executor.check_availability(
                house_id=tool_args["house_id"],
                check_in=tool_args["check_in"],
                check_out=tool_args["check_out"],
            )
        elif normalized_name == "create_booking":
            result = await executor.create_booking(
                house_id=tool_args["house_id"],
                check_in=tool_args["check_in"],
                check_out=tool_args["check_out"],
                guests_count=tool_args["guests_count"],
            )
        elif normalized_name == "cancel_booking":
            result = await executor.cancel_booking(
                booking_id=tool_args["booking_id"],
            )
        elif normalized_name == "get_my_bookings":
            result = await executor.get_my_bookings()
        else:
            logger.warning("Unknown tool: %s (normalized: %s)", tool_name, normalized_name)
            result = {"error": f"Unknown tool: {tool_name}. Available tools: list_available_houses, check_availability, create_booking, cancel_booking, get_my_bookings"}
    except KeyError as e:
        logger.error("Missing required argument for tool %s: %s", tool_name, e)
        result = {"error": f"Missing required argument: {e}"}
    except Exception as e:
        logger.exception("Tool execution failed: %s", tool_name)
        result = {"error": f"Tool execution failed: {str(e)}"}

    return json.dumps(result, ensure_ascii=False)
