"""SQLAlchemy tariff repository."""

from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.tariff import Tariff
from backend.schemas.tariff import TariffResponse


class TariffRepository:
    """SQLAlchemy repository for tariffs."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def create(
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
        tariff = Tariff(name=name, amount=amount)
        self._session.add(tariff)
        await self._session.flush()
        await self._session.refresh(tariff)
        return TariffResponse.model_validate(tariff)

    async def get(self, tariff_id: int) -> TariffResponse | None:
        """Get tariff by ID.

        Args:
            tariff_id: Tariff identifier

        Returns:
            Tariff if found, None otherwise
        """
        result = await self._session.execute(
            select(Tariff).where(Tariff.id == tariff_id)
        )
        tariff = result.scalar_one_or_none()
        return TariffResponse.model_validate(tariff) if tariff else None

    async def get_all(
        self,
        limit: int = 20,
        offset: int = 0,
        sort: str | None = None,
    ) -> tuple[list[TariffResponse], int]:
        """Get all tariffs with optional sorting and pagination.

        Args:
            limit: Number of results to return
            offset: Number of results to skip
            sort: Sort field (prefix with - for descending)

        Returns:
            Tuple of (tariffs list, total count)
        """
        query = select(Tariff)

        # Get total count
        count_result = await self._session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Apply sorting
        if sort:
            reverse = sort.startswith("-")
            sort_field = sort[1:] if reverse else sort
            if hasattr(Tariff, sort_field):
                order = (
                    getattr(Tariff, sort_field).desc()
                    if reverse
                    else getattr(Tariff, sort_field)
                )
                query = query.order_by(order)

        # Apply pagination
        query = query.offset(offset).limit(limit)

        result = await self._session.execute(query)
        tariffs = result.scalars().all()
        return [TariffResponse.model_validate(tariff) for tariff in tariffs], total

    async def update(
        self,
        tariff_id: int,
        name: str | None = None,
        amount: int | None = None,
    ) -> TariffResponse | None:
        """Update tariff fields.

        Args:
            tariff_id: Tariff identifier
            name: New name (optional)
            amount: New amount (optional)

        Returns:
            Updated tariff if found, None otherwise
        """
        result = await self._session.execute(
            select(Tariff).where(Tariff.id == tariff_id)
        )
        tariff = result.scalar_one_or_none()
        if not tariff:
            return None

        if name is not None:
            tariff.name = name
        if amount is not None:
            tariff.amount = amount

        await self._session.flush()
        await self._session.refresh(tariff)
        return TariffResponse.model_validate(tariff)

    async def delete(self, tariff_id: int) -> bool:
        """Delete tariff by ID.

        Args:
            tariff_id: Tariff identifier

        Returns:
            True if deleted, False if not found
        """
        result = await self._session.execute(
            select(Tariff).where(Tariff.id == tariff_id)
        )
        tariff = result.scalar_one_or_none()
        if not tariff:
            return False

        await self._session.delete(tariff)
        return True
