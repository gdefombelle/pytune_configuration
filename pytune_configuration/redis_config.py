import time
from redis.asyncio import Redis
from simple_logger.logger import get_logger
from pytune_configuration.root_config import root_config

logger = get_logger("configuration")
redis_client: Redis = None
_last_redis_ping_time = 0
REDIS_PING_INTERVAL = 30  # secondes

async def init_redis(redis_url: str) -> Redis:
    global redis_client
    redis_client = Redis.from_url(redis_url, decode_responses=True)
    await redis_client.ping()
    await logger.ainfo("Redis connection established successfully.")
    return redis_client

async def get_redis_client(redis_url: str = root_config.REDIS_URL) -> Redis:
    """
    Renvoie une instance Redis connectée, avec ping() toutes les 30s max.
    """
    global redis_client, _last_redis_ping_time

    if redis_client is None:
        await logger.awarning("Redis client is None. Re-initializing.")
        return await init_redis(redis_url)

    now = time.time()
    if now - _last_redis_ping_time > REDIS_PING_INTERVAL:
        try:
            await redis_client.ping()
            _last_redis_ping_time = now
        except Exception as e:
            await logger.awarning(f"Redis client lost. Re-initializing. Error: {e}")
            return await init_redis(redis_url)

    return redis_client
