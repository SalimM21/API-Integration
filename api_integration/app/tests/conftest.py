import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime, timedelta
import jwt
from app.config import TEST_JWT_SECRET, TEST_JWT_ALGORITHM, TEST_JWT_ISSUER, TEST_JWT_AUDIENCE

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
# JWT Fixtures
# ---------------------------
def _generate_jwt(username: str, roles: list, expire_minutes: int = 60):
    """
    Génère un JWT signé pour les tests.
    """
    now = datetime.utcnow()
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(minutes=expire_minutes),
        "iss": TEST_JWT_ISSUER,
        "aud": TEST_JWT_AUDIENCE,
        "realm_access": {"roles": roles}
    }
    token = jwt.encode(payload, TEST_JWT_SECRET, algorithm=TEST_JWT_ALGORITHM)
    return token

@pytest.fixture
def admin_token():
    return _generate_jwt("admin_user", roles=["admin"])

@pytest.fixture
def analyst_token():
    return _generate_jwt("analyst_user", roles=["analyst"])

@pytest.fixture
def expired_token():
    return _generate_jwt("expired_user", roles=["admin"], expire_minutes=-60)

@pytest.fixture
def invalid_signature_token():
    token = _generate_jwt("user_invalid", roles=["admin"])
    return token + "tampered"

# ---------------------------
# Headers fixtures
# ---------------------------
@pytest.fixture
def headers_admin(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def headers_analyst(analyst_token):
    return {"Authorization": f"Bearer {analyst_token}"}

@pytest.fixture
def headers_expired(expired_token):
    return {"Authorization": f"Bearer {expired_token}"}

@pytest.fixture
def headers_invalid(invalid_signature_token):
    return {"Authorization": f"Bearer {invalid_signature_token}"}

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
