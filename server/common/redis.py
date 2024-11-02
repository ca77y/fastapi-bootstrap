from typing import Optional

from redis import asyncio as aioredis

from server.config import settings

_redis: Optional[aioredis.Redis] = None


def get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.datastores.redis_url)
    return _redis


async def close_redis():
    global _redis
    if _redis:
        await _redis.close()
        _redis = None
