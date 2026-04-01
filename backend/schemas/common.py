"""Common Pydantic schemas shared across API."""

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field


class ValidationErrorDetail(BaseModel):
    """Detail of a single validation error."""

    field: Optional[str] = Field(None, description="Field that caused the error")
    msg: str = Field(..., description="Error message")
    type: Optional[str] = Field(None, description="Error type code")


class ErrorResponse(BaseModel):
    """Standard error response format.

    Used for all API error responses to ensure consistency.
    """

    error: str = Field(..., description="Error code (e.g., 'validation_error', 'not_found')")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[List[ValidationErrorDetail]] = Field(
        None,
        description="Detailed validation errors if applicable",
    )


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper.

    Used for list endpoints that support pagination.
    """

    items: List[T] = Field(..., description="List of items for current page")
    total: int = Field(..., ge=0, description="Total number of items")
    limit: int = Field(..., ge=1, description="Items per page")
    offset: int = Field(..., ge=0, description="Number of items skipped")
