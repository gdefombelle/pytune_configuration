PyTune Configuration - Documentation et README
📌 Introduction
pytune_configuration est un package très léger pour charger les configurations de PyTune depuis PostgreSQL.

Le package expose une seule classe principale : SimpleConfig.

Aucune synchronisation dynamique via Redis : les paramètres sont lus au démarrage du service.

📁 Structure du projet
bash
Copy
Edit
pytune_configuration/
│── pytune_configuration/
│   ├── __init__.py
│   ├── simple_config.py    # Classe SimpleConfig
│   ├── root_config.py      # Paramètres principaux (DB, credentials, etc.)
│   ├── utils.py            # Utilitaires (parse_value, etc.)
│── pyproject.toml          # Dépendances (Poetry)
│── README.md               # Documentation rapide
🔧 Installation
1️⃣ Installation via Poetry
bash
Copy
Edit
poetry add git+https://github.com/gdefombelle/pytune_configuration.git
2️⃣ Variables d'environnement nécessaires
Pas de .env dans ce package, mais il attend certaines variables dans l'environnement système :

ini
Copy
Edit
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=pianos
CONFIG_MANAGER_USER=config_manager
CONFIG_MANAGER_PWD=SuperSecretPassword
REDIS_URL=redis://127.0.0.1:6379
RABBIT_BROKER_URL=pyamqp://admin:MyStr0ngP@ss2024!@localhost//
RABBIT_BACKEND=redis://127.0.0.1:6379/0
📌 En général ces variables sont fournies par le conteneur Docker.

🚀 Utilisation
🔹 Charger la configuration
python
Copy
Edit
from pytune_configuration.simple_config import SimpleConfig

config = SimpleConfig(table_name="configurations")
🔹 Accéder aux paramètres
Après chargement, chaque paramètre est disponible comme attribut Python :

python
Copy
Edit
print(config.DB_HOST)
print(config.OPENSEARCH_HOST)
print(config.__ZZZ__)  # Exemple d'un paramètre custom
🔹 Personnaliser la table PostgreSQL
Par défaut, SimpleConfig lit la table configurations, mais tu peux spécifier une autre table :

python
Copy
Edit
custom_config = SimpleConfig(table_name="my_custom_config_table")
🏗️ Fonctionnement interne
Connexion PostgreSQL synchrone via psycopg2.

Chargement de toutes les paires (name, value) de la table donnée.

Dynamique : chaque clé devient un attribut Python de l'instance config.

Pas de Redis, pas de refresh automatique = fiable, simple et rapide.

📜 Bonnes pratiques
✅ Charger la config une seule fois au lancement du service.
✅ Mettre à jour la base PostgreSQL si des paramètres changent, puis redémarrer le service si nécessaire.
✅ Ne pas modifier directement les attributs Python du config, toujours passer par la base PostgreSQL.

🔗 Liens utiles
Documentation officielle PostgreSQL

Poetry

📌 Auteur
Développé pour PyTune Project 🎵 par
Gabriel de Fombelle
🌍 Site Web : pytune.com
✉️ Email : contact@pytune.com

Exemple ultra-minimal :
python
Copy
Edit
from pytune_configuration.simple_config import SimpleConfig

config = SimpleConfig()

print(config.SOME_PARAMETER)  # Accède à une config nommée "SOME_PARAMETER"
