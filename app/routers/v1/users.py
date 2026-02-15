"""User management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserUpdate
from app.core.dependencies import get_current_active_user
from app.core.security import hash_password


router = APIRouter(prefix="/users")


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user information."""
    if user_update.email is not None:
        current_user.email = user_update.email
    
    if user_update.password is not None:
        current_user.hashed_password = hash_password(user_update.password)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user
