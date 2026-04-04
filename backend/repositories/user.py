"""SQLAlchemy user repository."""

from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import User, UserRole
from backend.schemas.user import UserResponse


class UserRepository:
    """SQLAlchemy repository for users."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def create(
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
        user = User(telegram_id=telegram_id, name=name, role=role)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return UserResponse.model_validate(user)

    async def get(self, user_id: int) -> UserResponse | None:
        """Get user by ID.

        Args:
            user_id: User identifier

        Returns:
            User if found, None otherwise
        """
        result = await self._session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return UserResponse.model_validate(user) if user else None

    async def get_by_telegram_id(self, telegram_id: str) -> UserResponse | None:
        """Get user by Telegram ID.

        Args:
            telegram_id: Telegram ID

        Returns:
            User if found, None otherwise
        """
        result = await self._session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        return UserResponse.model_validate(user) if user else None

    async def get_all(
        self,
        role: UserRole | None = None,
        limit: int = 20,
        offset: int = 0,
        sort: str | None = None,
    ) -> tuple[list[UserResponse], int]:
        """Get all users with optional filtering.

        Args:
            role: Filter by user role
            limit: Number of results to return
            offset: Number of results to skip
            sort: Sort field (prefix with - for descending)

        Returns:
            Tuple of (filtered users list, total count)
        """
        query = select(User)

        # Apply filters
        if role is not None:
            query = query.where(User.role == role)

        # Get total count
        count_result = await self._session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Apply sorting
        if sort:
            reverse = sort.startswith("-")
            sort_field = sort[1:] if reverse else sort
            if hasattr(User, sort_field):
                order = (
                    getattr(User, sort_field).desc()
                    if reverse
                    else getattr(User, sort_field)
                )
                query = query.order_by(order)

        # Apply pagination
        query = query.offset(offset).limit(limit)

        result = await self._session.execute(query)
        users = result.scalars().all()
        return [UserResponse.model_validate(user) for user in users], total

    async def update(
        self,
        user_id: int,
        name: str | None = None,
        role: UserRole | None = None,
    ) -> UserResponse | None:
        """Update user fields.

        Args:
            user_id: User identifier
            name: New name (optional)
            role: New role (optional)

        Returns:
            Updated user if found, None otherwise
        """
        result = await self._session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None

        if name is not None:
            user.name = name
        if role is not None:
            user.role = role

        await self._session.flush()
        await self._session.refresh(user)
        return UserResponse.model_validate(user)

    async def delete(self, user_id: int) -> bool:
        """Delete user by ID.

        Args:
            user_id: User identifier

        Returns:
            True if deleted, False if not found
        """
        result = await self._session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return False

        await self._session.delete(user)
        return True
