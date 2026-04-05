"""Pydantic schemas for ConsumableNote resource."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CreateConsumableNoteRequest(BaseModel):
    """Request schema for creating a new consumable note."""

    house_id: int = Field(..., ge=1, description="ID of the house")
    name: str = Field(..., min_length=1, max_length=100, description="Consumable name")
    comment: Optional[str] = Field(None, description="Optional comment")
    created_by: int = Field(..., ge=1, description="ID of the user creating the note")


class UpdateConsumableNoteRequest(BaseModel):
    """Request schema for updating a consumable note."""

    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Consumable name")
    comment: Optional[str] = Field(None, description="Optional comment")


class ConsumableNoteResponse(BaseModel):
    """Consumable note response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique note identifier")
    house_id: int = Field(..., description="ID of the house")
    created_by: int = Field(..., description="ID of the user who created the note")
    name: str = Field(..., description="Consumable name")
    comment: Optional[str] = Field(None, description="Optional comment")
    created_at: datetime = Field(..., description="Creation timestamp")
