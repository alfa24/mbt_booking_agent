"""Schemas for natural language query API."""

from typing import Any

from pydantic import BaseModel, Field


class NaturalLanguageQueryRequest(BaseModel):
    """Request schema for natural language to SQL query."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Natural language question about the data",
        examples=["Сколько бронирований в этом месяце?"],
    )


class NaturalLanguageQueryResponse(BaseModel):
    """Response schema for natural language query results."""

    sql: str = Field(
        ...,
        description="Generated SQL query",
        examples=["SELECT COUNT(*) FROM bookings WHERE created_at >= '2024-01-01'"],
    )
    results: list[dict[str, Any]] = Field(
        ...,
        description="Query results as list of dictionaries",
        default_factory=list,
    )
    columns: list[str] = Field(
        ...,
        description="Column names from the query result",
        default_factory=list,
    )
    explanation: str = Field(
        ...,
        description="Human-readable explanation of the results",
        examples=["В этом месяце было сделано 15 бронирований."],
    )
