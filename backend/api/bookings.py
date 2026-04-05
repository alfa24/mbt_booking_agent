"""Booking API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from backend.schemas.booking import (
    BookingFilterParams,
    BookingResponse,
    CreateBookingRequest,
    UpdateBookingRequest,
)
from backend.schemas.common import ErrorResponse, PaginatedResponse
from backend.services.booking import BookingService

bookings_router = APIRouter(prefix="/bookings", tags=["bookings"])


@bookings_router.get(
    "",
    response_model=PaginatedResponse[BookingResponse],
    summary="List bookings",
    description="Get list of bookings with optional filtering and pagination.",
    responses={
        200: {"description": "List of bookings returned successfully"},
    },
)
async def list_bookings(
    filters: Annotated[BookingFilterParams, Depends()],
    service: Annotated[BookingService, Depends(BookingService)],
) -> PaginatedResponse[BookingResponse]:
    """List all bookings with filtering.

    Supports filtering by user_id, house_id, status, and date ranges.
    Results are paginated using limit/offset.

    Args:
        filters: Query parameters for filtering and pagination
        service: Booking service instance

    Returns:
        Paginated list of bookings
    """
    bookings, total = await service.list_bookings(filters)
    return PaginatedResponse(
        items=bookings,
        total=total,
        limit=filters.limit,
        offset=filters.offset,
    )


@bookings_router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Get booking by ID",
    description="Retrieve detailed information about a specific booking.",
    responses={
        200: {"description": "Booking found and returned"},
        404: {
            "description": "Booking not found",
            "model": ErrorResponse,
        },
    },
)
async def get_booking(
    booking_id: int,
    service: Annotated[BookingService, Depends(BookingService)],
) -> BookingResponse:
    """Get a single booking by its ID.

    Args:
        booking_id: Unique booking identifier
        service: Booking service instance

    Returns:
        Booking details

    Raises:
        HTTPException: 404 if booking not found
    """
    return await service.get_booking(booking_id)


@bookings_router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create booking",
    description="Create a new booking request for a house.",
    responses={
        201: {"description": "Booking created successfully"},
        400: {
            "description": "Validation error or date conflict",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def create_booking(
    request: CreateBookingRequest,
    service: Annotated[BookingService, Depends(BookingService)],
    tenant_id: int = 1,
) -> BookingResponse:
    """Create a new booking.

    Validates dates (check_in must be before check_out) and checks
    for conflicts with existing bookings for the same house.

    Args:
        request: Booking creation data
        service: Booking service instance
        tenant_id: ID of the tenant making the booking (query param, default=1)

    Returns:
        Created booking with generated ID

    Raises:
        HTTPException: 400 if dates conflict, 422 if validation fails
    """
    return await service.create_booking(tenant_id, request)


@bookings_router.patch(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Update booking",
    description="Update booking details (dates, guests, status).",
    responses={
        200: {"description": "Booking updated successfully"},
        400: {
            "description": "Validation error or invalid status",
            "model": ErrorResponse,
        },
        403: {
            "description": "Forbidden - can only update own bookings",
            "model": ErrorResponse,
        },
        404: {
            "description": "Booking not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def update_booking(
    booking_id: int,
    request: UpdateBookingRequest,
    service: Annotated[BookingService, Depends(BookingService)],
    tenant_id: int = 1,
) -> BookingResponse:
    """Update an existing booking.

    Only the booking owner can update. Cannot update cancelled or completed bookings.
    Validates dates and checks for conflicts if dates are changed.

    Args:
        booking_id: Booking identifier
        request: Fields to update
        service: Booking service instance
        tenant_id: ID of the tenant (for authorization check, query param, default=1)

    Returns:
        Updated booking

    Raises:
        HTTPException: 404 if not found, 403 if not owner, 400 if invalid
    """
    return await service.update_booking(booking_id, tenant_id, request)


@bookings_router.delete(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Cancel booking",
    description="Cancel a booking (soft delete - sets status to cancelled).",
    responses={
        200: {"description": "Booking cancelled successfully"},
        400: {
            "description": "Booking already cancelled or completed",
            "model": ErrorResponse,
        },
        403: {
            "description": "Forbidden - can only cancel own bookings",
            "model": ErrorResponse,
        },
        404: {
            "description": "Booking not found",
            "model": ErrorResponse,
        },
    },
)
async def cancel_booking(
    booking_id: int,
    service: Annotated[BookingService, Depends(BookingService)],
    tenant_id: int = 1,
) -> BookingResponse:
    """Cancel a booking.

    Sets booking status to 'cancelled'. Only the booking owner can cancel.
    Cannot cancel already cancelled or completed bookings.

    Args:
        booking_id: Booking identifier
        service: Booking service instance
        tenant_id: ID of the tenant (for authorization check, query param, default=1)

    Returns:
        Cancelled booking

    Raises:
        HTTPException: 404 if not found, 403 if not owner, 400 if invalid status
    """
    return await service.cancel_booking(booking_id, tenant_id)
