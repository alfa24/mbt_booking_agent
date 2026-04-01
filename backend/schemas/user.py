"""Pydantic schemas for User resource."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserRole(str, Enum):
    """User roles in the system."""

    TENANT = "tenant"  # Арендатор
    OWNER = "owner"  # Арендодатель
    BOTH = "both"  # Обе роли


class UserBase(BaseModel):
    """Base user schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Display name")
    role: UserRole = Field(default=UserRole.TENANT, description="User role")


class UserResponse(UserBase):
    """User response schema.

    Returned when fetching user data.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique user identifier")
    telegram_id: Optional[str] = Field(None, description="Telegram ID for bot login")
    created_at: datetime = Field(..., description="Registration timestamp")


class CreateUserRequest(UserBase):
    """Request schema for creating a new user.

    Used when registering user from Telegram bot.
    """

    telegram_id: str = Field(..., min_length=1, description="Telegram ID")


class UpdateUserRequest(BaseModel):
    """Request schema for updating user profile.

    All fields are optional - only provided fields will be updated.
    """

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None


class UserFilterParams(BaseModel):
    """Query parameters for filtering users list.

    Used in GET /users endpoint.
    """

    # Pagination
    limit: int = Field(20, ge=1, le=100, description="Number of results to return")
    offset: int = Field(0, ge=0, description="Number of results to skip")

    # Sorting: field name, prefix with - for descending. Example: "created_at", "-created_at"
    sort: Optional[str] = Field(None, description="Sort field. Prefix with - for desc. Example: created_at, -created_at")

    # Filters
    role: Optional[UserRole] = Field(None, description="Filter by role")
