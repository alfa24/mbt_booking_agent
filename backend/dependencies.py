"""Dependency injection providers for FastAPI."""

from backend.services.llm import LLMService


def get_llm_service() -> LLMService:
    """Dependency provider for LLM service.

    Returns:
        LLMService instance with default configuration
    """
    return LLMService()
