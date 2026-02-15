"""Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    role: Optional[str] = Field(default="user", description="User role: user, business, or admin")


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    quota_limit: Optional[int] = Field(None, ge=0)


class UserResponse(UserBase):
    """Schema for user response."""
    id: uuid.UUID
    role: str
    is_active: bool
    quota_limit: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserWithStats(UserResponse):
    """User response with usage statistics."""
    total_requests: int = 0
    requests_this_month: int = 0


# ============================================================================
# Authentication Schemas
# ============================================================================

class Token(BaseModel):
    """JWT token response with access and refresh tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=1800, description="Access token expiration in seconds")


class TokenData(BaseModel):
    """Token payload data."""
    user_id: Optional[uuid.UUID] = None
    email: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


# ============================================================================
# API Key Schemas
# ============================================================================

class APIKeyBase(BaseModel):
    """Base API key schema."""
    name: str = Field(..., min_length=1, max_length=100, description="Name for this API key")


class APIKeyCreate(APIKeyBase):
    """Schema for creating a new API key."""
    rate_limit: Optional[int] = Field(default=60, ge=1, le=1000, description="Requests per minute")
    expires_days: Optional[int] = Field(default=365, ge=1, le=3650, description="Days until expiration")


class APIKeyResponse(APIKeyBase):
    """Schema for API key response."""
    id: uuid.UUID
    is_active: bool
    rate_limit: int
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class APIKeyWithSecret(APIKeyResponse):
    """API key response with the plain text key (only returned on creation)."""
    key: str = Field(..., description="The actual API key - save this, it won't be shown again!")


# ============================================================================
# Usage Log Schemas
# ============================================================================

class UsageLogCreate(BaseModel):
    """Schema for creating a usage log."""
    endpoint: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    processing_time: Optional[float] = None
    status_code: int
    error_message: Optional[str] = None


class UsageLogResponse(UsageLogCreate):
    """Schema for usage log response."""
    id: int
    user_id: uuid.UUID
    api_key_id: Optional[uuid.UUID]
    tokens_used: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UsageStats(BaseModel):
    """Usage statistics schema."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_file_size: int
    average_processing_time: float
    requests_by_endpoint: dict[str, int]
    requests_by_file_type: dict[str, int]


# ============================================================================
# OCR Schemas
# ============================================================================

class OCRResponse(BaseModel):
    """Schema for OCR extraction response."""
    filename: str
    mime_type: str
    content: str
    file_size: Optional[int] = None
    processing_time: Optional[float] = None
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "document.pdf",
                "mime_type": "application/pdf",
                "content": "Extracted text from the document...",
                "file_size": 1024000,
                "processing_time": 2.5
            }
        }
    )


class OCRBatchRequest(BaseModel):
    """Schema for batch OCR processing request."""
    webhook_url: Optional[str] = Field(None, description="URL to receive results when processing completes")


class OCRBatchResponse(BaseModel):
    """Schema for batch OCR processing response."""
    job_id: str
    status: str
    message: str


class OCRJobStatus(BaseModel):
    """Schema for OCR job status response."""
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    total_files: int
    processed_files: int
    results: Optional[list[OCRResponse]] = None
    error: Optional[str] = None


# ============================================================================
# Health & Monitoring Schemas
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime


class HealthDetailResponse(HealthResponse):
    """Detailed health check response."""
    database: str
    redis: str
    celery: str


# ============================================================================
# Admin Schemas
# ============================================================================

class AdminUserUpdate(UserUpdate):
    """Admin schema for updating any user."""
    role: Optional[str] = None


class AdminUsageStats(BaseModel):
    """Admin usage statistics."""
    total_users: int
    active_users: int
    total_api_keys: int
    active_api_keys: int
    requests_today: int
    requests_this_month: int
    total_file_size_processed: int
    average_response_time: float
