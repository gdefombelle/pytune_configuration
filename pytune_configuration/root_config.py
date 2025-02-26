from dotenv import load_dotenv
import os

# Charger les variables d'environnement du fichier .env (si présent)
load_dotenv()

class RootConfig:
    """
    Configuration principale pour PyTune.
    - Les credentials sensibles sont lus depuis `.env`
    - Les paramètres réseau sont définis dans `docker-compose.yml`
    - En dev, des valeurs par défaut sont utilisées.
    """

    # Base de données (les valeurs réseau viennent de docker-compose.yml)
    DB_NAME = os.getenv("DB_NAME", "pianos")
    DB_HOST = os.getenv("DB_HOST", "localhost")  # Docker-compose doit définir `DB_HOST`
    DB_PORT = int(os.getenv("DB_PORT", 5432))

    # Identifiants de connexion (lus depuis .env)
    CONFIG_MANAGER_USER = os.getenv("CONFIG_MANAGER_USER", "config_manager")
    CONFIG_MANAGER_PWD = os.getenv("CONFIG_MANAGER_PWD")  # Défini dans .env
    FASTAPI_USER = os.getenv("FASTAPI_USER", "fastapi_user")
    FASTAPI_PWD = os.getenv("FASTAPI_PWD")  # Défini dans .env

    # Redis (Docker-compose doit définir `REDIS_HOST`)
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_URL = f"redis://{REDIS_HOST}:6379"

    def __init__(self):
        """
        Vérification des variables critiques pour éviter des erreurs en production.
        """
        if not self.CONFIG_MANAGER_PWD:
            raise ValueError("❌ ERREUR: La variable d'environnement 'CONFIG_MANAGER_PWD' est manquante !")
        if not self.FASTAPI_PWD:
            raise ValueError("❌ ERREUR: La variable d'environnement 'FASTAPI_PWD' est manquante !")

# Expose une instance de RootConfig pour usage global
root_config = RootConfig()
