"""
Rate Limiting Database Models.

Defines tables for:
- RateLimitPolicy: Endpoint-specific rate limiting rules
- RateLimitOverride: Per-user exceptions and custom limits
- RateLimitWhitelist: Identifiers exempt from rate limiting
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RateLimitPolicy(Base):
    """
    Rate limit policy for specific endpoint patterns.

    Stores configurable rate limits that can be updated without code changes.
    Supports regex patterns for flexible endpoint matching.
    """

    __tablename__ = "rate_limit_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    endpoint_pattern: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    limit_type: Mapped[str] = mapped_column(String(20), nullable=False)  # ip, user, api_key
    requests_per_window: Mapped[int] = mapped_column(Integer, nullable=False)
    window_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    burst_multiplier: Mapped[float] = mapped_column(Float, nullable=False, default=1.5)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_rate_limit_policies_enabled", "enabled"),
        Index("idx_rate_limit_policies_pattern", "endpoint_pattern"),
    )

    def __repr__(self) -> str:
        return (
            f"<RateLimitPolicy(id={self.id}, pattern='{self.endpoint_pattern}', "
            f"limit={self.requests_per_window}/{self.window_seconds}s, "
            f"type={self.limit_type}, enabled={self.enabled})>"
        )


class RateLimitOverride(Base):
    """
    User-specific rate limit overrides.

    Allows granting higher (or lower) rate limits to specific users.
    Useful for:
    - VIP customers
    - API partners
    - Internal testing
    - Temporary limit increases
    """

    __tablename__ = "rate_limit_overrides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    endpoint_pattern: Mapped[str] = mapped_column(String(255), nullable=False)
    limit_type: Mapped[str] = mapped_column(String(20), nullable=False)  # ip, user, api_key
    requests_per_window: Mapped[int] = mapped_column(Integer, nullable=False)
    window_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_rate_limit_overrides_user", "user_id"),
        Index("idx_rate_limit_overrides_expires", "expires_at"),
        Index("idx_rate_limit_overrides_user_expires", "user_id", "expires_at"),
    )

    def __repr__(self) -> str:
        expiry = f"expires {self.expires_at}" if self.expires_at else "permanent"
        return (
            f"<RateLimitOverride(id={self.id}, user_id={self.user_id}, "
            f"pattern='{self.endpoint_pattern}', "
            f"limit={self.requests_per_window}/{self.window_seconds}s, {expiry})>"
        )


class RateLimitWhitelist(Base):
    """
    Whitelist entries for rate limiting bypass.

    Identifiers in this table are exempt from all rate limiting.
    Useful for:
    - Internal service accounts
    - Monitoring/health check services
    - Admin users during incidents
    - CI/CD pipelines
    """

    __tablename__ = "rate_limit_whitelist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    identifier: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )  # IP, user_id, or api_key
    limit_type: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )  # ip, user, api_key
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_rate_limit_whitelist_identifier_type", "identifier", "limit_type"),
        Index("idx_rate_limit_whitelist_enabled", "enabled"),
        Index("idx_rate_limit_whitelist_expires", "expires_at"),
    )

    def __repr__(self) -> str:
        expiry = f"expires {self.expires_at}" if self.expires_at else "permanent"
        status = "enabled" if self.enabled else "disabled"
        return (
            f"<RateLimitWhitelist(id={self.id}, identifier='{self.identifier}', "
            f"type={self.limit_type}, {status}, {expiry})>"
        )
