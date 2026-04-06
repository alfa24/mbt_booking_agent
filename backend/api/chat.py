"""Chat API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, File, HTTPException, UploadFile, status

from backend.schemas.chat import (
    AudioTranscriptionResponse,
    ChatMessagesListResponse,
    ChatResponse,
    CreateChatRequest,
    SendMessageRequest,
    SendMessageResponse,
)
from backend.schemas.common import ErrorResponse
from backend.services.chat import ChatService
from backend.services.llm import LLMService

chat_router = APIRouter(prefix="/chats", tags=["chats"])


@chat_router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create chat",
    description="Create a new chat conversation.",
    responses={
        201: {"description": "Chat created successfully"},
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
async def create_chat(
    request: CreateChatRequest,
    service: Annotated[ChatService, Depends(ChatService)],
) -> ChatResponse:
    """Create a new chat.

    Args:
        request: Chat creation data
        service: Chat service instance

    Returns:
        Created chat with generated ID

    Raises:
        HTTPException: 404 if user not found, 422 if validation fails
    """
    return await service.create_chat(user_id=request.user_id)


@chat_router.get(
    "/{chat_id}/messages",
    response_model=ChatMessagesListResponse,
    summary="Get chat messages",
    description="Get messages for a chat with cursor-based pagination.",
    responses={
        200: {"description": "Messages returned successfully"},
        404: {
            "description": "Chat not found",
            "model": ErrorResponse,
        },
    },
)
async def get_messages(
    chat_id: int,
    service: Annotated[ChatService, Depends(ChatService)],
    user_id: int = Cookie(default=1, alias="user_id"),
    cursor: str | None = None,
    limit: int = 50,
) -> ChatMessagesListResponse:
    """Get messages for a chat.

    Args:
        chat_id: Chat identifier
        service: Chat service instance
        user_id: User identifier (from auth)
        cursor: Cursor for pagination
        limit: Number of messages to return

    Returns:
        Paginated list of messages

    Raises:
        HTTPException: 404 if chat not found
    """
    try:
        return await service.get_messages(
            chat_id=chat_id,
            user_id=user_id,
            cursor=cursor,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@chat_router.post(
    "/{chat_id}/messages",
    response_model=SendMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send message",
    description="Send a message to the chat and get LLM response.",
    responses={
        201: {"description": "Message sent successfully"},
        404: {
            "description": "Chat not found",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def send_message(
    chat_id: int,
    request: SendMessageRequest,
    service: Annotated[ChatService, Depends(ChatService)],
    user_id: int = Cookie(default=1, alias="user_id"),
    context: str = "",
) -> SendMessageResponse:
    """Send a message to the chat.

    Args:
        chat_id: Chat identifier
        request: Message data
        service: Chat service instance
        user_id: User identifier (from auth)
        context: Additional context about bookings

    Returns:
        Assistant response message

    Raises:
        HTTPException: 404 if chat not found, 422 if validation fails
    """
    try:
        message = await service.send_message(
            chat_id=chat_id,
            content=request.content,
            user_id=user_id,
            context=context,
        )
        return SendMessageResponse(message=message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@chat_router.post(
    "/transcribe",
    response_model=AudioTranscriptionResponse,
    status_code=status.HTTP_200_OK,
    summary="Transcribe audio",
    description="Transcribe audio file to text using Whisper API.",
    responses={
        200: {"description": "Transcription successful"},
        400: {
            "description": "Invalid audio file",
            "model": ErrorResponse,
        },
        422: {
            "description": "Invalid input data",
            "model": ErrorResponse,
        },
    },
)
async def transcribe_audio(
    audio: Annotated[UploadFile, File(description="Audio file to transcribe (webm, mp3, wav)")],
) -> AudioTranscriptionResponse:
    """Transcribe audio file to text.

    Args:
        audio: Audio file uploaded by the user

    Returns:
        Transcription response with text

    Raises:
        HTTPException: 400 if audio file is invalid
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Debug logging
    logger.info(f"[Transcribe] Received file: name={audio.filename}, content_type={audio.content_type}, size={audio.size if hasattr(audio, 'size') else 'unknown'}")
    
    # Validate file type
    allowed_types = {"audio/webm", "audio/mp3", "audio/wav", "audio/mpeg", "audio/ogg"}
    if audio.content_type not in allowed_types:
        logger.error(f"[Transcribe] Invalid content type: {audio.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid audio format. Allowed: {', '.join(allowed_types)}",
        )

    try:
        # Read audio bytes
        audio_bytes = await audio.read()
        logger.info(f"[Transcribe] Read {len(audio_bytes)} bytes")

        if len(audio_bytes) == 0:
            logger.error("[Transcribe] Empty audio file")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty audio file",
            )

        # Transcribe using LLM service
        llm_service = LLMService()
        transcription = await llm_service.transcribe_audio(
            audio_bytes=audio_bytes,
            filename=audio.filename or "audio.webm",
        )

        if not transcription:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Transcription failed",
            )

        return AudioTranscriptionResponse(text=transcription)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription error: {str(e)}",
        )
