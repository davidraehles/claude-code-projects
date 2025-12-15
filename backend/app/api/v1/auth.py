"""
Authentication API endpoints.

Provides JWT-based authentication with login, registration, and token refresh.
"""

from datetime import datetime, timedelta
from typing import Optional
import logging
import os

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field
from passlib.hash import bcrypt
import jwt

from app.api.dependencies import get_database, SECRET_KEY, ALGORITHM
from app.database import get_db
from app.models.user import User
from app.utils.rate_limit import AuthRateLimiter
from app.schemas.error import ErrorResponse, ErrorType

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Auth-specific rate limiter instance
auth_limiter = AuthRateLimiter()


def _extract_client_ip_from_request(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    if request.client:
        return request.client.host
    return "unknown"

def _ensure_redis_limiter():
    """Ensure auth limiter has access to Redis client if available."""
    if auth_limiter.redis_client is None:
        try:
            from app.events.bus import get_event_bus
            bus = get_event_bus()
            if bus.redis_client:
                auth_limiter.redis_client = bus.redis_client
                auth_limiter.login_limiter.redis_client = bus.redis_client
                auth_limiter.register_limiter.redis_client = bus.redis_client
                auth_limiter.refresh_limiter.redis_client = bus.redis_client
        except Exception:
            pass

# JWT Configuration - imported from dependencies.py to ensure single source of truth
# SECRET_KEY and ALGORITHM are imported above
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


# Pydantic Schemas

class UserRegister(BaseModel):
    """Schema for user registration."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    country: str = Field(..., min_length=2, max_length=2, description="ISO country code (e.g., DE, US)")


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str


class UserResponse(BaseModel):
    """Schema for user profile response."""
    id: int
    email: str
    country: str
    subscription_tier: str
    created_at: datetime

    class Config:
        from_attributes = True


# Helper Functions

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Use explicit bcrypt configuration with variant 2b and 12 rounds
    return bcrypt.using(ident="2b", rounds=12).hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: Data to encode in the token

    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


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


# Authorization Dependencies

def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
) -> User:
    """
    Dependency for endpoints that require admin privileges (sync version).

    Args:
        credentials: JWT token from Authorization header
        db: Database session

    Returns:
        Admin user object

    Raises:
        HTTPException: If user is not authenticated or not admin
    """
    # Decode token
    payload = decode_token(credentials.credentials)

    # Verify token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    # Get user
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()

    if not user or user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check admin status
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    return user


async def require_admin_async(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency for async endpoints that require admin privileges.

    Args:
        credentials: JWT token from Authorization header
        db: Async database session

    Returns:
        Admin user object

    Raises:
        HTTPException: If user is not authenticated or not admin
    """
    # Decode token
    payload = decode_token(credentials.credentials)

    # Verify token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    # Get user
    user_id = int(payload.get("sub"))
    from sqlalchemy import select
    user = await db.get(User, user_id)

    if not user or user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check admin status
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    return user


# Authentication Endpoints

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_database),
    request: Request = None,
    response: Response = None
):
    """
    Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        JWT tokens for the new user

    Raises:
        HTTPException: If email already exists
    """
    _ensure_redis_limiter()
    
    # Check if user already exists (do this before consuming rate-limiter quota)
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        # Return 400 Bad Request without leaking tokens
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Rate limit check (per-IP) - only apply for actual registration attempts
    client_ip = _extract_client_ip_from_request(request)
    is_allowed, metadata = auth_limiter.check_register_limit(client_ip)
    if not is_allowed:
        retry_after = metadata.get("retry_after") or auth_limiter.register_limiter.window_seconds
        err = ErrorResponse(
            error_type=ErrorType.RATE_LIMIT,
            message="Too many registration attempts. Please try again later.",
            details={"limit": metadata.get("limit"), "remaining": 0, "reset_at": metadata.get("reset_at")},
            path=str(request.url.path),
            request_id=request.headers.get("X-Request-ID"),
        )
        return JSONResponse(
            status_code=429,
            content={**err.model_dump(mode="json"), "error": "Too many registration attempts"},
            headers={
                "X-RateLimit-Limit": str(metadata.get("limit")),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": metadata.get("reset_at"),
                "Retry-After": str(retry_after),
            }
        )

    # Attach rate limit headers to response
    if response is not None:
        response.headers["X-RateLimit-Limit"] = str(metadata.get("limit"))
        response.headers["X-RateLimit-Remaining"] = str(metadata.get("remaining"))
        response.headers["X-RateLimit-Reset"] = metadata.get("reset_at")

    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        country=user_data.country.upper(),
        subscription_tier="free",
        preferences={}
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Clear failed login attempts after creating the user for test isolation
    try:
        auth_limiter.clear_failed_logins(new_user.email)
    except Exception:
        pass


    # Generate tokens
    access_token = create_access_token({"sub": str(new_user.id)})
    refresh_token = create_refresh_token({"sub": str(new_user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_database),
    request: Request = None,
    response: Response = None
):
    """
    Login a user and return JWT tokens.

    Args:
        credentials: User login credentials
        db: Database session

    Returns:
        JWT tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    _ensure_redis_limiter()
    client_ip = _extract_client_ip_from_request(request)

    # Check if account is locked due to failed attempts
    locked, unlock_time = auth_limiter.is_account_locked(credentials.email)
    if locked:
        content = {"error": "Account temporarily locked", "unlock_at": unlock_time.isoformat()}
        return JSONResponse(
            status_code=403,
            content=content,
            headers={
                "X-RateLimit-Limit": str(auth_limiter.login_limiter.max_requests),
                "X-RateLimit-Remaining": str(auth_limiter.login_limiter.max_requests),
                "X-RateLimit-Reset": "",
            }
        )

    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user:
        # For non-existent users, enforce IP-based rate limiting to prevent abuse
        is_allowed, metadata = auth_limiter.check_login_limit(client_ip)
        if not is_allowed:
            err = ErrorResponse(
                error_type=ErrorType.RATE_LIMIT,
                message="Too many login attempts. Please try again later.",
                details={"limit": metadata.get("limit"), "remaining": 0, "reset_at": metadata.get("reset_at")},
                path=str(request.url.path),
                request_id=request.headers.get("X-Request-ID"),
            )
            return JSONResponse(
                status_code=429,
                content={**err.model_dump(mode="json"), "error": "Too many login attempts"},
                headers={
                    "X-RateLimit-Limit": str(metadata.get("limit")),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": metadata.get("reset_at"),
                    "Retry-After": str(metadata.get("retry_after")) if metadata.get("retry_after") else str(auth_limiter.login_limiter.window_seconds),
                }
            )

        # Record failed login attempt and include rate limit headers
        auth_limiter.record_failed_login(credentials.email, client_ip)
        # Surface rate-limit headers for consistency in responses
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={
                "WWW-Authenticate": "Bearer",
                "X-RateLimit-Limit": str(auth_limiter.login_limiter.max_requests),
                "X-RateLimit-Remaining": str(auth_limiter.login_limiter.max_requests),
            },
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        # For failed attempts on existing accounts, record the failure and do NOT apply IP-level blocking here
        auth_limiter.record_failed_login(credentials.email, client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={
                "WWW-Authenticate": "Bearer",
                "X-RateLimit-Limit": str(auth_limiter.login_limiter.max_requests),
                "X-RateLimit-Remaining": str(auth_limiter.login_limiter.max_requests),
            },
        )

    # Check if account is deleted
    if user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deleted"
        )

    # Successful login: clear failed attempts
    auth_limiter.clear_failed_logins(credentials.email)

    # Enforce IP-based login limit for successful logins (counts towards quota)
    is_allowed, metadata = auth_limiter.check_login_limit(client_ip)
    if not is_allowed:
        err = ErrorResponse(
            error_type=ErrorType.RATE_LIMIT,
            message="Too many login attempts. Please try again later.",
            details={"limit": metadata.get("limit"), "remaining": 0, "reset_at": metadata.get("reset_at")},
            path=str(request.url.path),
            request_id=request.headers.get("X-Request-ID"),
        )
        return JSONResponse(
            status_code=429,
            content={**err.model_dump(mode="json"), "error": "Too many login attempts"},
            headers={
                "X-RateLimit-Limit": str(metadata.get("limit")),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": metadata.get("reset_at"),
                "Retry-After": str(metadata.get("retry_after")) if metadata.get("retry_after") else str(auth_limiter.login_limiter.window_seconds),
            }
        )

    if response is not None:
        response.headers["X-RateLimit-Limit"] = str(metadata.get("limit"))
        response.headers["X-RateLimit-Remaining"] = str(metadata.get("remaining"))
        response.headers["X-RateLimit-Reset"] = metadata.get("reset_at")

    # Generate tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_database),
    request: Request = None,
    response: Response = None
):
    """
    Refresh an access token using a refresh token.

    Args:
        token_data: Refresh token
        db: Database session

    Returns:
        New JWT tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    _ensure_redis_limiter()
    
    # Decode refresh token
    payload = decode_token(token_data.refresh_token)

    # Verify token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    # Get user ID
    user_id = int(payload.get("sub"))

    # Per-user refresh rate limiting
    is_allowed, metadata = auth_limiter.check_refresh_limit(user_id)
    if not is_allowed:
        err = ErrorResponse(
            error_type=ErrorType.RATE_LIMIT,
            message="Too many token refresh attempts. Please try again later.",
            details={"limit": metadata.get("limit"), "remaining": 0, "reset_at": metadata.get("reset_at")},
            path=str(request.url.path),
            request_id=request.headers.get("X-Request-ID"),
        )
        return JSONResponse(
            status_code=429,
            content={**err.model_dump(mode="json"), "error": "Too many token refresh attempts"},
            headers={
                "X-RateLimit-Limit": str(metadata.get("limit")),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": metadata.get("reset_at"),
                "Retry-After": str(metadata.get("retry_after")) if metadata.get("retry_after") else str(auth_limiter.refresh_limiter.window_seconds),
            }
        )

    if response is not None:
        response.headers["X-RateLimit-Limit"] = str(metadata.get("limit"))
        response.headers["X-RateLimit-Remaining"] = str(metadata.get("remaining"))
        response.headers["X-RateLimit-Reset"] = metadata.get("reset_at")

    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Generate new tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
):
    """
    Get current authenticated user profile.

    Args:
        credentials: JWT token
        db: Database session

    Returns:
        User profile data
    """
    # Decode token
    payload = decode_token(credentials.credentials)

    # Verify token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    # Get user
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()

    if not user or user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        country=user.country,
        subscription_tier=user.subscription_tier,
        created_at=user.created_at.isoformat()
    )
