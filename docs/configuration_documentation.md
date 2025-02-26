# PyTune Configuration - Documentation et README

## 📌 Introduction
`pytune_configuration` est un package Python permettant la gestion centralisée des configurations pour les différents services de PyTune. Il s'appuie sur **PostgreSQL** pour stocker et récupérer les paramètres de configuration et **Redis** pour la gestion des mises à jour dynamiques.

---

## 📁 Structure du projet
```
pytune_configuration/
│── pytune_configuration/  # Package source
│   ├── __init__.py
│   ├── config_service.py   # Service principal de gestion des configurations
│   ├── root_config.py      # Configuration principale (lecture .env et variables système)
│   ├── postgres_service.py # Connexion à PostgreSQL
│   ├── redis_config.py     # Connexion à Redis
│   ├── utils.py            # Fonctions utilitaires
│── tests/                 # Tests unitaires
│── .gitignore             # Fichiers ignorés par Git
│── .env.example           # Exemple des variables d'environnement
│── pyproject.toml         # Fichier Poetry (gestion des dépendances)
│── poetry.lock            # Fichier de verrouillage des dépendances
│── README.md              # Documentation du package
│── docs/                  # Documentation détaillée
```

---

## 🔧 Installation

### 1️⃣ Installation via Poetry
```bash
poetry add git+https://github.com/gdefombelle/pytune_configuration.git
```

### 2️⃣ Configuration des variables d'environnement
Créez un fichier `.env` dans le projet et définissez les variables nécessaires :

```
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=pianos
CONFIG_MANAGER_USER=config_manager
CONFIG_MANAGER_PWD=SuperSecretPassword
FASTAPI_USER=fastapi_user
FASTAPI_PWD=AnotherSecretPassword
REDIS_HOST=127.0.0.1
OPENSEARCH_HOST=http://localhost:9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=AnotherSecretPassword
```
> 📌 **Ne jamais committer le fichier `.env` dans Git !**

---

## 🚀 Utilisation

### 🔹 Charger les configurations

```python
from pytune_configuration.config_service import Config

async def main():
    config = await Config().initialize()
    print(config.DB_HOST)

import asyncio
asyncio.run(main())
```

### 🔹 Récupérer une configuration spécifique
```python
config_value = config.MY_CONFIG_KEY
```

### 🔹 Ajouter une nouvelle configuration
```python
await config.add_config_to_db("NEW_CONFIG", "some_value", "Nouvelle config ajoutée")
```

### 🔹 Mettre à jour une configuration
```python
await config.update_config_in_db("EXISTING_CONFIG", "updated_value", "Mise à jour")
```

### 🔹 Supprimer une configuration
```python
await config.delete_config_in_db("EXISTING_CONFIG")
```

---

## 🏗️ Architecture
### 1️⃣ **Chargement des configurations**
- La classe `RootConfig` charge les **valeurs de base** depuis `.env` ou **les variables d’environnement**.
- La classe `Config` récupère les **configurations dynamiques** depuis PostgreSQL.
- Les **changements de configuration** sont propagés en temps réel via **Redis**.

### 2️⃣ **Gestion des configurations avec PostgreSQL**
Toutes les configurations sont stockées dans une table `configurations` avec la structure suivante :
```sql
CREATE TABLE configurations (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT
);
```

### 3️⃣ **Mises à jour dynamiques avec Redis**
Lorsqu’un paramètre est mis à jour dans la base de données, un message est envoyé à Redis sur le canal `config_change` pour informer les services en écoute.

---

## 📜 Bonnes pratiques
✅ Toujours utiliser `await config.get_config()` pour éviter des incohérences.
✅ Ne stocker **aucun mot de passe en dur** dans le code, tout passe par `.env`.
✅ Utiliser PostgreSQL pour les configurations persistantes et Redis pour les mises à jour en temps réel.
✅ En **développement**, charger les valeurs depuis `.env`.
✅ En **production**, définir les variables dans `docker-compose.prod.yml`.

---

## 🔗 Liens utiles
- [Documentation officielle de PostgreSQL](https://www.postgresql.org/docs/)
- [Documentation officielle de Redis](https://redis.io/docs/)
- [Documentation FastAPI](https://fastapi.tiangolo.com/)

---

## 📌 Auteur
Projet développé par **Nicolas de Fombelle** - PyTune Project 🎵

🌍 **Site Web :** [pytune.com](https://pytune.com)  
🐙 **GitHub :** [gdefombelle](https://github.com/gdefombelle)  
✉️ **Email :** contact@pytune.com

