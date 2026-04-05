"""Consumable note service with business logic."""

from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.exceptions import HouseNotFoundError, UserNotFoundError
from backend.repositories.consumable_note import ConsumableNoteRepository
from backend.repositories.house import HouseRepository
from backend.repositories.user import UserRepository
from backend.schemas.consumable_note import (
    ConsumableNoteResponse,
    CreateConsumableNoteRequest,
    UpdateConsumableNoteRequest,
)


async def get_consumable_note_repository(
    db: AsyncSession = Depends(get_db),
) -> ConsumableNoteRepository:
    """Dependency provider for consumable note repository.

    Args:
        db: Database session from dependency injection

    Returns:
        ConsumableNoteRepository instance with database session
    """
    return ConsumableNoteRepository(db)


async def get_house_repository(
    db: AsyncSession = Depends(get_db),
) -> HouseRepository:
    """Dependency provider for house repository.

    Args:
        db: Database session from dependency injection

    Returns:
        HouseRepository instance with database session
    """
    return HouseRepository(db)


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


class ConsumableNoteService:
    """Service layer for consumable note operations."""

    def __init__(
        self,
        repository: ConsumableNoteRepository = Depends(get_consumable_note_repository),
        house_repository: HouseRepository = Depends(get_house_repository),
        user_repository: UserRepository = Depends(get_user_repository),
    ):
        """Initialize service with repositories.

        Args:
            repository: Consumable note repository instance
            house_repository: House repository instance
            user_repository: User repository instance
        """
        self._repo = repository
        self._house_repo = house_repository
        self._user_repo = user_repository

    async def create_note(
        self,
        request: CreateConsumableNoteRequest,
    ) -> ConsumableNoteResponse:
        """Create a new consumable note.

        Args:
            request: Note creation request

        Returns:
            Created note

        Raises:
            HouseNotFoundError: If house not found
            UserNotFoundError: If user not found
        """
        # Verify house exists
        house = await self._house_repo.get(request.house_id)
        if not house:
            raise HouseNotFoundError(request.house_id)

        # Verify user exists
        user = await self._user_repo.get(request.created_by)
        if not user:
            raise UserNotFoundError(request.created_by)

        return await self._repo.create(
            house_id=request.house_id,
            created_by=request.created_by,
            name=request.name,
            comment=request.comment,
        )

    async def get_note(self, note_id: int) -> ConsumableNoteResponse:
        """Get note by ID.

        Args:
            note_id: Note identifier

        Returns:
            Note data

        Raises:
            ValueError: If note not found
        """
        note = await self._repo.get(note_id)
        if not note:
            raise ValueError(f"Consumable note {note_id} not found")
        return note

    async def list_notes(
        self,
        house_id: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[ConsumableNoteResponse], int]:
        """List notes with optional filtering.

        Args:
            house_id: Filter by house ID
            limit: Number of results to return
            offset: Number of results to skip

        Returns:
            Tuple of (notes list, total count)
        """
        return await self._repo.get_multi(
            house_id=house_id,
            limit=limit,
            offset=offset,
        )

    async def update_note(
        self,
        note_id: int,
        request: UpdateConsumableNoteRequest,
    ) -> ConsumableNoteResponse:
        """Update a note.

        Args:
            note_id: Note identifier
            request: Update request

        Returns:
            Updated note

        Raises:
            ValueError: If note not found
        """
        existing = await self._repo.get(note_id)
        if not existing:
            raise ValueError(f"Consumable note {note_id} not found")

        updated = await self._repo.update(
            note_id=note_id,
            name=request.name,
            comment=request.comment,
        )
        return updated

    async def delete_note(self, note_id: int) -> None:
        """Delete a note.

        Args:
            note_id: Note identifier

        Raises:
            ValueError: If note not found
        """
        existing = await self._repo.get(note_id)
        if not existing:
            raise ValueError(f"Consumable note {note_id} not found")

        await self._repo.delete(note_id)
