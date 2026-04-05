"""Query API endpoints for natural language to SQL."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.dependencies import get_llm_service
from backend.schemas.common import ErrorResponse
from backend.schemas.query import (
    NaturalLanguageQueryRequest,
    NaturalLanguageQueryResponse,
)
from backend.services.llm import LLMService
from backend.services.text_to_sql import TextToSQLService

logger = logging.getLogger(__name__)

query_router = APIRouter(prefix="/query", tags=["query"])


def get_text_to_sql_service(llm_service: Annotated[LLMService, Depends(get_llm_service)]) -> TextToSQLService:
    """Dependency provider for TextToSQL service.

    Args:
        llm_service: LLM service instance

    Returns:
        TextToSQLService instance
    """
    return TextToSQLService(client=llm_service.client)


@query_router.post(
    "/natural-language",
    response_model=NaturalLanguageQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Natural language query",
    description="Convert natural language question to SQL and execute it.",
    responses={
        200: {"description": "Query executed successfully"},
        400: {
            "description": "Invalid or unsafe query",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def natural_language_query(
    request: NaturalLanguageQueryRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[TextToSQLService, Depends(get_text_to_sql_service)],
) -> dict[str, Any]:
    """Execute natural language query.

    Args:
        request: Query request with natural language question
        session: Database session
        service: Text-to-SQL service instance

    Returns:
        Query results with SQL, data, columns, and explanation

    Raises:
        HTTPException: 400 if query is unsafe or fails
    """
    try:
        result = await service.execute_query(session, request.question)
        return result
    except ValueError as e:
        logger.warning("Invalid query request: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query is invalid or unsafe",
        ) from e
    except Exception as e:
        logger.exception("Unhandled error in natural_language_query")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while executing query",
        ) from e
