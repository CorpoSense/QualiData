from datetime import datetime

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "MasterDataCleaner API",
        "debug": settings.debug,
    }
