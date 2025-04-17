# PyTune Configuration - README

## 📌 Introduction
# PyTune Configuration

## 📌 Introduction
`pytune_configuration` est un package Python **ultra-léger** pour charger les configurations de PyTune depuis une base **PostgreSQL**.

Le package expose une seule classe : **`SimpleConfig`**.

Pas de Redis, pas de rechargement dynamique : lecture au démarrage uniquement → **stable, rapide, fiable**.

---

## 📁 Structure

pytune_configuration/ │── pytune_configuration/ │ ├── init.py │ ├── simple_config.py │ ├── root_config.py │ ├── utils.py │── pyproject.toml │── README.md

yaml
Copy
Edit

---

## 🔧 Installation

### Avec Poetry
```bash
poetry add git+https://github.com/gdefombelle/pytune_configuration.git

⚙️ Variables attendues
Le package attend que ces variables soient présentes dans l'environnement système :

env
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
📌 En général injectées via Docker ou docker-compose.

🚀 Utilisation
Charger les configurations
python
Copy
Edit
from pytune_configuration.simple_config import SimpleConfig

config = SimpleConfig()
Accéder aux paramètres
Chaque paramètre devient un attribut :

python
Copy
Edit
print(config.DB_HOST)
print(config.OPENSEARCH_HOST)
print(config.MY_CUSTOM_PARAM)
🏗️ Fonctionnement
Connexion PostgreSQL avec psycopg2

Lecture de la table configurations (ou autre)

Chaque (name, value) devient un attribut dynamique

Pas de synchronisation en live, tout est local en mémoire 🧠.

📜 Bonnes pratiques
✅ Charger une seule instance de SimpleConfig par service.
✅ Modifier les configs uniquement via la base PostgreSQL.
✅ Redémarrer les services après modification si besoin.

🔗 Liens utiles
PostgreSQL Documentation

Poetry

📌 Auteur
Développé pour PyTune Project 🎵 par
Gabriel de Fombelle

🌍 pytune.com
✉️ contact@pytune.com