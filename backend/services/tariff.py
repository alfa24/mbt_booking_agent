"""Tariff service with business logic."""

from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.exceptions import TariffNotFoundError
from backend.repositories.tariff import TariffRepository
from backend.schemas.tariff import (
    CreateTariffRequest,
    TariffResponse,
    UpdateTariffRequest,
)


async def get_tariff_repository(
    db: AsyncSession = Depends(get_db),
) -> TariffRepository:
    """Dependency provider for tariff repository.

    Args:
        db: Database session from dependency injection

    Returns:
        TariffRepository instance with database session
    """
    return TariffRepository(db)


class TariffService:
    """Service layer for tariff operations.

    Handles business logic: CRUD operations for tariffs.
    """

    def __init__(
        self,
        repository: TariffRepository = Depends(get_tariff_repository),
    ):
        """Initialize service with repository.

        Args:
            repository: Tariff repository instance
        """
        self._repo = repository

    async def create_tariff(self, request: CreateTariffRequest) -> TariffResponse:
        """Create a new tariff.

        Args:
            request: Tariff creation request

        Returns:
            Created tariff
        """
        return await self._repo.create(
            name=request.name,
            amount=request.amount,
        )

    async def get_tariff(self, tariff_id: int) -> TariffResponse:
        """Get tariff by ID.

        Args:
            tariff_id: Tariff identifier

        Returns:
            Tariff data

        Raises:
            TariffNotFoundError: If tariff not found
        """
        tariff = await self._repo.get(tariff_id)
        if not tariff:
            raise TariffNotFoundError(tariff_id)
        return tariff

    async def list_tariffs(
        self,
        limit: int = 20,
        offset: int = 0,
        sort: str = "id",
    ) -> tuple[List[TariffResponse], int]:
        """List tariffs with pagination.

        Args:
            limit: Number of results to return
            offset: Number of results to skip
            sort: Sort field (prefix with - for descending)

        Returns:
            Tuple of (tariffs list, total count)
        """
        return await self._repo.get_all(
            limit=limit,
            offset=offset,
            sort=sort,
        )

    async def update_tariff(
        self,
        tariff_id: int,
        request: UpdateTariffRequest,
    ) -> TariffResponse:
        """Update tariff information.

        Args:
            tariff_id: Tariff identifier
            request: Update request with fields to change

        Returns:
            Updated tariff

        Raises:
            TariffNotFoundError: If tariff not found
        """
        existing = await self._repo.get(tariff_id)
        if not existing:
            raise TariffNotFoundError(tariff_id)

        updated = await self._repo.update(
            tariff_id=tariff_id,
            name=request.name,
            amount=request.amount,
        )
        return updated

    async def delete_tariff(self, tariff_id: int) -> None:
        """Delete a tariff.

        Args:
            tariff_id: Tariff identifier

        Raises:
            TariffNotFoundError: If tariff not found
        """
        existing = await self._repo.get(tariff_id)
        if not existing:
            raise TariffNotFoundError(tariff_id)

        await self._repo.delete(tariff_id)
