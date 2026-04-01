"""Tariff API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from backend.schemas.common import ErrorResponse, PaginatedResponse
from backend.schemas.tariff import (
    CreateTariffRequest,
    TariffResponse,
    UpdateTariffRequest,
)
from backend.services.tariff import TariffService

tariffs_router = APIRouter(prefix="/tariffs", tags=["tariffs"])


@tariffs_router.get(
    "",
    response_model=PaginatedResponse[TariffResponse],
    summary="List tariffs",
    description="Get list of all available tariffs.",
    responses={
        200: {"description": "List of tariffs returned successfully"},
    },
)
async def list_tariffs(
    service: Annotated[TariffService, Depends(TariffService)],
    limit: int = 20,
    offset: int = 0,
    sort: str = "id",
) -> PaginatedResponse[TariffResponse]:
    """List all tariffs.

    Results are paginated using limit/offset.

    Args:
        limit: Number of results to return
        offset: Number of results to skip
        sort: Sort field (prefix with - for descending)
        service: Tariff service instance

    Returns:
        Paginated list of tariffs
    """
    tariffs, total = await service.list_tariffs(limit=limit, offset=offset, sort=sort)
    return PaginatedResponse(
        items=tariffs,
        total=total,
        limit=limit,
        offset=offset,
    )


@tariffs_router.get(
    "/{tariff_id}",
    response_model=TariffResponse,
    summary="Get tariff by ID",
    description="Retrieve detailed information about a specific tariff.",
    responses={
        200: {"description": "Tariff found and returned"},
        404: {
            "description": "Tariff not found",
            "model": ErrorResponse,
        },
    },
)
async def get_tariff(
    tariff_id: int,
    service: Annotated[TariffService, Depends(TariffService)],
) -> TariffResponse:
    """Get a single tariff by its ID.

    Args:
        tariff_id: Unique tariff identifier
        service: Tariff service instance

    Returns:
        Tariff details

    Raises:
        HTTPException: 404 if tariff not found
    """
    return await service.get_tariff(tariff_id)


@tariffs_router.post(
    "",
    response_model=TariffResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create tariff",
    description="Create a new tariff (for landlords/admins).",
    responses={
        201: {"description": "Tariff created successfully"},
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def create_tariff(
    request: CreateTariffRequest,
    service: Annotated[TariffService, Depends(TariffService)],
) -> TariffResponse:
    """Create a new tariff.

    Args:
        request: Tariff creation data
        service: Tariff service instance

    Returns:
        Created tariff with generated ID

    Raises:
        HTTPException: 422 if validation fails
    """
    return await service.create_tariff(request)


@tariffs_router.patch(
    "/{tariff_id}",
    response_model=TariffResponse,
    summary="Update tariff",
    description="Update tariff information (partial update).",
    responses={
        200: {"description": "Tariff updated successfully"},
        404: {
            "description": "Tariff not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def update_tariff(
    tariff_id: int,
    request: UpdateTariffRequest,
    service: Annotated[TariffService, Depends(TariffService)],
) -> TariffResponse:
    """Update an existing tariff.

    Only provided fields will be updated.

    Args:
        tariff_id: Tariff identifier
        request: Fields to update
        service: Tariff service instance

    Returns:
        Updated tariff

    Raises:
        HTTPException: 404 if not found, 422 if validation fails
    """
    return await service.update_tariff(tariff_id, request)


@tariffs_router.delete(
    "/{tariff_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete tariff",
    description="Delete a tariff.",
    responses={
        204: {"description": "Tariff deleted successfully"},
        404: {
            "description": "Tariff not found",
            "model": ErrorResponse,
        },
    },
)
async def delete_tariff(
    tariff_id: int,
    service: Annotated[TariffService, Depends(TariffService)],
) -> None:
    """Delete a tariff.

    Args:
        tariff_id: Tariff identifier
        service: Tariff service instance

    Raises:
        HTTPException: 404 if tariff not found
    """
    await service.delete_tariff(tariff_id)
