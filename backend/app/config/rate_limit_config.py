"""
Rate Limiting Configuration System.

Provides database-driven rate limiting configuration with support for:
- Endpoint-specific rate limit policies
- Per-user overrides and exceptions
- Dynamic policy updates without code changes
- Burst allowances for short-term spikes
- Whitelisting for internal services
- Comprehensive metrics and monitoring

This replaces hardcoded rate limits with flexible, database-backed policies
that can be updated via admin API or database directly.
"""

import logging
import re
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rate_limit import RateLimitPolicy, RateLimitOverride, RateLimitWhitelist

logger = logging.getLogger(__name__)


class LimitType(str, Enum):
    """Type of rate limiting identifier."""

    IP = "ip"
    USER = "user"
    API_KEY = "api_key"


class EndpointTier(str, Enum):
    """Predefined rate limit tiers for common endpoint types."""

    AUTH = "auth"  # 5 req/min per IP
    RECIPE_API = "recipe_api"  # 100 req/min per user
    MEAL_PLANS = "meal_plans"  # 50 req/min per user
    WORKFLOWS = "workflows"  # 10 req/5min per user
    KNUSPR_CART = "knuspr_cart"  # 20 req/min per user
    PUBLIC = "public"  # 1000 req/min per IP
    BULK_EXPORT = "bulk_export"  # 5 req/hour per user


# Default rate limit configurations for each tier
DEFAULT_TIER_CONFIGS = {
    EndpointTier.AUTH: {
        "limit_type": LimitType.IP,
        "requests_per_window": 5,
        "window_seconds": 60,
        "burst_multiplier": 1.2,  # Allow 6 requests in burst
        "description": "Authentication endpoints - prevent brute force",
    },
    EndpointTier.RECIPE_API: {
        "limit_type": LimitType.USER,
        "requests_per_window": 100,
        "window_seconds": 60,
        "burst_multiplier": 1.5,  # Allow 150 in burst
        "description": "Recipe read operations - prevent scraping",
    },
    EndpointTier.MEAL_PLANS: {
        "limit_type": LimitType.USER,
        "requests_per_window": 50,
        "window_seconds": 60,
        "burst_multiplier": 1.3,  # Allow 65 in burst
        "description": "Meal plan operations - moderate usage",
    },
    EndpointTier.WORKFLOWS: {
        "limit_type": LimitType.USER,
        "requests_per_window": 10,
        "window_seconds": 300,
        "burst_multiplier": 1.0,  # No burst for expensive operations
        "description": "AI workflow operations - expensive, strict limits",
    },
    EndpointTier.KNUSPR_CART: {
        "limit_type": LimitType.USER,
        "requests_per_window": 20,
        "window_seconds": 60,
        "burst_multiplier": 1.5,  # Allow 30 in burst
        "description": "Grocery cart operations - external API integration",
    },
    EndpointTier.PUBLIC: {
        "limit_type": LimitType.IP,
        "requests_per_window": 1000,
        "window_seconds": 60,
        "burst_multiplier": 2.0,  # Allow 2000 in burst for docs/metrics
        "description": "Public endpoints - generous limits",
    },
    EndpointTier.BULK_EXPORT: {
        "limit_type": LimitType.USER,
        "requests_per_window": 5,
        "window_seconds": 3600,
        "burst_multiplier": 1.0,  # No burst for bulk operations
        "description": "Bulk export operations - very expensive",
    },
}


class RateLimitConfig:
    """
    Rate limiting configuration manager.

    Provides centralized access to rate limit policies with caching,
    override support, and whitelisting capabilities.
    """

    def __init__(self, cache_ttl: int = 300):
        """
        Initialize rate limit configuration.

        Args:
            cache_ttl: Cache TTL in seconds (default 5 minutes)
        """
        self.cache_ttl = cache_ttl
        self._policy_cache: Dict[str, Tuple[RateLimitPolicy, datetime]] = {}
        self._whitelist_cache: Dict[str, Tuple[bool, datetime]] = {}

    async def get_policy_for_endpoint(
        self, endpoint: str, db: AsyncSession
    ) -> Optional[RateLimitPolicy]:
        """
        Get rate limit policy for a specific endpoint.

        Checks cache first, then queries database. Falls back to default
        configuration if no policy is found.

        Args:
            endpoint: API endpoint path (e.g., "/api/v1/auth/login")
            db: Database session

        Returns:
            RateLimitPolicy or None if not found
        """
        # Check cache
        if endpoint in self._policy_cache:
            policy, cached_at = self._policy_cache[endpoint]
            if (datetime.utcnow() - cached_at).total_seconds() < self.cache_ttl:
                return policy

        # Query database for matching policy
        query = select(RateLimitPolicy).where(RateLimitPolicy.enabled == True)  # noqa: E712
        result = await db.execute(query)
        policies = result.scalars().all()

        # Find matching policy by regex pattern
        for policy in policies:
            try:
                if re.match(policy.endpoint_pattern, endpoint):
                    # Cache the policy
                    self._policy_cache[endpoint] = (policy, datetime.utcnow())
                    return policy
            except re.error:
                logger.warning(
                    f"Invalid regex pattern in policy {policy.id}: {policy.endpoint_pattern}"
                )
                continue

        return None

    async def get_override_for_user(
        self, user_id: int, endpoint: str, db: AsyncSession
    ) -> Optional[RateLimitOverride]:
        """
        Get rate limit override for a specific user and endpoint.

        Args:
            user_id: User ID
            endpoint: API endpoint path
            db: Database session

        Returns:
            RateLimitOverride or None if not found
        """
        query = (
            select(RateLimitOverride)
            .where(RateLimitOverride.user_id == user_id)
            .where(
                (RateLimitOverride.expires_at.is_(None))
                | (RateLimitOverride.expires_at > datetime.utcnow())
            )
        )
        result = await db.execute(query)
        overrides = result.scalars().all()

        # Find matching override by regex pattern
        for override in overrides:
            try:
                if re.match(override.endpoint_pattern, endpoint):
                    return override
            except re.error:
                logger.warning(
                    f"Invalid regex pattern in override {override.id}: "
                    f"{override.endpoint_pattern}"
                )
                continue

        return None

    async def is_whitelisted(
        self, identifier: str, limit_type: LimitType, db: AsyncSession
    ) -> bool:
        """
        Check if an identifier is whitelisted for rate limiting.

        Whitelisted identifiers bypass all rate limits. Useful for:
        - Internal service accounts
        - Admin users
        - Monitoring/health check services

        Args:
            identifier: IP address, user ID, or API key
            limit_type: Type of identifier
            db: Database session

        Returns:
            True if whitelisted, False otherwise
        """
        cache_key = f"{limit_type}:{identifier}"

        # Check cache
        if cache_key in self._whitelist_cache:
            is_whitelisted, cached_at = self._whitelist_cache[cache_key]
            if (datetime.utcnow() - cached_at).total_seconds() < self.cache_ttl:
                return is_whitelisted

        # Query database
        query = (
            select(RateLimitWhitelist)
            .where(RateLimitWhitelist.identifier == identifier)
            .where(RateLimitWhitelist.limit_type == limit_type.value)
            .where(RateLimitWhitelist.enabled == True)  # noqa: E712
            .where(
                (RateLimitWhitelist.expires_at.is_(None))
                | (RateLimitWhitelist.expires_at > datetime.utcnow())
            )
        )
        result = await db.execute(query)
        whitelist_entry = result.scalar_one_or_none()

        is_whitelisted = whitelist_entry is not None

        # Cache result
        self._whitelist_cache[cache_key] = (is_whitelisted, datetime.utcnow())

        return is_whitelisted

    async def get_effective_limit(
        self,
        endpoint: str,
        user_id: Optional[int],
        ip_address: str,
        db: AsyncSession,
    ) -> Dict[str, any]:
        """
        Calculate effective rate limit for a request.

        Considers:
        1. Whitelisting (bypasses all limits)
        2. User-specific overrides
        3. Endpoint-specific policies
        4. Default tier configuration

        Args:
            endpoint: API endpoint path
            user_id: User ID (if authenticated)
            ip_address: Client IP address
            db: Database session

        Returns:
            Dictionary with:
                - limit_type: Type of limiting (ip/user/api_key)
                - requests_per_window: Max requests allowed
                - window_seconds: Time window in seconds
                - burst_multiplier: Multiplier for burst allowance
                - identifier: Actual identifier to use for rate limiting
                - is_whitelisted: Whether request is whitelisted
        """
        # Check whitelisting first
        if user_id and await self.is_whitelisted(str(user_id), LimitType.USER, db):
            return {
                "limit_type": LimitType.USER,
                "requests_per_window": 999999,  # Effectively unlimited
                "window_seconds": 60,
                "burst_multiplier": 1.0,
                "identifier": f"user_{user_id}",
                "is_whitelisted": True,
            }

        if await self.is_whitelisted(ip_address, LimitType.IP, db):
            return {
                "limit_type": LimitType.IP,
                "requests_per_window": 999999,
                "window_seconds": 60,
                "burst_multiplier": 1.0,
                "identifier": f"ip_{ip_address}",
                "is_whitelisted": True,
            }

        # Check user override
        if user_id:
            override = await self.get_override_for_user(user_id, endpoint, db)
            if override:
                logger.info(
                    f"Applying rate limit override for user {user_id} on {endpoint}: "
                    f"{override.requests_per_window}/{override.window_seconds}s "
                    f"(reason: {override.reason})"
                )
                return {
                    "limit_type": override.limit_type,
                    "requests_per_window": override.requests_per_window,
                    "window_seconds": override.window_seconds,
                    "burst_multiplier": 1.5,  # Default burst for overrides
                    "identifier": f"{override.limit_type}_{user_id if user_id else ip_address}",
                    "is_whitelisted": False,
                }

        # Check endpoint policy
        policy = await self.get_policy_for_endpoint(endpoint, db)
        if policy:
            identifier_value = user_id if policy.limit_type == LimitType.USER.value else ip_address
            return {
                "limit_type": policy.limit_type,
                "requests_per_window": policy.requests_per_window,
                "window_seconds": policy.window_seconds,
                "burst_multiplier": policy.burst_multiplier,
                "identifier": f"{policy.limit_type}_{identifier_value}",
                "is_whitelisted": False,
            }

        # Fall back to default configuration based on endpoint pattern
        tier = self._infer_endpoint_tier(endpoint)
        config = DEFAULT_TIER_CONFIGS[tier]

        identifier_value = user_id if config["limit_type"] == LimitType.USER else ip_address
        return {
            "limit_type": config["limit_type"],
            "requests_per_window": config["requests_per_window"],
            "window_seconds": config["window_seconds"],
            "burst_multiplier": config["burst_multiplier"],
            "identifier": f"{config['limit_type']}_{identifier_value}",
            "is_whitelisted": False,
        }

    def _infer_endpoint_tier(self, endpoint: str) -> EndpointTier:
        """
        Infer rate limit tier from endpoint pattern.

        Args:
            endpoint: API endpoint path

        Returns:
            EndpointTier enum value
        """
        # Auth endpoints
        if re.match(r"^/api/v1/auth/(login|register|refresh)$", endpoint):
            return EndpointTier.AUTH

        # Workflow endpoints
        if re.match(r"^/api/v1/workflows/", endpoint):
            return EndpointTier.WORKFLOWS

        # Bulk export endpoints
        if "bulk-export" in endpoint or "export-all" in endpoint:
            return EndpointTier.BULK_EXPORT

        # Meal plan endpoints
        if re.match(r"^/api/v1/meal-plans", endpoint):
            return EndpointTier.MEAL_PLANS

        # Grocery cart endpoints
        if re.match(r"^/api/v1/grocery-carts", endpoint):
            return EndpointTier.KNUSPR_CART

        # Recipe endpoints
        if re.match(r"^/api/v1/recipes", endpoint):
            return EndpointTier.RECIPE_API

        # Public endpoints (docs, health, metrics)
        if endpoint in ["/", "/docs", "/redoc", "/health", "/metrics", "/openapi.json"]:
            return EndpointTier.PUBLIC

        # Default to recipe API tier for unknown endpoints
        return EndpointTier.RECIPE_API

    def clear_cache(self) -> None:
        """Clear all cached rate limit policies and whitelists."""
        self._policy_cache.clear()
        self._whitelist_cache.clear()
        logger.info("Rate limit configuration cache cleared")

    async def seed_default_policies(self, db: AsyncSession) -> None:
        """
        Seed database with default rate limit policies.

        Creates policies for all endpoint tiers if they don't already exist.
        Safe to run multiple times - only creates missing policies.

        Args:
            db: Database session
        """
        from app.models.rate_limit import RateLimitPolicy

        default_policies = [
            # Auth endpoints
            {
                "endpoint_pattern": r"^/api/v1/auth/login$",
                "limit_type": LimitType.IP.value,
                "requests_per_window": 5,
                "window_seconds": 60,
                "burst_multiplier": 1.2,
                "enabled": True,
                "description": "Login endpoint - prevent brute force",
            },
            {
                "endpoint_pattern": r"^/api/v1/auth/register$",
                "limit_type": LimitType.IP.value,
                "requests_per_window": 5,
                "window_seconds": 60,
                "burst_multiplier": 1.2,
                "enabled": True,
                "description": "Registration endpoint - prevent abuse",
            },
            {
                "endpoint_pattern": r"^/api/v1/auth/refresh$",
                "limit_type": LimitType.USER.value,
                "requests_per_window": 10,
                "window_seconds": 60,
                "burst_multiplier": 1.5,
                "enabled": True,
                "description": "Token refresh - moderate limits",
            },
            # Recipe endpoints
            {
                "endpoint_pattern": r"^/api/v1/recipes(\?.*)?$",
                "limit_type": LimitType.USER.value,
                "requests_per_window": 100,
                "window_seconds": 60,
                "burst_multiplier": 1.5,
                "enabled": True,
                "description": "Recipe list - prevent scraping",
            },
            {
                "endpoint_pattern": r"^/api/v1/recipes/\d+$",
                "limit_type": LimitType.USER.value,
                "requests_per_window": 100,
                "window_seconds": 60,
                "burst_multiplier": 1.5,
                "enabled": True,
                "description": "Recipe detail - reasonable access",
            },
            # Meal plans
            {
                "endpoint_pattern": r"^/api/v1/meal-plans",
                "limit_type": LimitType.USER.value,
                "requests_per_window": 50,
                "window_seconds": 60,
                "burst_multiplier": 1.3,
                "enabled": True,
                "description": "Meal plan operations",
            },
            # Workflows (expensive)
            {
                "endpoint_pattern": r"^/api/v1/workflows/",
                "limit_type": LimitType.USER.value,
                "requests_per_window": 10,
                "window_seconds": 300,
                "burst_multiplier": 1.0,
                "enabled": True,
                "description": "AI workflows - expensive operations",
            },
            # Grocery carts
            {
                "endpoint_pattern": r"^/api/v1/grocery-carts",
                "limit_type": LimitType.USER.value,
                "requests_per_window": 20,
                "window_seconds": 60,
                "burst_multiplier": 1.5,
                "enabled": True,
                "description": "Grocery cart operations",
            },
            # Bulk export (very expensive)
            {
                "endpoint_pattern": r"^/api/v1/recipes/bulk-export$",
                "limit_type": LimitType.USER.value,
                "requests_per_window": 5,
                "window_seconds": 3600,
                "burst_multiplier": 1.0,
                "enabled": True,
                "description": "Bulk export - very expensive",
            },
            # Public endpoints
            {
                "endpoint_pattern": r"^/(docs|redoc|health|metrics|openapi\.json)$",
                "limit_type": LimitType.IP.value,
                "requests_per_window": 1000,
                "window_seconds": 60,
                "burst_multiplier": 2.0,
                "enabled": True,
                "description": "Public documentation and health checks",
            },
        ]

        for policy_data in default_policies:
            # Check if policy already exists
            query = select(RateLimitPolicy).where(
                RateLimitPolicy.endpoint_pattern == policy_data["endpoint_pattern"]
            )
            result = await db.execute(query)
            existing = result.scalar_one_or_none()

            if not existing:
                policy = RateLimitPolicy(**policy_data)
                db.add(policy)
                logger.info(f"Created rate limit policy: {policy_data['endpoint_pattern']}")

        await db.commit()
        logger.info("Default rate limit policies seeded successfully")


# Global configuration instance
rate_limit_config = RateLimitConfig()
