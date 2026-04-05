"""Pydantic schemas for Dashboard resource."""

from typing import List

from pydantic import BaseModel, Field


class MonthlyRevenue(BaseModel):
    """Monthly revenue data point."""

    month: str = Field(..., description="Month in YYYY-MM format")
    revenue: float = Field(..., description="Revenue amount in rubles")


class OwnerDashboardResponse(BaseModel):
    """Owner dashboard KPI response."""

    total_bookings: int = Field(..., description="Total number of bookings")
    total_revenue: float = Field(..., description="Total revenue in rubles")
    occupancy_rate: float = Field(..., description="Occupancy rate percentage (0-100)")
    active_bookings: int = Field(..., description="Number of active (non-cancelled) bookings")
    monthly_revenue: List[MonthlyRevenue] = Field(
        default_factory=list, description="Revenue by month"
    )


class RevenueByHouse(BaseModel):
    """Revenue data for a specific house."""

    house_id: int = Field(..., description="House identifier")
    house_name: str = Field(..., description="House name")
    revenue: float = Field(..., description="Revenue amount in rubles")


class BookingsByMonth(BaseModel):
    """Booking count by month."""

    month: str = Field(..., description="Month in YYYY-MM format")
    count: int = Field(..., description="Number of bookings")


class LeaderboardResponse(BaseModel):
    """Leaderboard response with aggregated statistics."""

    bookings_by_month: List[BookingsByMonth] = Field(
        default_factory=list, description="Bookings count by month"
    )
    revenue_by_house: List[RevenueByHouse] = Field(
        default_factory=list, description="Revenue breakdown by house"
    )


class HouseStatsResponse(BaseModel):
    """Statistics for a specific house."""

    occupancy_rate: float = Field(..., description="Occupancy rate percentage (0-100)")
    total_revenue: float = Field(..., description="Total revenue in rubles")
    total_bookings: int = Field(..., description="Total number of bookings")
