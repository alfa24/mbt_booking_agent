"""House service with business logic."""

from datetime import date
from typing import List, Optional

from fastapi import Depends

from backend.exceptions import HouseNotFoundError
from backend.repositories.booking import BookingRepository
from backend.repositories.house import HouseRepository
from backend.schemas.house import (
    CreateHouseRequest,
    HouseCalendarResponse,
    HouseFilterParams,
    HouseResponse,
    OccupiedDateRange,
    UpdateHouseRequest,
)
from backend.services.booking import get_booking_repository


def get_house_repository() -> HouseRepository:
    """Dependency provider for house repository.

    Returns singleton instance of in-memory repository.
    To be replaced with database session in task-06.
    """
    if not hasattr(get_house_repository, "_instance"):
        get_house_repository._instance = HouseRepository()
    return get_house_repository._instance


class HouseService:
    """Service layer for house operations.

    Handles business logic: CRUD operations and calendar availability.
    """

    def __init__(
        self,
        repository: HouseRepository = Depends(get_house_repository),
        booking_repository: BookingRepository = Depends(get_booking_repository),
    ):
        """Initialize service with repositories.

        Args:
            repository: House repository instance
            booking_repository: Booking repository instance for calendar
        """
        self._repo = repository
        self._booking_repo = booking_repository

    def create_house(
        self,
        owner_id: int,
        request: CreateHouseRequest,
    ) -> HouseResponse:
        """Create a new house.

        Args:
            owner_id: ID of the house owner
            request: House creation request

        Returns:
            Created house
        """
        return self._repo.create(
            name=request.name,
            description=request.description,
            capacity=request.capacity,
            is_active=request.is_active,
            owner_id=owner_id,
        )

    def get_house(self, house_id: int) -> HouseResponse:
        """Get house by ID.

        Args:
            house_id: House identifier

        Returns:
            House data

        Raises:
            HouseNotFoundError: If house not found
        """
        house = self._repo.get(house_id)
        if not house:
            raise HouseNotFoundError(house_id)
        return house

    def list_houses(
        self,
        filters: HouseFilterParams,
    ) -> tuple[List[HouseResponse], int]:
        """List houses with filtering and pagination.

        Args:
            filters: Filter and pagination parameters

        Returns:
            Tuple of (houses list, total count)
        """
        return self._repo.get_all(
            owner_id=filters.owner_id,
            is_active=filters.is_active,
            capacity_min=filters.capacity_min,
            capacity_max=filters.capacity_max,
            limit=filters.limit,
            offset=filters.offset,
            sort=filters.sort,
        )

    def update_house(
        self,
        house_id: int,
        request: UpdateHouseRequest,
    ) -> HouseResponse:
        """Update house information.

        Args:
            house_id: House identifier
            request: Update request with fields to change

        Returns:
            Updated house

        Raises:
            HouseNotFoundError: If house not found
        """
        existing = self._repo.get(house_id)
        if not existing:
            raise HouseNotFoundError(house_id)

        updated = self._repo.update(
            house_id=house_id,
            name=request.name,
            description=request.description,
            capacity=request.capacity,
            is_active=request.is_active,
        )
        return updated

    def replace_house(
        self,
        house_id: int,
        request: CreateHouseRequest,
    ) -> HouseResponse:
        """Replace house information (full update).

        Args:
            house_id: House identifier
            request: Full house data

        Returns:
            Updated house

        Raises:
            HouseNotFoundError: If house not found
        """
        existing = self._repo.get(house_id)
        if not existing:
            raise HouseNotFoundError(house_id)

        updated = self._repo.update(
            house_id=house_id,
            name=request.name,
            description=request.description,
            capacity=request.capacity,
            is_active=request.is_active,
        )
        return updated

    def delete_house(self, house_id: int) -> None:
        """Delete a house.

        Args:
            house_id: House identifier

        Raises:
            HouseNotFoundError: If house not found
        """
        existing = self._repo.get(house_id)
        if not existing:
            raise HouseNotFoundError(house_id)

        self._repo.delete(house_id)

    def get_house_calendar(
        self,
        house_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> HouseCalendarResponse:
        """Get house availability calendar.

        Args:
            house_id: House identifier
            date_from: Start of period (optional)
            date_to: End of period (optional)

        Returns:
            Calendar with occupied date ranges

        Raises:
            HouseNotFoundError: If house not found
        """
        house = self._repo.get(house_id)
        if not house:
            raise HouseNotFoundError(house_id)

        # Get all bookings for this house (excluding cancelled)
        bookings = self._booking_repo.get_bookings_for_house(house_id)

        occupied_dates: List[OccupiedDateRange] = []
        for booking in bookings:
            # Filter by date range if provided
            if date_from and booking.check_out < date_from:
                continue
            if date_to and booking.check_in > date_to:
                continue

            occupied_dates.append(
                OccupiedDateRange(
                    check_in=booking.check_in,
                    check_out=booking.check_out,
                    booking_id=booking.id,
                )
            )

        return HouseCalendarResponse(
            house_id=house_id,
            occupied_dates=occupied_dates,
        )
