"""Consumable notes API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.schemas.common import ErrorResponse, PaginatedResponse
from backend.schemas.consumable_note import (
    ConsumableNoteResponse,
    CreateConsumableNoteRequest,
    UpdateConsumableNoteRequest,
)
from backend.services.consumable_note import ConsumableNoteService

consumable_notes_router = APIRouter(prefix="/consumable-notes", tags=["consumable-notes"])


@consumable_notes_router.get(
    "",
    response_model=PaginatedResponse[ConsumableNoteResponse],
    summary="List consumable notes",
    description="Get list of consumable notes with optional filtering.",
    responses={
        200: {"description": "List of notes returned successfully"},
    },
)
async def list_notes(
    service: Annotated[ConsumableNoteService, Depends(ConsumableNoteService)],
    house_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
) -> PaginatedResponse[ConsumableNoteResponse]:
    """List all consumable notes with optional filtering.

    Args:
        service: Consumable note service instance
        house_id: Filter by house ID
        limit: Number of results to return
        offset: Number of results to skip

    Returns:
        Paginated list of notes
    """
    notes, total = await service.list_notes(
        house_id=house_id,
        limit=limit,
        offset=offset,
    )
    return PaginatedResponse(
        items=notes,
        total=total,
        limit=limit,
        offset=offset,
    )


@consumable_notes_router.post(
    "",
    response_model=ConsumableNoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create consumable note",
    description="Create a new consumable note for a house.",
    responses={
        201: {"description": "Note created successfully"},
        404: {
            "description": "House or user not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def create_note(
    request: CreateConsumableNoteRequest,
    service: Annotated[ConsumableNoteService, Depends(ConsumableNoteService)],
) -> ConsumableNoteResponse:
    """Create a new consumable note.

    Args:
        request: Note creation data
        service: Consumable note service instance

    Returns:
        Created note with generated ID

    Raises:
        HTTPException: 404 if house or user not found, 422 if validation fails
    """
    return await service.create_note(request)


@consumable_notes_router.patch(
    "/{note_id}",
    response_model=ConsumableNoteResponse,
    summary="Update consumable note",
    description="Update consumable note information (partial update).",
    responses={
        200: {"description": "Note updated successfully"},
        404: {
            "description": "Note not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def update_note(
    note_id: int,
    request: UpdateConsumableNoteRequest,
    service: Annotated[ConsumableNoteService, Depends(ConsumableNoteService)],
) -> ConsumableNoteResponse:
    """Update an existing consumable note.

    Only provided fields will be updated.

    Args:
        note_id: Note identifier
        request: Fields to update
        service: Consumable note service instance

    Returns:
        Updated note

    Raises:
        HTTPException: 404 if not found, 422 if validation fails
    """
    try:
        return await service.update_note(note_id, request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@consumable_notes_router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete consumable note",
    description="Delete a consumable note.",
    responses={
        204: {"description": "Note deleted successfully"},
        404: {
            "description": "Note not found",
            "model": ErrorResponse,
        },
    },
)
async def delete_note(
    note_id: int,
    service: Annotated[ConsumableNoteService, Depends(ConsumableNoteService)],
) -> None:
    """Delete a consumable note.

    Args:
        note_id: Note identifier
        service: Consumable note service instance

    Raises:
        HTTPException: 404 if note not found
    """
    try:
        await service.delete_note(note_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
