
import aioredis
from redis import Redis
from rq import Queue
from backend.settings import Config

redis = Redis.from_url(Config.REDIS_URL)

async_redis = None

async def redis_connection() -> Redis:
    global async_redis
    async_redis = await aioredis.Redis.from_url(Config.REDIS_URL)

async def redis_disconnect(redis: Redis):
    if async_redis:
        await aioredis.Redis.close()


queue = Queue(connection=redis)