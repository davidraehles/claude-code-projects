"""
Shared dependencies for API endpoints.

Provides reusable dependencies for database sessions, authentication, etc.
"""

from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db


# Database session dependency (already defined in database.py, re-exported here)
def get_database() -> Generator[Session, None, None]:
    """
    Get database session for API endpoints.

    Yields:
        Session: SQLAlchemy database session
    """
    yield from get_db()


# Security scheme for JWT authentication
security = HTTPBearer()


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
    # TODO: Implement JWT token validation
    # For now, return a placeholder user ID for development
    # In production, this should:
    # 1. Decode JWT token
    # 2. Verify signature
    # 3. Check expiration
    # 4. Verify user exists in database
    # 5. Return user_id from token payload

    # Placeholder implementation:
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # For development, accept any token and return user_id=1
    # Replace this with actual JWT validation
    return 1


async def get_optional_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int | None:
    """
    Extract user ID from JWT token if present, otherwise return None.

    Used for endpoints that work with or without authentication.

    Args:
        credentials: HTTP Bearer token from Authorization header (optional)

    Returns:
        int | None: User ID if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        # TODO: Implement JWT token validation (same as get_current_user_id)
        return 1  # Placeholder
    except Exception:
        return None
