"""Booking service with business logic."""

from datetime import date
from typing import List, Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.exceptions import (
    BookingAlreadyCancelledError,
    BookingNotFoundError,
    BookingPermissionError,
    DateConflictError,
    InvalidBookingStatusError,
)
from backend.repositories.booking import BookingRepository
from backend.repositories.tariff import TariffRepository
from backend.schemas.booking import (
    BookingFilterParams,
    BookingResponse,
    BookingStatus,
    CreateBookingRequest,
    GuestInfo,
    UpdateBookingRequest,
)


async def get_booking_repository(
    db: AsyncSession = Depends(get_db),
) -> BookingRepository:
    """Dependency provider for booking repository.

    Args:
        db: Database session from dependency injection

    Returns:
        BookingRepository instance with database session
    """
    return BookingRepository(db)


async def get_tariff_repository(
    db: AsyncSession = Depends(get_db),
) -> TariffRepository:
    """Dependency provider for tariff repository.

    Args:
        db: Database session from dependency injection

    Returns:
        TariffRepository instance with database session
    """
    return TariffRepository(db)


class BookingService:
    """Service layer for booking operations.

    Handles business logic: validation, date conflict checking,
    amount calculation, and status management.
    """

    def __init__(
        self,
        repository: BookingRepository = Depends(get_booking_repository),
        tariff_repository: TariffRepository = Depends(get_tariff_repository),
    ):
        """Initialize service with repositories.

        Args:
            repository: Booking repository instance
            tariff_repository: Tariff repository instance
        """
        self._repo = repository
        self._tariff_repo = tariff_repository

    async def _check_date_conflicts(
        self,
        house_id: int,
        check_in: date,
        check_out: date,
        exclude_booking_id: Optional[int] = None,
    ) -> None:
        """Check if booking dates conflict with existing bookings.

        Args:
            house_id: House being booked
            check_in: Requested check-in date
            check_out: Requested check-out date
            exclude_booking_id: Optional booking ID to exclude (for updates)

        Raises:
            HTTPException: If dates conflict with existing booking
        """
        existing_bookings = await self._repo.get_bookings_for_house(
            house_id, exclude_booking_id
        )

        for booking in existing_bookings:
            # Check for overlap: (StartA < EndB) and (EndA > StartB)
            if check_in < booking.check_out and check_out > booking.check_in:
                raise DateConflictError(
                    check_in=str(check_in),
                    check_out=str(check_out),
                )

    async def _calculate_amount(self, guests: List[GuestInfo]) -> int:
        """Calculate total amount for booking.

        Fetches actual tariff amounts from database.

        Args:
            guests: List of guest info with tariff and count

        Returns:
            Total amount in rubles
        """
        total = 0
        for guest in guests:
            tariff = await self._tariff_repo.get(guest.tariff_id)
            rate = tariff.amount if tariff else 0
            total += rate * guest.count

        return total

    async def create_booking(
        self,
        tenant_id: int,
        request: CreateBookingRequest,
    ) -> BookingResponse:
        """Create a new booking with validation.

        Args:
            tenant_id: ID of the tenant making the booking
            request: Booking creation request

        Returns:
            Created booking

        Raises:
            HTTPException: If validation fails or dates conflict
        """
        # Check date conflicts
        await self._check_date_conflicts(
            request.house_id,
            request.check_in,
            request.check_out,
        )

        # Calculate amount
        total_amount = await self._calculate_amount(request.guests)

        # Convert GuestInfo to dict for storage
        guests_data = [
            {"tariff_id": g.tariff_id, "count": g.count}
            for g in request.guests
        ]

        # Create booking
        booking = await self._repo.create(
            house_id=request.house_id,
            tenant_id=tenant_id,
            check_in=request.check_in,
            check_out=request.check_out,
            guests_planned=guests_data,
            total_amount=total_amount,
        )

        return booking

    async def get_booking(self, booking_id: int) -> BookingResponse:
        """Get booking by ID.

        Args:
            booking_id: Booking identifier

        Returns:
            Booking data

        Raises:
            HTTPException: If booking not found
        """
        booking = await self._repo.get(booking_id)
        if not booking:
            raise BookingNotFoundError(booking_id)
        return booking

    async def list_bookings(
        self,
        filters: BookingFilterParams,
    ) -> tuple[List[BookingResponse], int]:
        """List bookings with filtering and pagination.

        Args:
            filters: Filter and pagination parameters

        Returns:
            Tuple of (bookings list, total count)
        """
        return await self._repo.get_all(
            user_id=filters.user_id,
            house_id=filters.house_id,
            status=filters.status,
            limit=filters.limit,
            offset=filters.offset,
            sort=filters.sort,
        )

    async def update_booking(
        self,
        booking_id: int,
        tenant_id: int,
        request: UpdateBookingRequest,
    ) -> BookingResponse:
        """Update booking with validation.

        Args:
            booking_id: Booking identifier
            tenant_id: ID of the tenant (for authorization check)
            request: Update request with fields to change

        Returns:
            Updated booking

        Raises:
            HTTPException: If booking not found, unauthorized, or validation fails
        """
        # Get existing booking
        existing = await self._repo.get(booking_id)
        if not existing:
            raise BookingNotFoundError(booking_id)

        # Authorization check
        if existing.tenant_id != tenant_id:
            raise BookingPermissionError(action="update")

        # Check if booking can be updated (only pending or confirmed)
        if existing.status not in (BookingStatus.PENDING, BookingStatus.CONFIRMED):
            raise InvalidBookingStatusError(
                status=existing.status.value,
                operation="update",
            )

        # Determine new dates
        new_check_in = request.check_in or existing.check_in
        new_check_out = request.check_out or existing.check_out

        # Check date conflicts if dates changed
        if request.check_in or request.check_out:
            await self._check_date_conflicts(
                existing.house_id,
                new_check_in,
                new_check_out,
                exclude_booking_id=booking_id,
            )

        # Calculate new amount if guests changed
        new_amount = existing.total_amount
        if request.guests:
            new_amount = await self._calculate_amount(request.guests)

        # Convert guests to dict if provided
        guests_data = None
        if request.guests:
            guests_data = [
                {"tariff_id": g.tariff_id, "count": g.count}
                for g in request.guests
            ]

        # Update booking
        updated = await self._repo.update(
            booking_id=booking_id,
            check_in=request.check_in,
            check_out=request.check_out,
            guests_planned=guests_data,
            total_amount=new_amount,
            status=request.status,
        )

        return updated

    async def cancel_booking(self, booking_id: int, tenant_id: int) -> BookingResponse:
        """Cancel a booking (soft delete).

        Args:
            booking_id: Booking identifier
            tenant_id: ID of the tenant (for authorization check)

        Returns:
            Cancelled booking

        Raises:
            HTTPException: If booking not found or unauthorized
        """
        # Get existing booking
        existing = await self._repo.get(booking_id)
        if not existing:
            raise BookingNotFoundError(booking_id)

        # Authorization check
        if existing.tenant_id != tenant_id:
            raise BookingPermissionError(action="cancel")

        # Check if booking can be cancelled
        if existing.status == BookingStatus.CANCELLED:
            raise BookingAlreadyCancelledError()

        if existing.status == BookingStatus.COMPLETED:
            raise InvalidBookingStatusError(
                status=existing.status.value,
                operation="cancel",
            )

        # Update status to cancelled
        updated = await self._repo.update(
            booking_id=booking_id,
            status=BookingStatus.CANCELLED,
        )

        return updated
