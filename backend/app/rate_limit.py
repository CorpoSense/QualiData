"""Rate limiting middleware."""

import time
from typing import Dict
from fastapi import HTTPException, Request


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests: Dict[int, list] = {}
        self.provider_limits = {
            "openai": {"requests_per_minute": 60, "tokens_per_minute": 90000},
            "anthropic": {"requests_per_minute": 50, "tokens_per_minute": 100000},
            "google": {"requests_per_minute": 60, "tokens_per_minute": 50000},
            "groq": {"requests_per_minute": 30, "tokens_per_minute": 6000},
            "deepseek": {"requests_per_minute": 60, "tokens_per_minute": 120000},
        }
    
    def check_rate_limit(self, user_id: int, provider: str = "openai") -> bool:
        """Check if user has exceeded rate limit."""
        now = time.time()
        minute_ago = now - 60
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Clean old requests
        self.requests[user_id] = [
            t for t in self.requests[user_id] if t > minute_ago
        ]
        
        # Check limit
        limit = self.provider_limits.get(provider, {}).get("requests_per_minute", 60)
        
        if len(self.requests[user_id]) >= limit:
            return False
        
        # Add current request
        self.requests[user_id].append(now)
        return True
    
    def get_remaining(self, user_id: int, provider: str = "openai") -> int:
        """Get remaining requests for user."""
        now = time.time()
        minute_ago = now - 60
        
        if user_id not in self.requests:
            return self.provider_limits.get(provider, {}).get("requests_per_minute", 60)
        
        recent = [t for t in self.requests[user_id] if t > minute_ago]
        limit = self.provider_limits.get(provider, {}).get("requests_per_minute", 60)
        
        return max(0, limit - len(recent))


# Global rate limiter
rate_limiter = RateLimiter()


def check_rate_limit(user_id: int, provider: str = "openai"):
    """Dependency for rate limiting."""
    if not rate_limiter.check_rate_limit(user_id, provider):
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "provider": provider,
                "retry_after": "60 seconds"
            }
        )


def get_rate_limit_info(user_id: int, provider: str = "openai") -> dict:
    """Get rate limit information."""
    return {
        "provider": provider,
        "remaining": rate_limiter.get_remaining(user_id, provider),
        "limit": rate_limiter.provider_limits.get(provider, {}).get("requests_per_minute", 60)
    }
