"""In-memory tariff repository for MVP."""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from backend.schemas.tariff import TariffResponse


class TariffRepository:
    """In-memory repository for tariffs.

    Uses dict for storage with auto-increment ID.
    To be replaced with SQLAlchemy repository in task-06.
    """

    def __init__(self):
        """Initialize repository with empty storage."""
        self._storage: Dict[int, TariffResponse] = {}
        self._counter: int = 0

    def _get_next_id(self) -> int:
        """Generate next tariff ID."""
        self._counter += 1
        return self._counter

    def create(
        self,
        name: str,
        amount: int,
    ) -> TariffResponse:
        """Create a new tariff.

        Args:
            name: Tariff name
            amount: Price per night in rubles (0 for free)

        Returns:
            Created tariff response
        """
        tariff_id = self._get_next_id()
        tariff = TariffResponse(
            id=tariff_id,
            name=name,
            amount=amount,
            created_at=datetime.now(timezone.utc),
        )
        self._storage[tariff_id] = tariff
        return tariff

    def get(self, tariff_id: int) -> Optional[TariffResponse]:
        """Get tariff by ID.

        Args:
            tariff_id: Tariff identifier

        Returns:
            Tariff if found, None otherwise
        """
        return self._storage.get(tariff_id)

    def get_all(
        self,
        limit: int = 20,
        offset: int = 0,
        sort: Optional[str] = None,
    ) -> tuple[List[TariffResponse], int]:
        """Get all tariffs with optional sorting and pagination.

        Args:
            limit: Number of results to return
            offset: Number of results to skip
            sort: Sort field (prefix with - for descending)

        Returns:
            Tuple of (tariffs list, total count)
        """
        tariffs = list(self._storage.values())

        # Apply sorting
        if sort:
            reverse = sort.startswith("-")
            sort_field = sort[1:] if reverse else sort
            if sort_field in ("name", "amount", "created_at", "id"):
                tariffs = sorted(
                    tariffs,
                    key=lambda t: getattr(t, sort_field),
                    reverse=reverse,
                )

        total = len(tariffs)

        # Apply pagination
        tariffs = tariffs[offset : offset + limit]

        return tariffs, total

    def update(
        self,
        tariff_id: int,
        name: Optional[str] = None,
        amount: Optional[int] = None,
    ) -> Optional[TariffResponse]:
        """Update tariff fields.

        Args:
            tariff_id: Tariff identifier
            name: New name (optional)
            amount: New amount (optional)

        Returns:
            Updated tariff if found, None otherwise
        """
        tariff = self._storage.get(tariff_id)
        if not tariff:
            return None

        # Create updated tariff with new values
        updated_data = tariff.model_dump()
        if name is not None:
            updated_data["name"] = name
        if amount is not None:
            updated_data["amount"] = amount

        updated_tariff = TariffResponse(**updated_data)
        self._storage[tariff_id] = updated_tariff
        return updated_tariff

    def delete(self, tariff_id: int) -> bool:
        """Delete tariff by ID.

        Args:
            tariff_id: Tariff identifier

        Returns:
            True if deleted, False if not found
        """
        if tariff_id in self._storage:
            del self._storage[tariff_id]
            return True
        return False

    def clear(self) -> None:
        """Clear all tariffs (for testing)."""
        self._storage.clear()
        self._counter = 0
