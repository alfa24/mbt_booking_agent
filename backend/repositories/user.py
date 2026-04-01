"""In-memory user repository for MVP."""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from backend.schemas.user import UserResponse, UserRole


class UserRepository:
    """In-memory repository for users.

    Uses dict for storage with auto-increment ID.
    To be replaced with SQLAlchemy repository in task-06.
    """

    def __init__(self):
        """Initialize repository with empty storage."""
        self._storage: Dict[int, UserResponse] = {}
        self._counter: int = 0
        self._telegram_id_index: Dict[str, int] = {}  # Index for telegram_id lookup

    def _get_next_id(self) -> int:
        """Generate next user ID."""
        self._counter += 1
        return self._counter

    def create(
        self,
        telegram_id: str,
        name: str,
        role: UserRole,
    ) -> UserResponse:
        """Create a new user.

        Args:
            telegram_id: Telegram ID for bot login
            name: Display name
            role: User role (tenant, owner, both)

        Returns:
            Created user response
        """
        user_id = self._get_next_id()
        user = UserResponse(
            id=user_id,
            telegram_id=telegram_id,
            name=name,
            role=role,
            created_at=datetime.now(timezone.utc),
        )
        self._storage[user_id] = user
        self._telegram_id_index[telegram_id] = user_id
        return user

    def get(self, user_id: int) -> Optional[UserResponse]:
        """Get user by ID.

        Args:
            user_id: User identifier

        Returns:
            User if found, None otherwise
        """
        return self._storage.get(user_id)

    def get_by_telegram_id(self, telegram_id: str) -> Optional[UserResponse]:
        """Get user by Telegram ID.

        Args:
            telegram_id: Telegram ID

        Returns:
            User if found, None otherwise
        """
        user_id = self._telegram_id_index.get(telegram_id)
        if user_id:
            return self._storage.get(user_id)
        return None

    def get_all(
        self,
        role: Optional[UserRole] = None,
        limit: int = 20,
        offset: int = 0,
        sort: Optional[str] = None,
    ) -> tuple[List[UserResponse], int]:
        """Get all users with optional filtering.

        Args:
            role: Filter by user role
            limit: Number of results to return
            offset: Number of results to skip
            sort: Sort field (prefix with - for descending)

        Returns:
            Tuple of (filtered users list, total count)
        """
        users = list(self._storage.values())

        # Apply filters
        if role is not None:
            users = [u for u in users if u.role == role]

        # Apply sorting
        if sort:
            reverse = sort.startswith("-")
            sort_field = sort[1:] if reverse else sort
            if sort_field in ("name", "created_at", "id"):
                users = sorted(
                    users,
                    key=lambda u: getattr(u, sort_field),
                    reverse=reverse,
                )

        total = len(users)

        # Apply pagination
        users = users[offset : offset + limit]

        return users, total

    def update(
        self,
        user_id: int,
        name: Optional[str] = None,
        role: Optional[UserRole] = None,
    ) -> Optional[UserResponse]:
        """Update user fields.

        Args:
            user_id: User identifier
            name: New name (optional)
            role: New role (optional)

        Returns:
            Updated user if found, None otherwise
        """
        user = self._storage.get(user_id)
        if not user:
            return None

        # Create updated user with new values
        updated_data = user.model_dump()
        if name is not None:
            updated_data["name"] = name
        if role is not None:
            updated_data["role"] = role

        updated_user = UserResponse(**updated_data)
        self._storage[user_id] = updated_user
        return updated_user

    def delete(self, user_id: int) -> bool:
        """Delete user by ID.

        Args:
            user_id: User identifier

        Returns:
            True if deleted, False if not found
        """
        user = self._storage.get(user_id)
        if user:
            del self._storage[user_id]
            del self._telegram_id_index[user.telegram_id]
            return True
        return False

    def clear(self) -> None:
        """Clear all users (for testing)."""
        self._storage.clear()
        self._telegram_id_index.clear()
        self._counter = 0
