import asyncio
from redis.asyncio import Redis

from simple_logger.logger import get_logger, SimpleLogger
from pytune_configuration.root_config import root_config

# Instance Logger globale
logger : SimpleLogger = get_logger()
redis_client: Redis = None

async def init_redis(redis_url:str)->Redis:
    """
    Initialise l'instance Redis globale et affiche les collections avec leur contenu.
    """
    global redis_client
    try:
        redis_client = Redis.from_url(redis_url, decode_responses=True)
        # Vérifie la connexion à Redis
        await redis_client.ping()
        await logger.ainfo("Redis connection established successfully.")
        return redis_client
    except Exception as e:
        await logger.acritical(f"Failed to connect to Redis: {e}")
        raise
        
async def get_redis_client(redis_url: str = root_config.REDIS_URL) -> Redis:
    """
    Renvoie l'instance Redis globale. Initialise Redis si nécessaire.
    """
    global redis_client
    if redis_client is None:
        await logger.awarning("Redis client is not initialized. Re-initializing.")
        await init_redis(redis_url)
    return redis_client

