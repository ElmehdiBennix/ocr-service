"""API key management endpoints."""

import uuid
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, APIKey, UsageLog
from app.schemas import APIKeyCreate, APIKeyResponse, APIKeyWithSecret, UsageStats
from app.core.dependencies import get_current_active_user
from app.core.security import generate_api_key, hash_api_key
from app.config import settings


router = APIRouter(prefix="/keys")


@router.post("/create", response_model=APIKeyWithSecret, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new API key."""
    # Generate API key
    plain_key = generate_api_key()
    
    # Calculate expiration
    expires_at = None
    if key_data.expires_days:
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_days)
    
    # Create API key record
    api_key = APIKey(
        key_hash=hash_api_key(plain_key),
        user_id=current_user.id,
        name=key_data.name,
        rate_limit=key_data.rate_limit or 60,
        expires_at=expires_at,
    )
    
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    
    # Return with plain key (only time it's shown!)
    return APIKeyWithSecret(
        id=api_key.id,
        name=api_key.name,
        is_active=api_key.is_active,
        rate_limit=api_key.rate_limit,
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
        last_used_at=api_key.last_used_at,
        key=plain_key
    )


@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all API keys for current user."""
    result = await db.execute(
        select(APIKey).where(APIKey.user_id == current_user.id)
    )
    api_keys = result.scalars().all()
    return api_keys


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an API key."""
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == key_id,
            APIKey.user_id == current_user.id
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    await db.delete(api_key)
    await db.commit()


@router.get("/{key_id}/usage", response_model=UsageStats)
async def get_api_key_usage(
    key_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get usage statistics for an API key."""
    # Verify ownership
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == key_id,
            APIKey.user_id == current_user.id
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Get usage logs
    result = await db.execute(
        select(UsageLog).where(UsageLog.api_key_id == key_id)
    )
    logs = result.scalars().all()
    
    # Calculate statistics
    total_requests = len(logs)
    successful_requests = sum(1 for log in logs if 200 <= log.status_code < 300)
    failed_requests = total_requests - successful_requests
    total_file_size = sum(log.file_size or 0 for log in logs)
    avg_processing_time = sum(log.processing_time or 0 for log in logs) / total_requests if total_requests > 0 else 0
    
    # Group by endpoint and file type
    requests_by_endpoint = {}
    requests_by_file_type = {}
    
    for log in logs:
        requests_by_endpoint[log.endpoint] = requests_by_endpoint.get(log.endpoint, 0) + 1
        if log.file_type:
            requests_by_file_type[log.file_type] = requests_by_file_type.get(log.file_type, 0) + 1
    
    return UsageStats(
        total_requests=total_requests,
        successful_requests=successful_requests,
        failed_requests=failed_requests,
        total_file_size=total_file_size,
        average_processing_time=avg_processing_time,
        requests_by_endpoint=requests_by_endpoint,
        requests_by_file_type=requests_by_file_type
    )
