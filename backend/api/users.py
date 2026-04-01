"""User API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from backend.schemas.common import ErrorResponse, PaginatedResponse
from backend.schemas.user import (
    CreateUserRequest,
    UpdateUserRequest,
    UserFilterParams,
    UserResponse,
)
from backend.services.user import UserService

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    summary="List users",
    description="Get list of users with optional filtering and pagination.",
    responses={
        200: {"description": "List of users returned successfully"},
    },
)
async def list_users(
    filters: Annotated[UserFilterParams, Depends()],
    service: Annotated[UserService, Depends(UserService)],
) -> PaginatedResponse[UserResponse]:
    """List all users with filtering.

    Supports filtering by role.
    Results are paginated using limit/offset.

    Args:
        filters: Query parameters for filtering and pagination
        service: User service instance

    Returns:
        Paginated list of users
    """
    users, total = await service.list_users(filters)
    return PaginatedResponse(
        items=users,
        total=total,
        limit=filters.limit,
        offset=filters.offset,
    )


@users_router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve detailed information about a specific user.",
    responses={
        200: {"description": "User found and returned"},
        404: {
            "description": "User not found",
            "model": ErrorResponse,
        },
    },
)
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(UserService)],
) -> UserResponse:
    """Get a single user by their ID.

    Args:
        user_id: Unique user identifier
        service: User service instance

    Returns:
        User details

    Raises:
        HTTPException: 404 if user not found
    """
    return await service.get_user(user_id)


@users_router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Create a new user (typically from Telegram bot).",
    responses={
        201: {"description": "User created successfully"},
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def create_user(
    request: CreateUserRequest,
    service: Annotated[UserService, Depends(UserService)],
) -> UserResponse:
    """Create a new user.

    Args:
        request: User creation data
        service: User service instance

    Returns:
        Created user with generated ID

    Raises:
        HTTPException: 422 if validation fails
    """
    return await service.create_user(request)


@users_router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Replace user",
    description="Replace all user profile information (full update).",
    responses={
        200: {"description": "User updated successfully"},
        404: {
            "description": "User not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def replace_user(
    user_id: int,
    request: CreateUserRequest,
    service: Annotated[UserService, Depends(UserService)],
) -> UserResponse:
    """Replace user profile (full update).

    Args:
        user_id: User identifier
        request: Complete user data
        service: User service instance

    Returns:
        Updated user

    Raises:
        HTTPException: 404 if user not found, 422 if validation fails
    """
    return await service.replace_user(user_id, request)


@users_router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update user profile (partial update).",
    responses={
        200: {"description": "User updated successfully"},
        404: {
            "description": "User not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def update_user(
    user_id: int,
    request: UpdateUserRequest,
    service: Annotated[UserService, Depends(UserService)],
) -> UserResponse:
    """Update an existing user.

    Only provided fields will be updated.

    Args:
        user_id: User identifier
        request: Fields to update
        service: User service instance

    Returns:
        Updated user

    Raises:
        HTTPException: 404 if not found, 422 if validation fails
    """
    return await service.update_user(user_id, request)


@users_router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user account.",
    responses={
        204: {"description": "User deleted successfully"},
        404: {
            "description": "User not found",
            "model": ErrorResponse,
        },
    },
)
async def delete_user(
    user_id: int,
    service: Annotated[UserService, Depends(UserService)],
) -> None:
    """Delete a user.

    Args:
        user_id: User identifier
        service: User service instance

    Raises:
        HTTPException: 404 if user not found
    """
    await service.delete_user(user_id)
