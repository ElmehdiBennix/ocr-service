"""Health check endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.database import get_db
from app.config import settings
from app.schemas import HealthResponse, HealthDetailResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow()
    }


@router.get("/health/details", response_model=HealthDetailResponse)
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check including dependencies."""
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check Redis
    try:
        redis = await aioredis.from_url(settings.REDIS_URL)
        await redis.ping()
        redis_status = "healthy"
        await redis.close()
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow(),
        "database": db_status,
        "redis": redis_status,
        "celery": "not implemented"
    }
