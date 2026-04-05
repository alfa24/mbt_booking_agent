"""Dashboard API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from backend.schemas.common import ErrorResponse
from backend.schemas.dashboard import (
    HouseStatsResponse,
    LeaderboardResponse,
    OwnerDashboardResponse,
)
from backend.services.dashboard import DashboardService

dashboard_router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@dashboard_router.get(
    "/owner",
    response_model=OwnerDashboardResponse,
    summary="Get owner dashboard",
    description="Get KPIs for the owner dashboard.",
    responses={
        200: {"description": "Dashboard data returned successfully"},
    },
)
async def get_owner_dashboard(
    service: Annotated[DashboardService, Depends(DashboardService)],
    # TODO: Replace with actual auth when implementing authentication
    user_id: int | None = None,
) -> OwnerDashboardResponse:
    """Get owner dashboard KPIs.

    Args:
        service: Dashboard service instance
        user_id: User identifier (from auth, optional)

    Returns:
        Dashboard KPI data
    """
    return await service.get_owner_dashboard(user_id=user_id)


@dashboard_router.get(
    "/leaderboard",
    response_model=LeaderboardResponse,
    summary="Get leaderboard",
    description="Get aggregated statistics for leaderboard.",
    responses={
        200: {"description": "Leaderboard data returned successfully"},
    },
)
async def get_leaderboard(
    service: Annotated[DashboardService, Depends(DashboardService)],
) -> LeaderboardResponse:
    """Get leaderboard statistics.

    Args:
        service: Dashboard service instance

    Returns:
        Leaderboard data
    """
    return await service.get_leaderboard()


@dashboard_router.get(
    "/houses/{house_id}/stats",
    response_model=HouseStatsResponse,
    summary="Get house stats",
    description="Get statistics for a specific house.",
    responses={
        200: {"description": "House stats returned successfully"},
        404: {
            "description": "House not found",
            "model": ErrorResponse,
        },
    },
)
async def get_house_stats(
    house_id: int,
    service: Annotated[DashboardService, Depends(DashboardService)],
    period: str = "30d",
) -> HouseStatsResponse:
    """Get statistics for a specific house.

    Args:
        house_id: House identifier
        service: Dashboard service instance
        period: Time period (e.g., "30d", "90d", "1y")

    Returns:
        House statistics

    Raises:
        HTTPException: 404 if house not found
    """
    return await service.get_house_stats(house_id=house_id, period=period)
