"""Rate limiting middleware using Redis."""

import time
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as aioredis

from app.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app):
        super().__init__(app)
        self.redis = None
    
    async def get_redis(self):
        """Get or create Redis connection."""
        if self.redis is None:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return self.redis
    
    async def dispatch(self, request: Request, call_next):
        """Process request and apply rate limiting."""
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json", "/metrics"]:
            return await call_next(request)
        
        # Get client identifier (API key or IP)
        api_key = request.headers.get("X-API-Key")
        client_id = api_key if api_key else request.client.host
        
        try:
            redis = await self.get_redis()
            
            # Check per-minute rate limit
            minute_key = f"rate_limit:{client_id}:minute:{int(time.time() // 60)}"
            minute_count = await redis.incr(minute_key)
            
            if minute_count == 1:
                await redis.expire(minute_key, 60)
            
            if minute_count > settings.RATE_LIMIT_PER_MINUTE:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Please try again later."
                )
            
            response = await call_next(request)
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_MINUTE)
            response.headers["X-RateLimit-Remaining"] = str(
                max(0, settings.RATE_LIMIT_PER_MINUTE - minute_count)
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            # If Redis fails, allow the request but log error
            print(f"Rate limiting error: {e}")
            return await call_next(request)
