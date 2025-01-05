from app.core.config import REDIS_URL
from typing import AsyncGenerator
import redis.asyncio as redis

async def get_redis_client()-> AsyncGenerator[redis.Redis, None]:
    redis_client = redis.from_url(REDIS_URL, db=0)
    try:
        yield redis_client
    finally:
        await redis_client.close()