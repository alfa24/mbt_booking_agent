"""SQLAlchemy house repository."""

from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.house import House
from backend.schemas.house import HouseResponse


class HouseRepository:
    """SQLAlchemy repository for houses."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def create(
        self,
        name: str,
        description: str | None,
        capacity: int,
        is_active: bool,
        owner_id: int,
    ) -> HouseResponse:
        """Create a new house.

        Args:
            name: House name
            description: House description
            capacity: Maximum number of guests
            is_active: Whether the house is available for booking
            owner_id: ID of the house owner

        Returns:
            Created house response
        """
        house = House(
            name=name,
            description=description,
            capacity=capacity,
            is_active=is_active,
            owner_id=owner_id,
        )
        self._session.add(house)
        await self._session.flush()
        await self._session.refresh(house)
        return HouseResponse.model_validate(house)

    async def get(self, house_id: int) -> HouseResponse | None:
        """Get house by ID.

        Args:
            house_id: House identifier

        Returns:
            House if found, None otherwise
        """
        result = await self._session.execute(select(House).where(House.id == house_id))
        house = result.scalar_one_or_none()
        return HouseResponse.model_validate(house) if house else None

    async def get_all(
        self,
        owner_id: int | None = None,
        is_active: bool | None = None,
        capacity_min: int | None = None,
        capacity_max: int | None = None,
        limit: int = 20,
        offset: int = 0,
        sort: str | None = None,
    ) -> tuple[list[HouseResponse], int]:
        """Get all houses with optional filtering.

        Args:
            owner_id: Filter by owner ID
            is_active: Filter by active status
            capacity_min: Filter by minimum capacity
            capacity_max: Filter by maximum capacity
            limit: Number of results to return
            offset: Number of results to skip
            sort: Sort field (prefix with - for descending)

        Returns:
            Tuple of (filtered houses list, total count)
        """
        query = select(House)

        # Apply filters
        if owner_id is not None:
            query = query.where(House.owner_id == owner_id)
        if is_active is not None:
            query = query.where(House.is_active == is_active)
        if capacity_min is not None:
            query = query.where(House.capacity >= capacity_min)
        if capacity_max is not None:
            query = query.where(House.capacity <= capacity_max)

        # Get total count
        count_result = await self._session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar() or 0

        # Apply sorting
        if sort:
            reverse = sort.startswith("-")
            sort_field = sort[1:] if reverse else sort
            if hasattr(House, sort_field):
                order = (
                    getattr(House, sort_field).desc()
                    if reverse
                    else getattr(House, sort_field)
                )
                query = query.order_by(order)

        # Apply pagination
        query = query.offset(offset).limit(limit)

        result = await self._session.execute(query)
        houses = result.scalars().all()
        return [HouseResponse.model_validate(house) for house in houses], total

    async def update(
        self,
        house_id: int,
        name: str | None = None,
        description: str | None = None,
        capacity: int | None = None,
        is_active: bool | None = None,
    ) -> HouseResponse | None:
        """Update house fields.

        Args:
            house_id: House identifier
            name: New name (optional)
            description: New description (optional)
            capacity: New capacity (optional)
            is_active: New active status (optional)

        Returns:
            Updated house if found, None otherwise
        """
        result = await self._session.execute(select(House).where(House.id == house_id))
        house = result.scalar_one_or_none()
        if not house:
            return None

        if name is not None:
            house.name = name
        if description is not None:
            house.description = description
        if capacity is not None:
            house.capacity = capacity
        if is_active is not None:
            house.is_active = is_active

        await self._session.flush()
        await self._session.refresh(house)
        return HouseResponse.model_validate(house)

    async def delete(self, house_id: int) -> bool:
        """Delete house by ID.

        Args:
            house_id: House identifier

        Returns:
            True if deleted, False if not found
        """
        result = await self._session.execute(select(House).where(House.id == house_id))
        house = result.scalar_one_or_none()
        if not house:
            return False

        await self._session.delete(house)
        return True
