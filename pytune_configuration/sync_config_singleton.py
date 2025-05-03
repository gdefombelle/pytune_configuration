import os
import threading
import psycopg2  # Utilisé pour les connexions synchrones à PostgreSQL
from pytune_configuration.root_config import root_config
from pytune_configuration.utils import parse_value

class SimpleConfig:
    _instances = {}  # Dictionnaire pour stocker les instances par table_name
    _lock = threading.Lock()  # Lock pour gérer la création d'instances

    def __new__(cls, *args, table_name="configurations", **kwargs):
        with cls._lock:
            if table_name not in cls._instances:
                cls._instances[table_name] = super(SimpleConfig, cls).__new__(cls)
        return cls._instances[table_name]

    def __init__(self, table_name="configurations"):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.table_name = table_name
            self._load_configurations()

            # Charger les URL dynamiques en fonction de l'environnement
            self.REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
            self.RABBIT_BROKER_URL = os.getenv("RABBIT_BROKER_URL", "pyamqp://admin:MyStr0ngP@ss2024!@localhost//")
            self.RABBIT_BACKEND = os.getenv("RABBIT_BACKEND", "redis://:UltraSecurePass2024!@195.201.9.184:6379")
            

    def _load_configurations(self):
        """
        Charge les configurations depuis PostgreSQL et les attribue comme attributs de l'instance.
        """
        try:
            # Connexion à la base de données
            conn = psycopg2.connect(
                user=root_config.CONFIG_MANAGER_USER,
                password=root_config.CONFIG_MANAGER_PWD,
                database=root_config.DB_NAME,
                host=root_config.DB_HOST,
                port=root_config.DB_PORT,
            )
            cursor = conn.cursor()
            query = f"SELECT name, value FROM {self.table_name}"
            cursor.execute(query)

            for record in cursor.fetchall():
                name, value = record
                parsed_value = parse_value(value)
                setattr(self, name, parsed_value)  # Définit chaque paramètre comme un attribut
            
            cursor.close()
            conn.close()
        except Exception as e:
            raise RuntimeError(f"Error loading configurations from table {self.table_name}: {e}")

# Utilisation de SimpleConfig
config = SimpleConfig(table_name="configurations")

# Exemple d'accès à une configuration
print("Simple Coonfifg Ready: ", config.__ZZZ__)
