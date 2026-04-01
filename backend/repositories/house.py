"""In-memory house repository for MVP."""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from backend.schemas.house import HouseResponse


class HouseRepository:
    """In-memory repository for houses.

    Uses dict for storage with auto-increment ID.
    To be replaced with SQLAlchemy repository in task-06.
    """

    def __init__(self):
        """Initialize repository with empty storage."""
        self._storage: Dict[int, HouseResponse] = {}
        self._counter: int = 0

    def _get_next_id(self) -> int:
        """Generate next house ID."""
        self._counter += 1
        return self._counter

    def create(
        self,
        name: str,
        description: Optional[str],
        capacity: int,
        is_active: bool,
        owner_id: int,
    ) -> HouseResponse:
        """Create a new house.

        Args:
            name: House name
            description: House description
            capacity: Maximum number of guests
            is_active: Whether the house is available for booking
            owner_id: ID of the house owner

        Returns:
            Created house response
        """
        house_id = self._get_next_id()
        house = HouseResponse(
            id=house_id,
            name=name,
            description=description,
            capacity=capacity,
            is_active=is_active,
            owner_id=owner_id,
            created_at=datetime.now(timezone.utc),
        )
        self._storage[house_id] = house
        return house

    def get(self, house_id: int) -> Optional[HouseResponse]:
        """Get house by ID.

        Args:
            house_id: House identifier

        Returns:
            House if found, None otherwise
        """
        return self._storage.get(house_id)

    def get_all(
        self,
        owner_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        capacity_min: Optional[int] = None,
        capacity_max: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
        sort: Optional[str] = None,
    ) -> tuple[List[HouseResponse], int]:
        """Get all houses with optional filtering.

        Args:
            owner_id: Filter by owner ID
            is_active: Filter by active status
            capacity_min: Filter by minimum capacity
            capacity_max: Filter by maximum capacity
            limit: Number of results to return
            offset: Number of results to skip
            sort: Sort field (prefix with - for descending)

        Returns:
            Tuple of (filtered houses list, total count)
        """
        houses = list(self._storage.values())

        # Apply filters
        if owner_id is not None:
            houses = [h for h in houses if h.owner_id == owner_id]
        if is_active is not None:
            houses = [h for h in houses if h.is_active == is_active]
        if capacity_min is not None:
            houses = [h for h in houses if h.capacity >= capacity_min]
        if capacity_max is not None:
            houses = [h for h in houses if h.capacity <= capacity_max]

        # Apply sorting
        if sort:
            reverse = sort.startswith("-")
            sort_field = sort[1:] if reverse else sort
            if sort_field in ("name", "capacity", "created_at", "id"):
                houses = sorted(
                    houses,
                    key=lambda h: getattr(h, sort_field),
                    reverse=reverse,
                )

        total = len(houses)

        # Apply pagination
        houses = houses[offset : offset + limit]

        return houses, total

    def update(
        self,
        house_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        capacity: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[HouseResponse]:
        """Update house fields.

        Args:
            house_id: House identifier
            name: New name (optional)
            description: New description (optional)
            capacity: New capacity (optional)
            is_active: New active status (optional)

        Returns:
            Updated house if found, None otherwise
        """
        house = self._storage.get(house_id)
        if not house:
            return None

        # Create updated house with new values
        updated_data = house.model_dump()
        if name is not None:
            updated_data["name"] = name
        if description is not None:
            updated_data["description"] = description
        if capacity is not None:
            updated_data["capacity"] = capacity
        if is_active is not None:
            updated_data["is_active"] = is_active

        updated_house = HouseResponse(**updated_data)
        self._storage[house_id] = updated_house
        return updated_house

    def delete(self, house_id: int) -> bool:
        """Delete house by ID.

        Args:
            house_id: House identifier

        Returns:
            True if deleted, False if not found
        """
        if house_id in self._storage:
            del self._storage[house_id]
            return True
        return False

    def clear(self) -> None:
        """Clear all houses (for testing)."""
        self._storage.clear()
        self._counter = 0
