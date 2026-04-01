"""Backend API schemas package."""

from backend.schemas.booking import (
    BookingFilterParams,
    BookingResponse,
    BookingStatus,
    CreateBookingRequest,
    GuestInfo,
    UpdateBookingRequest,
)
from backend.schemas.common import ErrorResponse, PaginatedResponse, ValidationErrorDetail
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
]
