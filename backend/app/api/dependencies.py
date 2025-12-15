"""
Shared dependencies for API endpoints.

Provides reusable dependencies for database sessions, authentication, etc.
"""

import os
import secrets
import logging
from typing import Generator, AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.database import get_db, get_async_db
from app.models.user import User

logger = logging.getLogger(__name__)


def get_jwt_secret_key() -> str:
    """
    Get JWT secret key with fail-secure pattern.

    In production, requires JWT_SECRET_KEY env var (fails if missing).
    In development, generates random key with warning.

    Returns:
        str: JWT secret key

    Raises:
        ValueError: In production if JWT_SECRET_KEY env var not set
    """
    secret = os.getenv("JWT_SECRET_KEY")
    if not secret:
        app_env = os.getenv("APP_ENV", "development")
        if app_env == "production":
            raise ValueError(
                "JWT_SECRET_KEY environment variable is required in production. "
                "Generate a secure key with: python -c 'import secrets; "
                "print(secrets.token_urlsafe(32))'"
            )
        # Development: generate random key
        secret = secrets.token_urlsafe(32)
        logger.warning(
            "JWT_SECRET_KEY not set. Using randomly generated key for development. "
            "Set JWT_SECRET_KEY environment variable for production."
        )
    return secret


# JWT Configuration
SECRET_KEY = get_jwt_secret_key()
ALGORITHM = "HS256"


# Database session dependency (already defined in database.py, re-exported here)
def get_database() -> Generator[Session, None, None]:
    """
    Get database session for API endpoints.

    Yields:
        Session: SQLAlchemy database session
    """
    yield from get_db()


async def get_async_database() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session for API endpoints.

    Yields:
        AsyncSession: SQLAlchemy async database session
    """
    async for session in get_async_db():
        yield session


# Security scheme for JWT authentication
security = HTTPBearer()


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.PyJWTError, jwt.InvalidTokenError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
) -> int:
    """
    Extract and validate user ID from JWT token.

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session

    Returns:
        int: User ID from validated token

    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Decode and validate token
    payload = decode_token(credentials.credentials)

    # Verify token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user ID from token
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user exists and is not deleted
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_database)
) -> int | None:
    """
    Extract user ID from JWT token if present, otherwise return None.

    Used for endpoints that work with or without authentication.

    Args:
        credentials: HTTP Bearer token from Authorization header (optional)
        db: Database session

    Returns:
        int | None: User ID if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        return await get_current_user_id(credentials, db)
    except HTTPException:
        return None
