"""Dashboard service with business logic."""

from datetime import date, timedelta
from typing import List

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.exceptions import HouseNotFoundError
from backend.models.booking import Booking, BookingStatus
from backend.models.house import House
from backend.repositories.house import HouseRepository
from backend.schemas.dashboard import (
    BookingsByMonth,
    HouseStatsResponse,
    LeaderboardResponse,
    MonthlyRevenue,
    OwnerDashboardResponse,
    RevenueByHouse,
)


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


class DashboardService:
    """Service layer for dashboard operations."""

    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        house_repository: HouseRepository = Depends(get_house_repository),
    ):
        """Initialize service.

        Args:
            db: Database session
            house_repository: House repository instance
        """
        self._db = db
        self._house_repo = house_repository

    async def get_owner_dashboard(
        self,
        user_id: int | None = None,
    ) -> OwnerDashboardResponse:
        """Get owner dashboard KPIs.

        Args:
            user_id: Optional user ID to filter by owner

        Returns:
            Dashboard KPI data
        """
        # Base query for bookings
        booking_query = select(Booking)
        house_ids: list[int] = []
        if user_id is not None:
            # Filter by houses owned by user
            house_ids_query = select(House.id).where(House.owner_id == user_id)
            house_ids_result = await self._db.execute(house_ids_query)
            house_ids = [r[0] for r in house_ids_result.all()]
            if house_ids:
                booking_query = booking_query.where(Booking.house_id.in_(house_ids))
            else:
                # Owner has no houses - return empty dashboard
                return OwnerDashboardResponse(
                    total_bookings=0,
                    total_revenue=0.0,
                    occupancy_rate=0.0,
                    active_bookings=0,
                    monthly_revenue=[],
                )

        # Get all bookings for calculations
        result = await self._db.execute(booking_query)
        bookings = result.scalars().all()

        # Calculate totals
        total_bookings = len(bookings)
        active_bookings = len([b for b in bookings if b.status != BookingStatus.CANCELLED])
        total_revenue = sum(
            (b.total_amount or 0) for b in bookings if b.status == BookingStatus.COMPLETED
        )

        # Calculate occupancy rate (simplified: active bookings / total capacity over time)
        # For MVP, we'll use a simple heuristic
        occupancy_rate = 0.0
        if active_bookings > 0:
            # Rough estimate: assume 30 days period, 16 capacity per house
            total_capacity_days = 30 * 16  # Simplified
            booked_days = sum(
                (b.check_out - b.check_in).days for b in bookings
                if b.status in (BookingStatus.CONFIRMED, BookingStatus.COMPLETED)
            )
            occupancy_rate = min(100.0, (booked_days / total_capacity_days) * 100) if total_capacity_days > 0 else 0.0

        # Calculate monthly revenue
        monthly_revenue = await self._get_monthly_revenue(
            house_ids=house_ids if house_ids else None,
        )

        return OwnerDashboardResponse(
            total_bookings=total_bookings,
            total_revenue=float(total_revenue),
            occupancy_rate=occupancy_rate,
            active_bookings=active_bookings,
            monthly_revenue=monthly_revenue,
        )

    async def _get_monthly_revenue(
        self,
        house_ids: list[int] | None = None,
        months: int = 6,
    ) -> List[MonthlyRevenue]:
        """Calculate monthly revenue for the last N months.

        Args:
            house_ids: Optional list of house IDs to filter by
            months: Number of months to include

        Returns:
            List of monthly revenue data
        """
        # Get date range
        end_date = date.today()
        start_date = end_date - timedelta(days=30 * months)

        # Query for monthly aggregation
        query = (
            select(
                func.date_trunc('month', Booking.check_in).label('month'),
                func.sum(Booking.total_amount).label('revenue'),
            )
            .where(
                Booking.check_in >= start_date,
                Booking.status == BookingStatus.COMPLETED,
            )
        )

        # Apply house filter if provided
        if house_ids is not None:
            query = query.where(Booking.house_id.in_(house_ids))

        query = query.group_by('month').order_by('month')

        result = await self._db.execute(query)
        rows = result.all()

        return [
            MonthlyRevenue(
                month=row[0].strftime('%Y-%m') if row[0] else '',
                revenue=float(row[1] or 0),
            )
            for row in rows
        ]

    async def get_leaderboard(self) -> LeaderboardResponse:
        """Get leaderboard statistics.

        Returns:
            Leaderboard data with bookings by month and revenue by house
        """
        # Bookings by month (last 6 months)
        end_date = date.today()
        start_date = end_date - timedelta(days=180)

        bookings_query = (
            select(
                func.date_trunc('month', Booking.check_in).label('month'),
                func.count().label('count'),
            )
            .where(
                Booking.check_in >= start_date,
                Booking.status != BookingStatus.CANCELLED,
            )
            .group_by('month')
            .order_by('month')
        )

        bookings_result = await self._db.execute(bookings_query)
        bookings_by_month = [
            BookingsByMonth(
                month=row[0].strftime('%Y-%m') if row[0] else '',
                count=row[1],
            )
            for row in bookings_result.all()
        ]

        # Revenue by house
        revenue_query = (
            select(
                House.id,
                House.name,
                func.sum(Booking.total_amount).label('revenue'),
            )
            .join(Booking, House.id == Booking.house_id)
            .where(Booking.status == BookingStatus.COMPLETED)
            .group_by(House.id, House.name)
        )

        revenue_result = await self._db.execute(revenue_query)
        revenue_by_house = [
            RevenueByHouse(
                house_id=row[0],
                house_name=row[1],
                revenue=float(row[2] or 0),
            )
            for row in revenue_result.all()
        ]

        return LeaderboardResponse(
            bookings_by_month=bookings_by_month,
            revenue_by_house=revenue_by_house,
        )

    async def get_house_stats(
        self,
        house_id: int,
        period: str = "30d",
    ) -> HouseStatsResponse:
        """Get statistics for a specific house.

        Args:
            house_id: House identifier
            period: Time period (e.g., "30d", "90d", "1y")

        Returns:
            House statistics

        Raises:
            HouseNotFoundError: If house not found
        """
        # Verify house exists
        house = await self._house_repo.get(house_id)
        if not house:
            raise HouseNotFoundError(house_id)

        # Parse period
        days = 30
        if period.endswith('d'):
            days = int(period[:-1])
        elif period.endswith('y'):
            days = int(period[:-1]) * 365

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Get bookings for house in period
        bookings_query = (
            select(Booking)
            .where(
                Booking.house_id == house_id,
                Booking.check_in >= start_date,
                Booking.status != BookingStatus.CANCELLED,
            )
        )

        result = await self._db.execute(bookings_query)
        bookings = result.scalars().all()

        # Calculate stats
        total_bookings = len(bookings)
        total_revenue = sum(
            (b.total_amount or 0) for b in bookings if b.status == BookingStatus.COMPLETED
        )

        # Calculate occupancy rate
        booked_days = sum(
            (b.check_out - b.check_in).days for b in bookings
        )
        total_days = days * house.capacity  # Simplified calculation
        occupancy_rate = min(100.0, (booked_days / total_days) * 100) if total_days > 0 else 0.0

        return HouseStatsResponse(
            occupancy_rate=occupancy_rate,
            total_revenue=float(total_revenue),
            total_bookings=total_bookings,
        )
