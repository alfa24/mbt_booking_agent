import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.api import api_router
from backend.exceptions import (
    BookingAlreadyCancelledError,
    BookingException,
    BookingNotFoundError,
    BookingPermissionError,
    DateConflictError,
    HouseNotFoundError,
    InvalidBookingStatusError,
    TariffNotFoundError,
    UserNotFoundError,
)
from backend.schemas.common import ErrorResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting up Booking API...")
    # TODO: Initialize database connection here
    yield
    logger.info("Shutting down Booking API...")
    # TODO: Close database connection here


app = FastAPI(
    title="Booking API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Booking domain exception handlers
@app.exception_handler(BookingNotFoundError)
async def booking_not_found_handler(request: Request, exc: BookingNotFoundError):
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="not_found",
            message=exc.message,
        ).model_dump(),
    )


@app.exception_handler(DateConflictError)
async def date_conflict_handler(request: Request, exc: DateConflictError):
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error="date_conflict",
            message=exc.message,
        ).model_dump(),
    )


@app.exception_handler(BookingPermissionError)
async def permission_error_handler(request: Request, exc: BookingPermissionError):
    return JSONResponse(
        status_code=403,
        content=ErrorResponse(
            error="forbidden",
            message=exc.message,
        ).model_dump(),
    )


@app.exception_handler(InvalidBookingStatusError)
async def invalid_status_handler(request: Request, exc: InvalidBookingStatusError):
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error="invalid_status",
            message=exc.message,
        ).model_dump(),
    )


@app.exception_handler(BookingAlreadyCancelledError)
async def already_cancelled_handler(request: Request, exc: BookingAlreadyCancelledError):
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error="already_cancelled",
            message=exc.message,
        ).model_dump(),
    )


@app.exception_handler(HouseNotFoundError)
async def house_not_found_handler(request: Request, exc: HouseNotFoundError):
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="not_found",
            message=exc.message,
        ).model_dump(),
    )


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="not_found",
            message=exc.message,
        ).model_dump(),
    )


@app.exception_handler(TariffNotFoundError)
async def tariff_not_found_handler(request: Request, exc: TariffNotFoundError):
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="not_found",
            message=exc.message,
        ).model_dump(),
    )


# Global exception handler (must be last)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception occurred")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="internal_error",
            message="An unexpected error occurred",
        ).model_dump(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
