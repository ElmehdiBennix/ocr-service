"""Security utilities for authentication and password hashing."""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from app.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_api_key() -> str:
    """Generate a secure random API key."""
    # Generate 32 bytes (256 bits) of random data and convert to hex
    return f"ocr_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify an API key against a hash."""
    return hash_api_key(plain_key) == hashed_key


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with signature verification.
    
    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string signed with SECRET_KEY
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    # JWT is signed with SECRET_KEY using HS256 algorithm to prevent tampering
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    # JWT is signed with SECRET_KEY using HS256 algorithm
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token with signature validation.
    
    Args:
        token: JWT token string
        
    Returns:
        Dictionary of decoded claims if valid, None otherwise
    """
    try:
        # Verify signature and decode - will raise exception if tampered
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Verify token type
        if payload.get("type") != "access":
            return None
            
        return payload
    except jwt.PyJWTError:
        return None


def verify_refresh_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT refresh token with signature validation.
    
    Args:
        token: JWT refresh token string
        
    Returns:
        Dictionary of decoded claims if valid, None otherwise
    """
    try:
        # Verify signature and decode - will raise exception if tampered
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            return None
            
        return payload
    except jwt.PyJWTError:
        return None
