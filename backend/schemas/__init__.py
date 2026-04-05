"""Backend API schemas package."""

from backend.schemas.booking import (
    BookingFilterParams,
    BookingResponse,
    BookingStatus,
    CreateBookingRequest,
    GuestInfo,
    UpdateBookingRequest,
)
from backend.schemas.chat import (
    ChatResponse,
    ChatMessageResponse,
    ChatMessagesListResponse,
    CreateChatRequest,
    SendMessageRequest,
)
from backend.schemas.common import ErrorResponse, PaginatedResponse, ValidationErrorDetail
from backend.schemas.consumable_note import (
    ConsumableNoteResponse,
    CreateConsumableNoteRequest,
    UpdateConsumableNoteRequest,
)
from backend.schemas.dashboard import (
    BookingsByMonth,
    HouseStatsResponse,
    LeaderboardResponse,
    MonthlyRevenue,
    OwnerDashboardResponse,
    RevenueByHouse,
)
from backend.schemas.house import (
    CreateHouseRequest,
    HouseCalendarResponse,
    HouseFilterParams,
    HouseResponse,
    OccupiedDateRange,
    UpdateHouseRequest,
)
from backend.schemas.tariff import (
    CreateTariffRequest,
    TariffResponse,
    UpdateTariffRequest,
)
from backend.schemas.user import (
    CreateUserRequest,
    UpdateUserRequest,
    UserFilterParams,
    UserResponse,
    UserRole,
)

__all__ = [
    # Common
    "ErrorResponse",
    "PaginatedResponse",
    "ValidationErrorDetail",
    # User
    "UserResponse",
    "UserRole",
    "CreateUserRequest",
    "UpdateUserRequest",
    "UserFilterParams",
    # House
    "HouseResponse",
    "CreateHouseRequest",
    "UpdateHouseRequest",
    "HouseCalendarResponse",
    "OccupiedDateRange",
    "HouseFilterParams",
    # Booking
    "BookingResponse",
    "BookingStatus",
    "GuestInfo",
    "CreateBookingRequest",
    "UpdateBookingRequest",
    "BookingFilterParams",
    # Tariff
    "TariffResponse",
    "CreateTariffRequest",
    "UpdateTariffRequest",
    # Chat
    "ChatResponse",
    "ChatMessageResponse",
    "ChatMessagesListResponse",
    "CreateChatRequest",
    "SendMessageRequest",
    # ConsumableNote
    "ConsumableNoteResponse",
    "CreateConsumableNoteRequest",
    "UpdateConsumableNoteRequest",
    # Dashboard
    "OwnerDashboardResponse",
    "MonthlyRevenue",
    "LeaderboardResponse",
    "RevenueByHouse",
    "BookingsByMonth",
    "HouseStatsResponse",
]
