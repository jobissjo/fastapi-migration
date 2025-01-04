import aioredis
from app.core.config import REDIS_URL
from typing import AsyncGenerator

async def get_redis_client()-> AsyncGenerator[aioredis.Redis, None]:
    redis = aioredis.from_url(REDIS_URL, db=0)
    try:
        yield redis
    finally:
        await redis.close()