
import asyncpg
from pytune_configuration.root_config import root_config
import os

# Configuration de la base de données
DATABASE_CONFIG = {
    'config_manager': {
        'user': root_config.CONFIG_MANAGER_USER,
        'password': root_config.CONFIG_MANAGER_PWD,
        'database': root_config.DB_NAME,
        'host': root_config.DB_HOST,  
        'port': root_config.DB_PORT,       
    },
    'fastapi_user': {
        'user': root_config.FASTAPI_USER,
        'password': root_config.FASTAPI_PWD,
        'database':root_config.DB_NAME,
        'host': root_config.DB_HOST, 
        'port': root_config.DB_PORT,    
    }
}

class PostgresService:
    _config_manager_pool = None
    _fastapi_user_pool = None

    @classmethod
    async def create_pools(cls):
        if cls._config_manager_pool is None:
            cls._config_manager_pool = await asyncpg.create_pool(**DATABASE_CONFIG['config_manager'])
        if cls._fastapi_user_pool is None:
            cls._fastapi_user_pool = await asyncpg.create_pool(**DATABASE_CONFIG['fastapi_user'])

    @classmethod
    def get_config_manager_pool(cls):
        return cls._config_manager_pool

    @classmethod
    def get_fastapi_user_pool(cls):
        return cls._fastapi_user_pool

    @classmethod
    async def close_pools(cls):
        if cls._config_manager_pool is not None:
            await cls._config_manager_pool.close()
        if cls._fastapi_user_pool is not None:
            await cls._fastapi_user_pool.close()

# appeler create_pools au démarrage de l'application (main)
# et close_pools à la fermeture. 



