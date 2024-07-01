from redis import Redis
from backend.settings import Config

redis = Redis.from_url(Config.REDIS_URL)