from fastapi import APIRouter

from backend.api.health import health_router
from backend.api.bookings import bookings_router
from backend.api.houses import houses_router
from backend.api.users import users_router
from backend.api.tariffs import tariffs_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(bookings_router)
api_router.include_router(houses_router)
api_router.include_router(users_router)
api_router.include_router(tariffs_router)
