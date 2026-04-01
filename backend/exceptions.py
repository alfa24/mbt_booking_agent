"""Custom exceptions for the booking API.

This module defines domain-specific exceptions that are converted
to HTTP responses via exception handlers in main.py.
"""


class BookingException(Exception):
    """Base exception for booking domain."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class BookingNotFoundError(BookingException):
    """Raised when a booking is not found."""

    def __init__(self, booking_id: int):
        self.booking_id = booking_id
        super().__init__(f"Booking with id {booking_id} not found")


class DateConflictError(BookingException):
    """Raised when booking dates conflict with existing bookings."""

    def __init__(self, check_in: str, check_out: str):
        self.check_in = check_in
        self.check_out = check_out
        super().__init__(
            f"House is already booked for the requested period "
            f"({check_in} to {check_out})"
        )


class BookingPermissionError(BookingException):
    """Raised when user tries to access/modify another user's booking."""

    def __init__(self, action: str = "access"):
        self.action = action
        super().__init__(f"You can only {action} your own bookings")


class InvalidBookingStatusError(BookingException):
    """Raised when operation cannot be performed due to booking status."""

    def __init__(self, status: str, operation: str):
        self.status = status
        self.operation = operation
        super().__init__(f"Cannot {operation} booking with status: {status}")


class BookingAlreadyCancelledError(BookingException):
    """Raised when trying to cancel an already cancelled booking."""

    def __init__(self):
        super().__init__("Booking is already cancelled")


class HouseNotFoundError(BookingException):
    """Raised when a house is not found."""

    def __init__(self, house_id: int):
        self.house_id = house_id
        super().__init__(f"House with id {house_id} not found")


class UserNotFoundError(BookingException):
    """Raised when a user is not found."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User with id {user_id} not found")


class TariffNotFoundError(BookingException):
    """Raised when a tariff is not found."""

    def __init__(self, tariff_id: int):
        self.tariff_id = tariff_id
        super().__init__(f"Tariff with id {tariff_id} not found")
