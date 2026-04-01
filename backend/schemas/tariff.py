"""Pydantic schemas for Tariff resource."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TariffBase(BaseModel):
    """Base tariff schema with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Tariff name (e.g., 'Ребёнок', 'Взрослый', 'Постоянный гость')",
    )
    amount: int = Field(
        ...,
        ge=0,
        description="Price per night in rubles (0 for free)",
    )


class TariffResponse(TariffBase):
    """Tariff response schema.

    Returned when fetching tariff data.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique tariff identifier")
    created_at: datetime = Field(..., description="Creation timestamp")


class CreateTariffRequest(TariffBase):
    """Request schema for creating a new tariff.

    Used by landlords to define guest pricing tiers.
    """

    pass


class UpdateTariffRequest(BaseModel):
    """Request schema for updating a tariff.

    All fields are optional - only provided fields will be updated.
    """

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[int] = Field(None, ge=0)
