"""
Admin API endpoints for managing rate limiting policies.

Provides CRUD operations for rate limit policies, user overrides,
and whitelist management. All endpoints require admin authentication.
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.rate_limit import RateLimitPolicy, RateLimitOverride, RateLimitWhitelist
from app.config.rate_limit_config import rate_limit_config, LimitType
from app.api.v1.auth import require_admin_async, require_admin
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/rate-limits", tags=["admin", "rate-limits"])


# Pydantic schemas for request/response
class RateLimitPolicyCreate(BaseModel):
    """Schema for creating a new rate limit policy."""

    endpoint_pattern: str = Field(..., min_length=1, max_length=255)
    limit_type: LimitType
    requests_per_window: int = Field(..., gt=0)
    window_seconds: int = Field(..., gt=0)
    burst_multiplier: float = Field(default=1.5, ge=1.0, le=5.0)
    enabled: bool = Field(default=True)
    description: Optional[str] = Field(None, max_length=1000)

    @field_validator("endpoint_pattern")
    @classmethod
    def validate_regex(cls, v: str) -> str:
        """Validate that endpoint_pattern is a valid regex."""
        import re

        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {str(e)}")
        return v


class RateLimitPolicyUpdate(BaseModel):
    """Schema for updating a rate limit policy."""

    requests_per_window: Optional[int] = Field(None, gt=0)
    window_seconds: Optional[int] = Field(None, gt=0)
    burst_multiplier: Optional[float] = Field(None, ge=1.0, le=5.0)
    enabled: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=1000)


class RateLimitPolicyResponse(BaseModel):
    """Schema for rate limit policy response."""

    id: int
    endpoint_pattern: str
    limit_type: str
    requests_per_window: int
    window_seconds: int
    burst_multiplier: float
    enabled: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RateLimitOverrideCreate(BaseModel):
    """Schema for creating a rate limit override."""

    user_id: int = Field(..., gt=0)
    endpoint_pattern: str = Field(..., min_length=1, max_length=255)
    limit_type: LimitType
    requests_per_window: int = Field(..., gt=0)
    window_seconds: int = Field(..., gt=0)
    reason: str = Field(..., min_length=1, max_length=255)
    expires_at: Optional[datetime] = None

    @field_validator("endpoint_pattern")
    @classmethod
    def validate_regex(cls, v: str) -> str:
        """Validate that endpoint_pattern is a valid regex."""
        import re

        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {str(e)}")
        return v

    @field_validator("expires_at")
    @classmethod
    def validate_expiry(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Ensure expiry is in the future."""
        if v and v <= datetime.utcnow():
            raise ValueError("expires_at must be in the future")
        return v


class RateLimitOverrideResponse(BaseModel):
    """Schema for rate limit override response."""

    id: int
    user_id: int
    endpoint_pattern: str
    limit_type: str
    requests_per_window: int
    window_seconds: int
    reason: str
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RateLimitWhitelistCreate(BaseModel):
    """Schema for creating a whitelist entry."""

    identifier: str = Field(..., min_length=1, max_length=255)
    limit_type: LimitType
    reason: str = Field(..., min_length=1, max_length=255)
    enabled: bool = Field(default=True)
    expires_at: Optional[datetime] = None
    created_by: Optional[str] = Field(None, max_length=100)

    @field_validator("expires_at")
    @classmethod
    def validate_expiry(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Ensure expiry is in the future."""
        if v and v <= datetime.utcnow():
            raise ValueError("expires_at must be in the future")
        return v


class RateLimitWhitelistResponse(BaseModel):
    """Schema for whitelist entry response."""

    id: int
    identifier: str
    limit_type: str
    reason: str
    enabled: bool
    expires_at: Optional[datetime]
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True




# Rate Limit Policy Endpoints
@router.get("/policies", response_model=List[RateLimitPolicyResponse])
async def list_policies(
    enabled_only: bool = False,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_async),
) -> List[RateLimitPolicy]:
    """
    List all rate limit policies.

    Args:
        enabled_only: If True, only return enabled policies
        db: Database session
        admin: Authenticated admin user

    Returns:
        List of rate limit policies
    """
    query = select(RateLimitPolicy)
    if enabled_only:
        query = query.where(RateLimitPolicy.enabled == True)  # noqa: E712

    result = await db.execute(query)
    policies = result.scalars().all()

    logger.info(f"Listed {len(policies)} rate limit policies (enabled_only={enabled_only})")
    return list(policies)


@router.post("/policies", response_model=RateLimitPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    policy_data: RateLimitPolicyCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_async),
) -> RateLimitPolicy:
    """
    Create a new rate limit policy.

    Args:
        policy_data: Policy creation data
        db: Database session
        admin: Authenticated admin user

    Returns:
        Created rate limit policy

    Raises:
        HTTPException: If policy with same pattern already exists
    """
    # Check for duplicate pattern
    query = select(RateLimitPolicy).where(
        RateLimitPolicy.endpoint_pattern == policy_data.endpoint_pattern
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Policy for pattern '{policy_data.endpoint_pattern}' already exists",
        )

    # Create policy
    policy = RateLimitPolicy(
        endpoint_pattern=policy_data.endpoint_pattern,
        limit_type=policy_data.limit_type.value,
        requests_per_window=policy_data.requests_per_window,
        window_seconds=policy_data.window_seconds,
        burst_multiplier=policy_data.burst_multiplier,
        enabled=policy_data.enabled,
        description=policy_data.description,
    )

    db.add(policy)
    await db.commit()
    await db.refresh(policy)

    # Clear cache
    rate_limit_config.clear_cache()

    logger.info(
        f"Created rate limit policy: {policy.endpoint_pattern} "
        f"({policy.requests_per_window}/{policy.window_seconds}s)"
    )
    return policy


@router.get("/policies/{policy_id}", response_model=RateLimitPolicyResponse)
async def get_policy(
    policy_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_async),
) -> RateLimitPolicy:
    """
    Get a specific rate limit policy.

    Args:
        policy_id: Policy ID
        db: Database session
        admin: Authenticated admin user

    Returns:
        Rate limit policy

    Raises:
        HTTPException: If policy not found
    """
    query = select(RateLimitPolicy).where(RateLimitPolicy.id == policy_id)
    result = await db.execute(query)
    policy = result.scalar_one_or_none()

    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy {policy_id} not found",
        )

    return policy


@router.patch("/policies/{policy_id}", response_model=RateLimitPolicyResponse)
async def update_policy(
    policy_id: int,
    policy_update: RateLimitPolicyUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_async),
) -> RateLimitPolicy:
    """
    Update a rate limit policy.

    Args:
        policy_id: Policy ID
        policy_update: Fields to update
        db: Database session
        admin: Authenticated admin user

    Returns:
        Updated rate limit policy

    Raises:
        HTTPException: If policy not found
    """
    query = select(RateLimitPolicy).where(RateLimitPolicy.id == policy_id)
    result = await db.execute(query)
    policy = result.scalar_one_or_none()

    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy {policy_id} not found",
        )

    # Update fields
    update_data = policy_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(policy, field, value)

    policy.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(policy)

    # Clear cache
    rate_limit_config.clear_cache()

    logger.info(f"Updated rate limit policy {policy_id}: {update_data}")
    return policy


@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
    policy_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_async),
) -> None:
    """
    Delete a rate limit policy.

    Args:
        policy_id: Policy ID
        db: Database session
        admin: Authenticated admin user

    Raises:
        HTTPException: If policy not found
    """
    query = select(RateLimitPolicy).where(RateLimitPolicy.id == policy_id)
    result = await db.execute(query)
    policy = result.scalar_one_or_none()

    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy {policy_id} not found",
        )

    await db.execute(delete(RateLimitPolicy).where(RateLimitPolicy.id == policy_id))
    await db.commit()

    # Clear cache
    rate_limit_config.clear_cache()

    logger.info(f"Deleted rate limit policy {policy_id}")


# Rate Limit Override Endpoints
@router.get("/overrides", response_model=List[RateLimitOverrideResponse])
async def list_overrides(
    user_id: Optional[int] = None,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_async),
) -> List[RateLimitOverride]:
    """
    List rate limit overrides.

    Args:
        user_id: Filter by user ID
        active_only: If True, only return non-expired overrides
        db: Database session
        admin: Authenticated admin user

    Returns:
        List of rate limit overrides
    """
    query = select(RateLimitOverride)

    if user_id:
        query = query.where(RateLimitOverride.user_id == user_id)

    if active_only:
        query = query.where(
            (RateLimitOverride.expires_at.is_(None))
            | (RateLimitOverride.expires_at > datetime.utcnow())
        )

    result = await db.execute(query)
    overrides = result.scalars().all()

    logger.info(
        f"Listed {len(overrides)} rate limit overrides "
        f"(user_id={user_id}, active_only={active_only})"
    )
    return list(overrides)


@router.post("/overrides", response_model=RateLimitOverrideResponse, status_code=status.HTTP_201_CREATED)
async def create_override(
    override_data: RateLimitOverrideCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_async),
) -> RateLimitOverride:
    """
    Create a rate limit override for a specific user.

    Args:
        override_data: Override creation data
        db: Database session
        admin: Authenticated admin user

    Returns:
        Created rate limit override
    """
    override = RateLimitOverride(
        user_id=override_data.user_id,
        endpoint_pattern=override_data.endpoint_pattern,
        limit_type=override_data.limit_type.value,
        requests_per_window=override_data.requests_per_window,
        window_seconds=override_data.window_seconds,
        reason=override_data.reason,
        expires_at=override_data.expires_at,
    )

    db.add(override)
    await db.commit()
    await db.refresh(override)

    # Clear cache
    rate_limit_config.clear_cache()

    logger.info(
        f"Created rate limit override for user {override.user_id}: "
        f"{override.endpoint_pattern} ({override.requests_per_window}/{override.window_seconds}s) "
        f"- {override.reason}"
    )
    return override


@router.delete("/overrides/{override_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_override(
    override_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_async),
) -> None:
    """
    Delete a rate limit override.

    Args:
        override_id: Override ID
        db: Database session
        admin: Authenticated admin user

    Raises:
        HTTPException: If override not found
    """
    query = select(RateLimitOverride).where(RateLimitOverride.id == override_id)
    result = await db.execute(query)
    override = result.scalar_one_or_none()

    if not override:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Override {override_id} not found",
        )

    await db.execute(delete(RateLimitOverride).where(RateLimitOverride.id == override_id))
    await db.commit()

    # Clear cache
    rate_limit_config.clear_cache()

    logger.info(f"Deleted rate limit override {override_id}")


# Whitelist Endpoints
@router.get("/whitelist", response_model=List[RateLimitWhitelistResponse])
async def list_whitelist(
    enabled_only: bool = False,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_async),
) -> List[RateLimitWhitelist]:
    """
    List whitelist entries.

    Args:
        enabled_only: If True, only return enabled entries
        active_only: If True, only return non-expired entries
        db: Database session
        admin: Authenticated admin user

    Returns:
        List of whitelist entries
    """
    query = select(RateLimitWhitelist)

    if enabled_only:
        query = query.where(RateLimitWhitelist.enabled == True)  # noqa: E712

    if active_only:
        query = query.where(
            (RateLimitWhitelist.expires_at.is_(None))
            | (RateLimitWhitelist.expires_at > datetime.utcnow())
        )

    result = await db.execute(query)
    whitelist_entries = result.scalars().all()

    logger.info(
        f"Listed {len(whitelist_entries)} whitelist entries "
        f"(enabled_only={enabled_only}, active_only={active_only})"
    )
    return list(whitelist_entries)


@router.post("/whitelist", response_model=RateLimitWhitelistResponse, status_code=status.HTTP_201_CREATED)
async def create_whitelist_entry(
    whitelist_data: RateLimitWhitelistCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_async),
) -> RateLimitWhitelist:
    """
    Create a whitelist entry to bypass rate limiting.

    Args:
        whitelist_data: Whitelist creation data
        db: Database session
        admin: Authenticated admin user

    Returns:
        Created whitelist entry
    """
    # Check for duplicate
    query = select(RateLimitWhitelist).where(
        RateLimitWhitelist.identifier == whitelist_data.identifier,
        RateLimitWhitelist.limit_type == whitelist_data.limit_type.value,
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Whitelist entry for {whitelist_data.identifier} "
            f"({whitelist_data.limit_type}) already exists",
        )

    whitelist_entry = RateLimitWhitelist(
        identifier=whitelist_data.identifier,
        limit_type=whitelist_data.limit_type.value,
        reason=whitelist_data.reason,
        enabled=whitelist_data.enabled,
        expires_at=whitelist_data.expires_at,
        created_by=whitelist_data.created_by,
    )

    db.add(whitelist_entry)
    await db.commit()
    await db.refresh(whitelist_entry)

    # Clear cache
    rate_limit_config.clear_cache()

    logger.info(
        f"Created whitelist entry: {whitelist_entry.identifier} "
        f"({whitelist_entry.limit_type}) - {whitelist_entry.reason}"
    )
    return whitelist_entry


@router.delete("/whitelist/{whitelist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_whitelist_entry(
    whitelist_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_async),
) -> None:
    """
    Delete a whitelist entry.

    Args:
        whitelist_id: Whitelist entry ID
        db: Database session
        admin: Authenticated admin user

    Raises:
        HTTPException: If whitelist entry not found
    """
    query = select(RateLimitWhitelist).where(RateLimitWhitelist.id == whitelist_id)
    result = await db.execute(query)
    whitelist_entry = result.scalar_one_or_none()

    if not whitelist_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Whitelist entry {whitelist_id} not found",
        )

    await db.execute(delete(RateLimitWhitelist).where(RateLimitWhitelist.id == whitelist_id))
    await db.commit()

    # Clear cache
    rate_limit_config.clear_cache()

    logger.info(f"Deleted whitelist entry {whitelist_id}")


# Utility Endpoints
@router.post("/clear-cache", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cache(_: bool = Depends(require_admin)) -> None:
    """
    Clear the rate limit configuration cache.

    Forces reload of policies and whitelist from database on next request.

    Args:
        admin: Authenticated admin user
    """
    rate_limit_config.clear_cache()
    logger.info("Rate limit configuration cache cleared")


@router.post("/seed-defaults", status_code=status.HTTP_201_CREATED)
async def seed_default_policies(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin_async),
) -> dict:
    """
    Seed database with default rate limit policies.

    Creates standard policies if they don't exist. Safe to run multiple times.

    Args:
        db: Database session
        admin: Authenticated admin user

    Returns:
        Status message
    """
    await rate_limit_config.seed_default_policies(db)
    return {"message": "Default rate limit policies seeded successfully"}
