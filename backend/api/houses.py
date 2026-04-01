"""House API endpoints."""

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, status

from backend.schemas.common import ErrorResponse, PaginatedResponse
from backend.schemas.house import (
    CreateHouseRequest,
    HouseCalendarResponse,
    HouseFilterParams,
    HouseResponse,
    UpdateHouseRequest,
)
from backend.services.house import HouseService

houses_router = APIRouter(prefix="/houses", tags=["houses"])


@houses_router.get(
    "",
    response_model=PaginatedResponse[HouseResponse],
    summary="List houses",
    description="Get list of houses with optional filtering and pagination.",
    responses={
        200: {"description": "List of houses returned successfully"},
    },
)
async def list_houses(
    filters: Annotated[HouseFilterParams, Depends()],
    service: Annotated[HouseService, Depends(HouseService)],
) -> PaginatedResponse[HouseResponse]:
    """List all houses with filtering.

    Supports filtering by owner_id, is_active, and capacity ranges.
    Results are paginated using limit/offset.

    Args:
        filters: Query parameters for filtering and pagination
        service: House service instance

    Returns:
        Paginated list of houses
    """
    houses, total = service.list_houses(filters)
    return PaginatedResponse(
        items=houses,
        total=total,
        limit=filters.limit,
        offset=filters.offset,
    )


@houses_router.get(
    "/{house_id}",
    response_model=HouseResponse,
    summary="Get house by ID",
    description="Retrieve detailed information about a specific house.",
    responses={
        200: {"description": "House found and returned"},
        404: {
            "description": "House not found",
            "model": ErrorResponse,
        },
    },
)
async def get_house(
    house_id: int,
    service: Annotated[HouseService, Depends(HouseService)],
) -> HouseResponse:
    """Get a single house by its ID.

    Args:
        house_id: Unique house identifier
        service: House service instance

    Returns:
        House details

    Raises:
        HTTPException: 404 if house not found
    """
    return service.get_house(house_id)


@houses_router.post(
    "",
    response_model=HouseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create house",
    description="Create a new house listing.",
    responses={
        201: {"description": "House created successfully"},
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def create_house(
    request: CreateHouseRequest,
    service: Annotated[HouseService, Depends(HouseService)],
) -> HouseResponse:
    """Create a new house.

    Args:
        request: House creation data
        service: House service instance

    Returns:
        Created house with generated ID

    Raises:
        HTTPException: 422 if validation fails
    """
    # TODO: Replace with actual auth when implementing authentication
    owner_id = 1
    return service.create_house(owner_id, request)


@houses_router.put(
    "/{house_id}",
    response_model=HouseResponse,
    summary="Replace house",
    description="Replace all house information (full update).",
    responses={
        200: {"description": "House updated successfully"},
        404: {
            "description": "House not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def replace_house(
    house_id: int,
    request: CreateHouseRequest,
    service: Annotated[HouseService, Depends(HouseService)],
) -> HouseResponse:
    """Replace house information (full update).

    Args:
        house_id: House identifier
        request: Complete house data
        service: House service instance

    Returns:
        Updated house

    Raises:
        HTTPException: 404 if house not found, 422 if validation fails
    """
    return service.replace_house(house_id, request)


@houses_router.patch(
    "/{house_id}",
    response_model=HouseResponse,
    summary="Update house",
    description="Update house details (partial update).",
    responses={
        200: {"description": "House updated successfully"},
        404: {
            "description": "House not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def update_house(
    house_id: int,
    request: UpdateHouseRequest,
    service: Annotated[HouseService, Depends(HouseService)],
) -> HouseResponse:
    """Update an existing house.

    Only provided fields will be updated.

    Args:
        house_id: House identifier
        request: Fields to update
        service: House service instance

    Returns:
        Updated house

    Raises:
        HTTPException: 404 if not found, 422 if validation fails
    """
    return service.update_house(house_id, request)


@houses_router.delete(
    "/{house_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete house",
    description="Delete a house listing.",
    responses={
        204: {"description": "House deleted successfully"},
        404: {
            "description": "House not found",
            "model": ErrorResponse,
        },
    },
)
async def delete_house(
    house_id: int,
    service: Annotated[HouseService, Depends(HouseService)],
) -> None:
    """Delete a house.

    Args:
        house_id: House identifier
        service: House service instance

    Raises:
        HTTPException: 404 if house not found
    """
    service.delete_house(house_id)


@houses_router.get(
    "/{house_id}/calendar",
    response_model=HouseCalendarResponse,
    summary="Get house calendar",
    description="Get house availability calendar with occupied date ranges.",
    responses={
        200: {"description": "Calendar returned successfully"},
        404: {
            "description": "House not found",
            "model": ErrorResponse,
        },
    },
)
async def get_house_calendar(
    house_id: int,
    service: Annotated[HouseService, Depends(HouseService)],
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> HouseCalendarResponse:
    """Get house availability calendar.

    Returns all occupied date ranges for the house.
    Optionally filter by date range.

    Args:
        house_id: House identifier
        date_from: Start of period filter (optional)
        date_to: End of period filter (optional)
        service: House service instance

    Returns:
        Calendar with occupied date ranges

    Raises:
        HTTPException: 404 if house not found
    """
    return service.get_house_calendar(house_id, date_from, date_to)
