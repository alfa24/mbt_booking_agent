from fastapi import APIRouter

from backend.api.health import health_router
from backend.api.bookings import bookings_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(bookings_router)
