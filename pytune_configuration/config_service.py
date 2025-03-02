import asyncio
import os
import threading
import asyncpg
from fastapi import HTTPException
from pytune_configuration.postgres_service import PostgresService
from pytune_configuration.root_config import root_config
from pytune_configuration.utils import parse_value
from simple_logger.logger import SimpleLogger, get_logger
from pytune_configuration.redis_config import get_redis_client

# Global async lock for protecting config updates
config_lock = asyncio.Lock()
logger: SimpleLogger = get_logger()
config_global = None
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Use Config multisingleton class only in ASYNC Context 
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

class Config:
    _instances = {}  # Dictionnaire pour stocker les instances par table_name
    _lock = threading.Lock()  # Lock pour la gestion des instances

    def __new__(cls, *args, table_name="configurations", **kwargs):
        with cls._lock:
            if table_name not in cls._instances:
                cls._instances[table_name] = super(Config, cls).__new__(cls)
        return cls._instances[table_name]

    def __init__(self, table_name="configurations"):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.table_name = table_name
            self.logger:SimpleLogger = get_logger()

    async def initialize(self):
        """
        Initialize configuration and associated services.
        :param use_redis_listener: Boolean to decide if the RedisListener should be started.
        """
        await self.logger.ainfo(f"Starting PyTune Configuration Provider for table: {self.table_name}")
        await self.load_configurations()

    async def load_configurations(self):
        """
        Load configurations from PostgreSQL and set them as attributes.
        """
        await self.logger.ainfo(f"Loading configurations from table: {self.table_name}")
        async with config_lock:
            try:
                conn = await asyncpg.connect(
                    user=root_config.CONFIG_MANAGER_USER,
                    password=root_config.CONFIG_MANAGER_PWD,
                    database=root_config.DB_NAME,
                    host=root_config.DB_HOST,
                    port=root_config.DB_PORT,
                )
                async with conn.transaction():
                    query = f"SELECT name, value FROM {self.table_name}"
                    async for record in conn.cursor(query):
                        name = record["name"]
                        value = record["value"]
                        parsed_value = parse_value(value)
                        setattr(self, name, parsed_value) # Définit chaque paramètre comme un attribut
                await conn.close()
                await self.logger.ainfo(f"Configurations loaded successfully for table: {self.table_name}")

                # Charger l'URL Redis en fonction de l'environnement
                config_global.REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
                config_global.RABBIT_BROKER_URL = os.getenv("RABBIT_BROKER_URL", "pyamqp://admin:MyStr0ngP@ss2024!@localhost//")
                config_global.RABBIT_BACKEND = os.getenv("RABBIT_BACKEND", "redis://127.0.0.1:6379/0")
                    
                await self.logger.ainfo(f"REDIS_URL défini sur : {config_global.REDIS_URL}")
                await self.logger.ainfo(f"RABBIT_BROKER_URL défini sur : {config_global.RABBIT_BROKER_URL}")
                await self.logger.ainfo(f"RABBIT_BACKEND défini sur : {config_global.RABBIT_BACKEND}")
            
            except Exception as e:
                await self.logger.acritical(f"Error while loading configurations from table {self.table_name}: {e}")
                raise RuntimeError(f"Error while loading configurations: {e}")

    async def update_config_in_db(self, config_key: str, config_value: str, description: str):
        """
        Met à jour un paramètre de configuration dans la base de données PostgreSQL.
        """
        redis_client = await get_redis_client()
        async with config_lock:
            async with PostgresService.get_config_manager_pool().acquire() as conn:
                try:
                    await conn.execute(
                        "UPDATE configurations SET value = $1, description = $2 WHERE name = $3",
                        config_value, description, config_key
                    )
                    await redis_client.publish("config_change", f"config_update:{config_key}:{config_value}")
                except Exception as e:
                    await self.logger.acritical(f"Error while updating config : {e}")
                
    async def delete_config_in_db(self, config_key: str):
        """
        Supprime un paramètre de configuration de la base de données PostgreSQL
        """
        redis_client = await get_redis_client()
        async with config_lock:
            async with PostgresService.get_config_manager_pool().acquire() as conn:
                try:
                    await conn.execute(
                        "DELETE FROM configurations WHERE name = $1",
                        config_key
                    )
                    await redis_client.publish("config_change", f"config_delete:{config_key}")
                except Exception as e:
                    await self.logger.acritical(f"Error while deleting an iten from configuration : {e}")
                    
    async def add_config_to_db(self, config_key: str, config_value: str, description: str = ""):
        """
        Adds a new configuration parameter to the PostgreSQL database.
        """
        redis_client = await get_redis_client()
        async with config_lock:
            async with PostgresService.get_config_manager_pool().acquire() as conn:
                try:
                    await self.logger.ainfo(f"Attempting to insert config_key={config_key}, config_value={config_value}, description={description}")
                    result = await conn.execute(
                        "INSERT INTO configurations (name, value, description) VALUES ($1, $2, $3)",
                        config_key, config_value, description
                    )
                    await redis_client.publish("config_change", f"config_add:{config_key}:{config_value}")
                    await self.logger.ainfo(f"Insert result: {result}")
                    return {"message": "Configuration added successfully."}

                except asyncpg.UniqueViolationError:
                    await self.logger.aerror(f"Configuration key '{config_key}' already exists.")
                    raise HTTPException(status_code=400, detail=f"Configuration '{config_key}' already exists.")  # Client response

                except asyncpg.DataError as e:
                    await self.logger.aerror(f"Data type error while adding configuration: {e}")
                    raise HTTPException(status_code=400, detail=f"Data error: {e}")

                except asyncpg.Error as e:
                    await self.logger.aerror(f"General database error while adding configuration: {e}")
                    raise HTTPException(status_code=500, detail="A database error occurred.")

                except Exception as e:
                    await self.logger.aerror(f"Unexpected error while adding configuration: {e}")
                    raise HTTPException(status_code=500, detail="An unexpected error occurred.")


    async def handle_config_change(self, message):
        """
        Callback to handle events from the 'config_change' channel.
        """
        try:
            if message.startswith("config_update:"):
                _, config_data = message.split("config_update:")
                key, value = config_data.split(":", 1)
                setattr(self, key, value)
                await self.logger.ainfo(f"Configuration updated: {key} = {value}")
            elif message.startswith("config_delete:"):
                _, key = message.split("config_delete:")
                if hasattr(self, key):
                    delattr(self, key)
                    await self.logger.ainfo(f"Configuration deleted: {key}")
                else:
                    await self.logger.awarning(f"Attempted to delete non-existent key: {key}")
            elif message.startswith("config_add:"):
                _, config_data = message.split("config_add:")
                key, value = config_data.split(":", 1)
                setattr(self, key, value)
                await self.logger.ainfo(f"Configuration added: {key} = {value}")
            elif message == "force_reload":
                await self.logger.ainfo("Force reload of configurations triggered.")
                await self.load_configurations()
            else:
                await self.logger.awarning(f"Unrecognized message received on 'config_change': {message}")
        except Exception as e:
            await self.logger.acritical(f"Error handling config change message: {e}")

    async def update_config(self, key, value):
        """
        Mettre à jour une configuration.
        """
        async with config_lock:
            setattr(self, key, value)
            await self.logger.ainfo(f"Configuration updated: {key} = {value}")

    async def add_config(self, key, value):
            """
            Ajouter une nouvelle configuration.
            """
            async with config_lock:
                setattr(self, key, value)
                await self.logger.ainfo(f"Configuration added: {key} = {value}")

    async def delete_config(self, key):
        """
        Supprimer une configuration.
        """
        async with config_lock:
            if hasattr(self, key):
                delattr(self, key)
                await self.logger.ainfo(f"Configuration deleted: {key}")

    async def reload_configurations(self):
        """
        Recharger toutes les configurations depuis la base de données.
        """
        await self.load_configurations()
        await self.logger.ainfo("Configurations reloaded successfully.")


# Fonctions utilitaires pour l'instance globale de configuration
#####!!!!!!!!!! Verifier si encore utile ?????????????????????
async def initialize_config(table_name: str = "configurations"):
    """
    Initialise l'instance globale de configuration si ce n'est pas déjà fait.
    """
    global config_global
    if config_global is None:
        await logger.ainfo(f"Initializing global Config for table '{table_name}'")
        config_global = Config(table_name=table_name)
        await config_global.initialize()
 

    return config_global

async def get_config(table_name : str = "configurations")->Config:
    global config_global
    if config_global is None:
        config_global = Config(table_name=table_name)
        await config_global.initialize()
    return config_global


