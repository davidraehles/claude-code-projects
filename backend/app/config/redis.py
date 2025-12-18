import os
from functools import lru_cache
from typing import Optional
import redis.asyncio as redis

class RedisSettings:
    """Redis configuration settings."""
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.db = int(os.getenv("REDIS_DB", "0"))
        self.password = os.getenv("REDIS_PASSWORD", None)
        self.ssl = os.getenv("REDIS_SSL", "false").lower() == "true"

    @property
    def url(self) -> str:
        """Get Redis connection URL."""
        # Return a non-authenticated URL for display/logging. Avoid embedding
        # passwords in URLs to prevent accidental leakage in logs.
        schema = "rediss" if self.ssl else "redis"
        return f"{schema}://{self.host}:{self.port}/{self.db}"

@lru_cache()
def get_redis_settings() -> RedisSettings:
    """Get cached Redis settings."""
    return RedisSettings()

_pool: Optional[redis.ConnectionPool] = None

def get_redis_pool() -> redis.ConnectionPool:
    """Get or create global Redis connection pool."""
    global _pool
    if _pool is None:
        settings = get_redis_settings()
        # Use ConnectionPool with explicit credentials to avoid embedding
        # secrets in the URL string which may be logged.
        _pool = redis.ConnectionPool(
            host=settings.host,
            port=settings.port,
            db=settings.db,
            password=settings.password,
            ssl=settings.ssl,
            encoding="utf-8",
            decode_responses=True,
        )
    return _pool

async def get_redis_client() -> redis.Redis:
    """Get Redis client instance using shared pool."""
    pool = get_redis_pool()
    return redis.Redis(connection_pool=pool)
