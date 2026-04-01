"""Pydantic schemas for Booking resource."""

from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BookingStatus(str, Enum):
    """Booking status enum.

    - pending: Booking requested, awaiting confirmation
    - confirmed: Booking confirmed by owner
    - cancelled: Booking cancelled
    - completed: Stay completed, final calculation done
    """

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class GuestInfo(BaseModel):
    """Guest composition info for booking.

    Represents a group of guests of the same tariff type.
    """

    tariff_id: int = Field(..., ge=1, description="Tariff type ID")
    count: int = Field(..., ge=1, description="Number of guests of this type")


class BookingBase(BaseModel):
    """Base booking schema with common fields."""

    house_id: int = Field(..., ge=1, description="ID of the booked house")
    check_in: date = Field(..., description="Check-in date")
    check_out: date = Field(..., description="Check-out date")


class BookingResponse(BookingBase):
    """Booking response schema.

    Returned when fetching booking data.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique booking identifier")
    tenant_id: int = Field(..., description="ID of the tenant who made the booking")
    guests_planned: List[GuestInfo] = Field(
        ...,
        description="Planned guest composition",
    )
    guests_actual: Optional[List[GuestInfo]] = Field(
        None,
        description="Actual guest composition (filled after stay)",
    )
    total_amount: Optional[int] = Field(
        None,
        ge=0,
        description="Total amount in rubles (recalculated after stay)",
    )
    status: BookingStatus = Field(..., description="Current booking status")
    created_at: datetime = Field(..., description="Booking creation timestamp")


class CreateBookingRequest(BookingBase):
    """Request schema for creating a new booking.

    Used by tenants to request a booking.
    """

    guests: List[GuestInfo] = Field(
        ...,
        min_length=1,
        description="Guest composition (tariff_id + count)",
    )

    @model_validator(mode="after")
    def validate_dates(self):
        """Ensure check_in is before check_out."""
        if self.check_in >= self.check_out:
            raise ValueError("check_in must be before check_out")
        return self


class UpdateBookingRequest(BaseModel):
    """Request schema for updating a booking.

    All fields are optional - only provided fields will be updated.
    Used for modifying dates or guest composition before confirmation.
    """

    check_in: Optional[date] = None
    check_out: Optional[date] = None
    guests: Optional[List[GuestInfo]] = Field(None, min_length=1)
    status: Optional[BookingStatus] = None

    @model_validator(mode="after")
    def validate_dates(self):
        """Ensure check_in is before check_out if both provided."""
        if self.check_in and self.check_out and self.check_in >= self.check_out:
            raise ValueError("check_in must be before check_out")
        return self


class BookingFilterParams(BaseModel):
    """Query parameters for filtering bookings list.

    Used in GET /bookings endpoint.
    """

    # Pagination
    limit: int = Field(20, ge=1, le=100, description="Number of results to return")
    offset: int = Field(0, ge=0, description="Number of results to skip")

    # Sorting: field name, prefix with - for descending. Example: "check_in", "-created_at"
    sort: Optional[str] = Field(None, description="Sort field. Prefix with - for desc. Example: check_in, -created_at")

    # Filters
    user_id: Optional[int] = Field(None, description="Filter by tenant ID")
    house_id: Optional[int] = Field(None, description="Filter by house ID")
    status: Optional[BookingStatus] = Field(None, description="Filter by status")

    # Date range filters
    check_in_from: Optional[date] = Field(None, description="Check-in not earlier than")
    check_in_to: Optional[date] = Field(None, description="Check-in not later than")
    check_out_from: Optional[date] = Field(None, description="Check-out not earlier than")
    check_out_to: Optional[date] = Field(None, description="Check-out not later than")
