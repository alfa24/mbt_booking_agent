"""In-memory booking repository for MVP."""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from backend.schemas.booking import BookingResponse, BookingStatus


class BookingRepository:
    """In-memory repository for bookings.

    Uses dict for storage with auto-increment ID.
    To be replaced with SQLAlchemy repository in task-06.
    """

    def __init__(self):
        """Initialize repository with empty storage."""
        self._storage: Dict[int, BookingResponse] = {}
        self._counter: int = 0

    def _get_next_id(self) -> int:
        """Generate next booking ID."""
        self._counter += 1
        return self._counter

    def create(
        self,
        house_id: int,
        tenant_id: int,
        check_in: datetime,
        check_out: datetime,
        guests_planned: List[dict],
        total_amount: Optional[int] = None,
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
        booking_id = self._get_next_id()
        booking = BookingResponse(
            id=booking_id,
            house_id=house_id,
            tenant_id=tenant_id,
            check_in=check_in,
            check_out=check_out,
            guests_planned=guests_planned,
            guests_actual=None,
            total_amount=total_amount,
            status=BookingStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )
        self._storage[booking_id] = booking
        return booking

    def get(self, booking_id: int) -> Optional[BookingResponse]:
        """Get booking by ID.

        Args:
            booking_id: Booking identifier

        Returns:
            Booking if found, None otherwise
        """
        return self._storage.get(booking_id)

    def get_all(
        self,
        user_id: Optional[int] = None,
        house_id: Optional[int] = None,
        status: Optional[BookingStatus] = None,
        limit: int = 20,
        offset: int = 0,
        sort: Optional[str] = None,
    ) -> tuple[List[BookingResponse], int]:
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
        bookings = list(self._storage.values())

        # Apply filters
        if user_id is not None:
            bookings = [b for b in bookings if b.tenant_id == user_id]
        if house_id is not None:
            bookings = [b for b in bookings if b.house_id == house_id]
        if status is not None:
            bookings = [b for b in bookings if b.status == status]

        # Apply sorting
        if sort:
            reverse = sort.startswith("-")
            sort_field = sort[1:] if reverse else sort
            if sort_field in ("check_in", "check_out", "created_at", "id"):
                bookings = sorted(
                    bookings,
                    key=lambda b: getattr(b, sort_field),
                    reverse=reverse,
                )

        total = len(bookings)

        # Apply pagination
        bookings = bookings[offset : offset + limit]

        return bookings, total

    def update(
        self,
        booking_id: int,
        check_in: Optional[datetime] = None,
        check_out: Optional[datetime] = None,
        guests_planned: Optional[List[dict]] = None,
        guests_actual: Optional[List[dict]] = None,
        total_amount: Optional[int] = None,
        status: Optional[BookingStatus] = None,
    ) -> Optional[BookingResponse]:
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
        booking = self._storage.get(booking_id)
        if not booking:
            return None

        # Create updated booking with new values
        updated_data = booking.model_dump()
        if check_in is not None:
            updated_data["check_in"] = check_in
        if check_out is not None:
            updated_data["check_out"] = check_out
        if guests_planned is not None:
            updated_data["guests_planned"] = guests_planned
        if guests_actual is not None:
            updated_data["guests_actual"] = guests_actual
        if total_amount is not None:
            updated_data["total_amount"] = total_amount
        if status is not None:
            updated_data["status"] = status

        updated_booking = BookingResponse(**updated_data)
        self._storage[booking_id] = updated_booking
        return updated_booking

    def delete(self, booking_id: int) -> bool:
        """Delete booking by ID.

        Args:
            booking_id: Booking identifier

        Returns:
            True if deleted, False if not found
        """
        if booking_id in self._storage:
            del self._storage[booking_id]
            return True
        return False

    def get_bookings_for_house(
        self,
        house_id: int,
        exclude_booking_id: Optional[int] = None,
    ) -> List[BookingResponse]:
        """Get all bookings for a specific house.

        Args:
            house_id: House identifier
            exclude_booking_id: Optional booking ID to exclude (for updates)

        Returns:
            List of bookings for the house
        """
        bookings = [
            b for b in self._storage.values()
            if b.house_id == house_id and b.status != BookingStatus.CANCELLED
        ]
        if exclude_booking_id is not None:
            bookings = [b for b in bookings if b.id != exclude_booking_id]
        return bookings

    def clear(self) -> None:
        """Clear all bookings (for testing)."""
        self._storage.clear()
        self._counter = 0
