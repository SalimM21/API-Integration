import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

# --- Charger le fichier .env ---
load_dotenv()

# --- API & Application ---
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# --- Elasticsearch (ELK) ---
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "localhost")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))
ELASTIC_USER = os.getenv("ELASTIC_USER", "")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", "")

# Création du client Elasticsearch
if ELASTIC_USER and ELASTIC_PASSWORD:
    es_client = Elasticsearch(
        hosts=[{"host": ELASTIC_HOST, "port": ELASTIC_PORT}],
        http_auth=(ELASTIC_USER, ELASTIC_PASSWORD)
    )
else:
    es_client = Elasticsearch(
        hosts=[{"host": ELASTIC_HOST, "port": ELASTIC_PORT}]
    )

# --- Keycloak / OAuth2 ---
KEYCLOAK_ISSUER = os.getenv("KEYCLOAK_ISSUER", "https://keycloak.example.com/realms/myrealm")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "my-client-id")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "secret")
KEYCLOAK_ALGORITHMS = os.getenv("KEYCLOAK_ALGORITHMS", "RS256")  # Signature JWT

# --- Modèles ML ---
SCORING_MODEL_PATH = os.getenv("SCORING_MODEL_PATH", "app/models/scoring_model.onnx")
FRAUDE_MODEL_PATH = os.getenv("FRAUDE_MODEL_PATH", "app/models/fraude_model.onnx")

# --- Seuils et règles ---
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", 0.5))
FRAUDE_ALERT_THRESHOLD = float(os.getenv("FRAUDE_ALERT_THRESHOLD", 0.7))

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_INDEX = os.getenv("LOG_INDEX", "api-logs")

# --- Autres paramètres ---
MAX_PAYLOAD_SIZE = int(os.getenv("MAX_PAYLOAD_SIZE", 1024 * 1024))  # 1MB par défaut

# --- Vérification minimale à l'import ---
def check_config():
    missing = []
    for var in ["KEYCLOAK_ISSUER", "KEYCLOAK_CLIENT_ID", "SCORING_MODEL_PATH", "FRAUDE_MODEL_PATH"]:
        if not globals().get(var):
            missing.append(var)
    if missing:
        raise RuntimeError(f"Variables d'environnement manquantes: {missing}")

check_config()
