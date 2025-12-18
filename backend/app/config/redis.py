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
        schema = "rediss" if self.ssl else "redis"
        auth = f":{self.password}@" if self.password else ""
        return f"{schema}://{auth}{self.host}:{self.port}/{self.db}"

@lru_cache()
def get_redis_settings() -> RedisSettings:
    """Get cached Redis settings."""
    return RedisSettings()

async def get_redis_client() -> redis.Redis:
    """Get Redis client instance."""
    settings = get_redis_settings()
    return await redis.from_url(
        settings.url,
        encoding="utf-8",
        decode_responses=True
    )
