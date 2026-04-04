"""SQLAlchemy booking repository."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.booking import Booking, BookingStatus
from backend.schemas.booking import BookingResponse


class BookingRepository:
    """SQLAlchemy repository for bookings."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def create(
        self,
        house_id: int,
        tenant_id: int,
        check_in: date,
        check_out: date,
        guests_planned: list[dict],
        total_amount: int | None = None,
    ) -> BookingResponse:
        """Create a new booking.

        Args:
            house_id: ID of the booked house
            tenant_id: ID of the tenant who made the booking
            check_in: Check-in date
            check_out: Check-out date
            guests_planned: Planned guest composition
            total_amount: Calculated total amount (optional)

        Returns:
            Created booking response
        """
        booking = Booking(
            house_id=house_id,
            tenant_id=tenant_id,
            check_in=check_in,
            check_out=check_out,
            guests_planned=guests_planned,
            total_amount=total_amount,
            status=BookingStatus.PENDING,
        )
        self._session.add(booking)
        await self._session.flush()
        await self._session.refresh(booking)
        return BookingResponse.model_validate(booking)

    async def get(self, booking_id: int) -> BookingResponse | None:
        """Get booking by ID.

        Args:
            booking_id: Booking identifier

        Returns:
            Booking if found, None otherwise
        """
        result = await self._session.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()
        return BookingResponse.model_validate(booking) if booking else None

    async def get_all(
        self,
        user_id: int | None = None,
        house_id: int | None = None,
        status: BookingStatus | None = None,
        limit: int = 20,
        offset: int = 0,
        sort: str | None = None,
    ) -> tuple[list[BookingResponse], int]:
        """Get all bookings with optional filtering.

        Args:
            user_id: Filter by tenant ID
            house_id: Filter by house ID
            status: Filter by booking status
            limit: Number of results to return
            offset: Number of results to skip
            sort: Sort field (prefix with - for descending)

        Returns:
            Tuple of (filtered bookings list, total count)
        """
        query = select(Booking)

        # Apply filters
        if user_id is not None:
            query = query.where(Booking.tenant_id == user_id)
        if house_id is not None:
            query = query.where(Booking.house_id == house_id)
        if status is not None:
            query = query.where(Booking.status == status)

        # Get total count
        count_result = await self._session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Apply sorting
        if sort:
            reverse = sort.startswith("-")
            sort_field = sort[1:] if reverse else sort
            if hasattr(Booking, sort_field):
                order = (
                    getattr(Booking, sort_field).desc()
                    if reverse
                    else getattr(Booking, sort_field)
                )
                query = query.order_by(order)

        # Apply pagination
        query = query.offset(offset).limit(limit)

        result = await self._session.execute(query)
        bookings = result.scalars().all()
        return [BookingResponse.model_validate(b) for b in bookings], total

    async def update(
        self,
        booking_id: int,
        check_in: date | None = None,
        check_out: date | None = None,
        guests_planned: list[dict] | None = None,
        guests_actual: list[dict] | None = None,
        total_amount: int | None = None,
        status: BookingStatus | None = None,
    ) -> BookingResponse | None:
        """Update booking fields.

        Args:
            booking_id: Booking identifier
            check_in: New check-in date (optional)
            check_out: New check-out date (optional)
            guests_planned: New guest composition (optional)
            guests_actual: Actual guest composition (optional)
            total_amount: New total amount (optional)
            status: New status (optional)

        Returns:
            Updated booking if found, None otherwise
        """
        result = await self._session.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()
        if not booking:
            return None

        if check_in is not None:
            booking.check_in = check_in
        if check_out is not None:
            booking.check_out = check_out
        if guests_planned is not None:
            booking.guests_planned = guests_planned
        if guests_actual is not None:
            booking.guests_actual = guests_actual
        if total_amount is not None:
            booking.total_amount = total_amount
        if status is not None:
            booking.status = status

        await self._session.flush()
        await self._session.refresh(booking)
        return BookingResponse.model_validate(booking)

    async def delete(self, booking_id: int) -> bool:
        """Delete booking by ID.

        Args:
            booking_id: Booking identifier

        Returns:
            True if deleted, False if not found
        """
        result = await self._session.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()
        if not booking:
            return False

        await self._session.delete(booking)
        return True

    async def get_bookings_for_house(
        self,
        house_id: int,
        exclude_booking_id: int | None = None,
    ) -> list[BookingResponse]:
        """Get all bookings for a specific house.

        Args:
            house_id: House identifier
            exclude_booking_id: Optional booking ID to exclude (for updates)

        Returns:
            List of bookings for the house
        """
        query = select(Booking).where(
            Booking.house_id == house_id,
            Booking.status != BookingStatus.CANCELLED,
        )

        if exclude_booking_id is not None:
            query = query.where(Booking.id != exclude_booking_id)

        result = await self._session.execute(query)
        bookings = result.scalars().all()
        return [BookingResponse.model_validate(b) for b in bookings]
