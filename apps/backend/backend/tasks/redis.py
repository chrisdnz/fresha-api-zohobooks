
import aioredis
from datetime import datetime, timedelta
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler

from backend.settings import Config


async def redis_connection() -> Redis:
    return await aioredis.Redis.from_url(Config.REDIS_URL)


async def redis_disconnect(redis: Redis):
    await aioredis.Redis.close(redis)


def init_queue():
    return Queue(connection=Redis.from_url(Config.REDIS_URL))


def daily_task():
    print("Daily task")


def init_scheduler(queue: Queue, redis: Redis):
    scheduler = Scheduler(queue=queue, connection=Redis.from_url(Config.REDIS_URL))
    
    scheduler.schedule(
        scheduled_time=datetime.utcnow() + timedelta(seconds=5),
        func=daily_task,
        interval=60,
        repeat=None
    )

    scheduler.run()
