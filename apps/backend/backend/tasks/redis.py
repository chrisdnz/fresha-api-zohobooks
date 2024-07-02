
import aioredis
from redis import Redis
from rq import Queue
from backend.settings import Config


async def redis_connection() -> Redis:
    return await aioredis.Redis.from_url(Config.REDIS_URL)


async def redis_disconnect(redis: Redis):
    await aioredis.Redis.close(redis)


def init_queue():
    return Queue(connection=Redis.from_url(Config.REDIS_URL))