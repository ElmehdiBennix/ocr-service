"""Admin endpoints for user and system management."""

import uuid
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, APIKey, UsageLog, UserRole
from app.schemas import UserResponse, UserUpdate, AdminUsageStats
from app.core.dependencies import get_current_admin_user
from app.core.security import hash_password


router = APIRouter(prefix="/admin")


@router.get("/users", response_model=List[UserResponse])
async def list_all_users(
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """List all users (admin only)."""
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: uuid.UUID,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID (admin only)."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user (admin only)."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.password is not None:
        user.hashed_password = hash_password(user_update.password)
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    if user_update.quota_limit is not None:
        user.quota_limit = user_update.quota_limit
    
    await db.commit()
    await db.refresh(user)
    
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete user (admin only)."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting yourself
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    await db.delete(user)
    await db.commit()


@router.get("/stats", response_model=AdminUsageStats)
async def get_system_stats(
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get system-wide usage statistics (admin only)."""
    # User counts
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar()
    
    result = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = result.scalar()
    
    # API key counts
    result = await db.execute(select(func.count(APIKey.id)))
    total_api_keys = result.scalar()
    
    result = await db.execute(
        select(func.count(APIKey.id)).where(APIKey.is_active == True)
    )
    active_api_keys = result.scalar()
    
    # Usage logs
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    result = await db.execute(
        select(func.count(UsageLog.id)).where(UsageLog.created_at >= today)
    )
    requests_today = result.scalar()
    
    result = await db.execute(
        select(func.count(UsageLog.id)).where(UsageLog.created_at >= month_start)
    )
    requests_this_month = result.scalar()
    
    # File size and response time
    result = await db.execute(
        select(func.sum(UsageLog.file_size))
    )
    total_file_size_processed = result.scalar() or 0
    
    result = await db.execute(
        select(func.avg(UsageLog.processing_time))
    )
    average_response_time = result.scalar() or 0.0
    
    return AdminUsageStats(
        total_users=total_users,
        active_users=active_users,
        total_api_keys=total_api_keys,
        active_api_keys=active_api_keys,
        requests_today=requests_today,
        requests_this_month=requests_this_month,
        total_file_size_processed=total_file_size_processed,
        average_response_time=average_response_time
    )
