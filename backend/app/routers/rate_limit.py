"""Rate limit API routes."""

from fastapi import APIRouter, Depends

from app.db.models import User
from app.rate_limit import rate_limiter
from app.routers.auth import get_current_active_user

router = APIRouter(prefix="/rate-limit", tags=["rate-limit"])


@router.get("/status")
async def get_rate_limit_status(current_user: User = Depends(get_current_active_user)):
    """Get rate limit status for all providers."""
    providers = {}

    for provider in ["openai", "anthropic", "google", "groq", "deepseek"]:
        providers[provider] = {
            "name": provider.capitalize(),
            "remaining": rate_limiter.get_remaining(current_user.id, provider),
            "limit": rate_limiter.provider_limits.get(provider, {}).get(
                "requests_per_minute", 60
            ),
            "resetsAt": None,  # Would calculate actual reset time in production
        }

    return {"providers": providers}


@router.get("/status/{provider}")
async def get_provider_rate_limit(
    provider: str, current_user: User = Depends(get_current_active_user)
):
    """Get rate limit status for a specific provider."""
    return {
        "provider": provider,
        "remaining": rate_limiter.get_remaining(current_user.id, provider),
        "limit": rate_limiter.provider_limits.get(provider, {}).get(
            "requests_per_minute", 60
        ),
    }
