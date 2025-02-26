import asyncio
from pytune_configuration.postgres_service import DATABASE_CONFIG, PostgresService
from pytune_configuration.redis_config import *
from pytune_configuration.config_service import Config
from pytune_configuration.redis_listener import RedisListener
from pytune_configuration.config_change_handler import ConfigChangeHandler
from pytune_logger.logger import get_logger

# Logger pour le service de configuration
logger_config = get_logger(name="config_service", index="pytune_configuration")
logger_config.sync_log_info("Logger for Config initialized")


# Exporte explicitement les objets ou fonctions visibles pour les utilisateurs
__all__ = [
    "DATABASE_CONFIG",
    "PostgresService",
    "Config",
    "RedisListener",
    "ConfigChangeHandler",
    "initialize_config",
    "get_config_instance",
]
