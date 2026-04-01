from fastapi import APIRouter

health_router = APIRouter()


@health_router.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
