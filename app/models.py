"""SQLAlchemy database models."""

import uuid
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String,
    Boolean,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    Text,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    USER = "user"
    BUSINESS = "business"
    ADMIN = "admin"


class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.USER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    quota_limit: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)  # requests per month
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    
    # Relationships
    api_keys: Mapped[list["APIKey"]] = relationship(
        "APIKey",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    usage_logs: Mapped[list["UsageLog"]] = relationship(
        "UsageLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"


class APIKey(Base):
    """API key model for API authentication."""
    
    __tablename__ = "api_keys"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    key_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rate_limit: Mapped[int] = mapped_column(Integer, default=60, nullable=False)  # requests per minute
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="api_keys")
    usage_logs: Mapped[list["UsageLog"]] = relationship(
        "UsageLog",
        back_populates="api_key",
        cascade="all, delete-orphan",
    )
    
    __table_args__ = (
        Index("idx_api_key_user_active", "user_id", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<APIKey {self.name} (user_id={self.user_id})>"


class UsageLog(Base):
    """Usage log model for tracking API usage."""
    
    __tablename__ = "usage_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    api_key_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("api_keys.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # bytes
    processing_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # seconds
    tokens_used: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="usage_logs")
    api_key: Mapped[Optional["APIKey"]] = relationship("APIKey", back_populates="usage_logs")
    
    __table_args__ = (
        Index("idx_usage_user_created", "user_id", "created_at"),
        Index("idx_usage_apikey_created", "api_key_id", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<UsageLog user_id={self.user_id} endpoint={self.endpoint}>"
