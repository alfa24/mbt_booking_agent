"""User service with business logic."""

from typing import List, Optional

from fastapi import Depends

from backend.exceptions import UserNotFoundError
from backend.repositories.user import UserRepository
from backend.schemas.user import (
    CreateUserRequest,
    UpdateUserRequest,
    UserFilterParams,
    UserResponse,
    UserRole,
)


def get_user_repository() -> UserRepository:
    """Dependency provider for user repository.

    Returns singleton instance of in-memory repository.
    To be replaced with database session in task-06.
    """
    if not hasattr(get_user_repository, "_instance"):
        get_user_repository._instance = UserRepository()
    return get_user_repository._instance


class UserService:
    """Service layer for user operations.

    Handles business logic: CRUD operations for users.
    """

    def __init__(
        self,
        repository: UserRepository = Depends(get_user_repository),
    ):
        """Initialize service with repository.

        Args:
            repository: User repository instance
        """
        self._repo = repository

    def create_user(self, request: CreateUserRequest) -> UserResponse:
        """Create a new user.

        Args:
            request: User creation request

        Returns:
            Created user
        """
        return self._repo.create(
            telegram_id=request.telegram_id,
            name=request.name,
            role=request.role,
        )

    def get_user(self, user_id: int) -> UserResponse:
        """Get user by ID.

        Args:
            user_id: User identifier

        Returns:
            User data

        Raises:
            UserNotFoundError: If user not found
        """
        user = self._repo.get(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user

    def get_user_by_telegram_id(self, telegram_id: str) -> Optional[UserResponse]:
        """Get user by Telegram ID.

        Args:
            telegram_id: Telegram ID

        Returns:
            User if found, None otherwise
        """
        return self._repo.get_by_telegram_id(telegram_id)

    def list_users(
        self,
        filters: UserFilterParams,
    ) -> tuple[List[UserResponse], int]:
        """List users with filtering and pagination.

        Args:
            filters: Filter and pagination parameters

        Returns:
            Tuple of (users list, total count)
        """
        return self._repo.get_all(
            role=filters.role,
            limit=filters.limit,
            offset=filters.offset,
            sort=filters.sort,
        )

    def update_user(
        self,
        user_id: int,
        request: UpdateUserRequest,
    ) -> UserResponse:
        """Update user profile.

        Args:
            user_id: User identifier
            request: Update request with fields to change

        Returns:
            Updated user

        Raises:
            UserNotFoundError: If user not found
        """
        existing = self._repo.get(user_id)
        if not existing:
            raise UserNotFoundError(user_id)

        updated = self._repo.update(
            user_id=user_id,
            name=request.name,
            role=request.role,
        )
        return updated

    def replace_user(
        self,
        user_id: int,
        request: CreateUserRequest,
    ) -> UserResponse:
        """Replace user profile (full update).

        Args:
            user_id: User identifier
            request: Full user data

        Returns:
            Updated user

        Raises:
            UserNotFoundError: If user not found
        """
        existing = self._repo.get(user_id)
        if not existing:
            raise UserNotFoundError(user_id)

        # For full replace, we update all fields
        updated = self._repo.update(
            user_id=user_id,
            name=request.name,
            role=request.role,
        )
        return updated

    def delete_user(self, user_id: int) -> None:
        """Delete a user.

        Args:
            user_id: User identifier

        Raises:
            UserNotFoundError: If user not found
        """
        existing = self._repo.get(user_id)
        if not existing:
            raise UserNotFoundError(user_id)

        self._repo.delete(user_id)
