"""User service with business logic."""

from typing import List, Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.exceptions import UserNotFoundError
from backend.repositories.user import UserRepository
from backend.schemas.user import (
    CreateUserRequest,
    UpdateUserRequest,
    UserFilterParams,
    UserResponse,
)


async def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> UserRepository:
    """Dependency provider for user repository.

    Args:
        db: Database session from dependency injection

    Returns:
        UserRepository instance with database session
    """
    return UserRepository(db)


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

    async def create_user(self, request: CreateUserRequest) -> UserResponse:
        """Create a new user.

        Args:
            request: User creation request

        Returns:
            Created user
        """
        return await self._repo.create(
            telegram_id=request.telegram_id,
            name=request.name,
            role=request.role,
        )

    async def get_user(self, user_id: int) -> UserResponse:
        """Get user by ID.

        Args:
            user_id: User identifier

        Returns:
            User data

        Raises:
            UserNotFoundError: If user not found
        """
        user = await self._repo.get(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user

    async def get_user_by_telegram_id(self, telegram_id: str) -> Optional[UserResponse]:
        """Get user by Telegram ID.

        Args:
            telegram_id: Telegram ID

        Returns:
            User if found, None otherwise
        """
        return await self._repo.get_by_telegram_id(telegram_id)

    async def list_users(
        self,
        filters: UserFilterParams,
    ) -> tuple[List[UserResponse], int]:
        """List users with filtering and pagination.

        Args:
            filters: Filter and pagination parameters

        Returns:
            Tuple of (users list, total count)
        """
        return await self._repo.get_all(
            role=filters.role,
            limit=filters.limit,
            offset=filters.offset,
            sort=filters.sort,
        )

    async def update_user(
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
        existing = await self._repo.get(user_id)
        if not existing:
            raise UserNotFoundError(user_id)

        updated = await self._repo.update(
            user_id=user_id,
            name=request.name,
            role=request.role,
        )
        return updated

    async def replace_user(
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
        existing = await self._repo.get(user_id)
        if not existing:
            raise UserNotFoundError(user_id)

        # For full replace, we update all fields
        updated = await self._repo.update(
            user_id=user_id,
            name=request.name,
            role=request.role,
        )
        return updated

    async def delete_user(self, user_id: int) -> None:
        """Delete a user.

        Args:
            user_id: User identifier

        Raises:
            UserNotFoundError: If user not found
        """
        existing = await self._repo.get(user_id)
        if not existing:
            raise UserNotFoundError(user_id)

        await self._repo.delete(user_id)
