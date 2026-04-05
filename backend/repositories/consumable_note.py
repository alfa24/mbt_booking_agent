"""SQLAlchemy consumable note repository."""

from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.consumable_note import ConsumableNote
from backend.schemas.consumable_note import ConsumableNoteResponse


class ConsumableNoteRepository:
    """SQLAlchemy repository for consumable notes."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def create(
        self,
        house_id: int,
        created_by: int,
        name: str,
        comment: str | None = None,
    ) -> ConsumableNoteResponse:
        """Create a new consumable note.

        Args:
            house_id: ID of the house
            created_by: ID of the user creating the note
            name: Consumable name
            comment: Optional comment

        Returns:
            Created note response
        """
        note = ConsumableNote(
            house_id=house_id,
            created_by=created_by,
            name=name,
            comment=comment,
        )
        self._session.add(note)
        await self._session.flush()
        await self._session.refresh(note)
        return ConsumableNoteResponse.model_validate(note)

    async def get(self, note_id: int) -> ConsumableNoteResponse | None:
        """Get note by ID.

        Args:
            note_id: Note identifier

        Returns:
            Note if found, None otherwise
        """
        result = await self._session.execute(
            select(ConsumableNote).where(ConsumableNote.id == note_id)
        )
        note = result.scalar_one_or_none()
        return ConsumableNoteResponse.model_validate(note) if note else None

    async def get_multi(
        self,
        house_id: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[ConsumableNoteResponse], int]:
        """Get multiple notes with optional filtering.

        Args:
            house_id: Filter by house ID
            limit: Number of results to return
            offset: Number of results to skip

        Returns:
            Tuple of (notes list, total count)
        """
        query = select(ConsumableNote)

        # Apply filters
        if house_id is not None:
            query = query.where(ConsumableNote.house_id == house_id)

        # Get total count
        count_result = await self._session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Apply pagination
        query = query.offset(offset).limit(limit)

        result = await self._session.execute(query)
        notes = result.scalars().all()
        return [ConsumableNoteResponse.model_validate(n) for n in notes], total

    async def update(
        self,
        note_id: int,
        name: str | None = None,
        comment: str | None = None,
    ) -> ConsumableNoteResponse | None:
        """Update note fields.

        Args:
            note_id: Note identifier
            name: New name (optional)
            comment: New comment (optional)

        Returns:
            Updated note if found, None otherwise
        """
        result = await self._session.execute(
            select(ConsumableNote).where(ConsumableNote.id == note_id)
        )
        note = result.scalar_one_or_none()
        if not note:
            return None

        if name is not None:
            note.name = name
        if comment is not None:
            note.comment = comment

        await self._session.flush()
        await self._session.refresh(note)
        return ConsumableNoteResponse.model_validate(note)

    async def delete(self, note_id: int) -> bool:
        """Delete note by ID.

        Args:
            note_id: Note identifier

        Returns:
            True if deleted, False if not found
        """
        result = await self._session.execute(
            select(ConsumableNote).where(ConsumableNote.id == note_id)
        )
        note = result.scalar_one_or_none()
        if not note:
            return False

        await self._session.delete(note)
        return True
