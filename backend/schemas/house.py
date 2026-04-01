"""Pydantic schemas for House resource."""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class HouseBase(BaseModel):
    """Base house schema with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="House name (e.g., 'Старый дом', 'Новый дом')",
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Detailed description of the house",
    )
    capacity: int = Field(
        ...,
        ge=1,
        description="Maximum number of guests",
    )
    is_active: bool = Field(
        default=True,
        description="Whether the house is available for booking",
    )


class HouseResponse(HouseBase):
    """House response schema.

    Returned when fetching house data.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique house identifier")
    owner_id: int = Field(..., description="ID of the house owner")
    created_at: datetime = Field(..., description="Creation timestamp")


class CreateHouseRequest(HouseBase):
    """Request schema for creating a new house.

    Used by landlords to add new properties.
    """

    pass


class UpdateHouseRequest(BaseModel):
    """Request schema for updating house information.

    All fields are optional - only provided fields will be updated.
    """

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    capacity: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class OccupiedDateRange(BaseModel):
    """Represents a date range when the house is occupied."""

    check_in: date = Field(..., description="Start of occupied period")
    check_out: date = Field(..., description="End of occupied period")
    booking_id: int = Field(..., description="ID of the booking occupying this period")


class HouseFilterParams(BaseModel):
    """Query parameters for filtering houses list.

    Used in GET /houses endpoint.
    """

    # Pagination
    limit: int = Field(20, ge=1, le=100, description="Number of results to return")
    offset: int = Field(0, ge=0, description="Number of results to skip")

    # Sorting: field name, prefix with - for descending. Example: "name", "-created_at"
    sort: Optional[str] = Field(None, description="Sort field. Prefix with - for desc. Example: name, -created_at")

    # Filters
    owner_id: Optional[int] = Field(None, description="Filter by owner ID")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    capacity_min: Optional[int] = Field(None, ge=1, description="Minimum capacity")
    capacity_max: Optional[int] = Field(None, ge=1, description="Maximum capacity")


class HouseCalendarResponse(BaseModel):
    """Response schema for house availability calendar.

    Shows all occupied date ranges for the house.
    """

    house_id: int = Field(..., description="House identifier")
    occupied_dates: List[OccupiedDateRange] = Field(
        default_factory=list,
        description="List of occupied date ranges",
    )
