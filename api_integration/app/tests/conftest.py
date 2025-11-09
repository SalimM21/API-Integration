import pytest
from fastapi.testclient import TestClient
import os
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# Charger les variables d'environnement de test
os.environ['ENV'] = 'test'
load_dotenv('.env.test', override=True)

# Mock des services externes avant l'import de l'application
mock_es = MagicMock()
mock_jwks = MagicMock()
mock_jwks.json.return_value = {
    "keys": [{
        "kid": "test-key",
        "kty": "RSA",
        "n": "test",
        "e": "AQAB"
    }]
}

with patch('elasticsearch.Elasticsearch', return_value=mock_es), \
     patch('requests.get', return_value=mock_jwks):
    from app.main import app

# ---------------------------
# Client FastAPI global
# ---------------------------
@pytest.fixture(scope="session")
def client():
    """
    Fixture globale pour créer un TestClient FastAPI.
    """
    with TestClient(app) as c:
        yield c

# ---------------------------
# Exemple de fixture de payload standard
# ---------------------------
@pytest.fixture
def example_score_payload():
    return {
        "client_id": "C100",
        "age": 35,
        "revenu": 55000,
        "historique_impaye": 0,
        "montant_credit": 15000
    }

@pytest.fixture
def example_fraude_payload():
    return {
        "transaction_id": "T100",
        "client_id": "C100",
        "montant": 1200,
        "type": "virement",
        "devise": "USD",
        "date_transaction": "2025-10-01T12:00:00"
    }
