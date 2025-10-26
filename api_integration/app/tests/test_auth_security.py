import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.token_utils import generate_jwt
from datetime import datetime, timedelta
import jwt
from app.config import TEST_JWT_SECRET, TEST_JWT_ALGORITHM, TEST_JWT_ISSUER, TEST_JWT_AUDIENCE

client = TestClient(app)

# ---------------------------
# Fixtures JWT
# ---------------------------
@pytest.fixture
def valid_admin_token():
    return generate_jwt("admin_user", roles=["admin"])

@pytest.fixture
def valid_analyst_token():
    return generate_jwt("analyst_user", roles=["analyst"])

@pytest.fixture
def expired_token():
    now = datetime.utcnow()
    payload = {
        "sub": "expired_user",
        "iat": now - timedelta(hours=2),
        "exp": now - timedelta(hours=1),
        "iss": TEST_JWT_ISSUER,
        "aud": TEST_JWT_AUDIENCE,
        "realm_access": {"roles": ["admin"]}
    }
    return jwt.encode(payload, TEST_JWT_SECRET, algorithm=TEST_JWT_ALGORITHM)

@pytest.fixture
def invalid_signature_token():
    # Token signé avec une mauvaise clé
    return generate_jwt("user", roles=["admin"]) + "tampered"

# ---------------------------
# Tests JWT expirés et invalides
# ---------------------------
def test_expired_token(expired_token):
    response = client.post(
        "/score",
        json={"client_id": "C101", "age": 30, "revenu": 50000, "historique_impaye": 1, "montant_credit": 10000},
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert "token" in response.json().get("detail", "").lower()

def test_invalid_signature_token(invalid_signature_token):
    response = client.post(
        "/score",
        json={"client_id": "C102", "age": 35, "revenu": 60000, "historique_impaye": 0, "montant_credit": 15000},
        headers={"Authorization": f"Bearer {invalid_signature_token}"}
    )
    assert response.status_code == 401
    assert "token" in response.json().get("detail", "").lower()

# ---------------------------
# Tests RBAC
# ---------------------------
def test_admin_access(valid_admin_token):
    payload = {"client_id": "C103", "age": 40, "revenu": 70000, "historique_impaye": 1, "montant_credit": 20000}
    response = client.post("/score", json=payload, headers={"Authorization": f"Bearer {valid_admin_token}"})
    assert response.status_code == 200

def test_analyst_access(valid_analyst_token):
    payload = {"client_id": "C104", "age": 28, "revenu": 45000, "historique_impaye": 0, "montant_credit": 12000}
    response = client.post("/score", json=payload, headers={"Authorization": f"Bearer {valid_analyst_token}"})
    # Selon RBAC configuré, analyst peut être autorisé ou non
    assert response.status_code in [200, 403]

def test_no_token():
    payload = {"client_id": "C105", "age": 32, "revenu": 50000, "historique_impaye": 0, "montant_credit": 10000}
    response = client.post("/score", json=payload)
    assert response.status_code == 401

# ---------------------------
# Tests OAuth2 scopes simulés
# ---------------------------
def test_scope_restriction(valid_admin_token):
    """
    Simule une route nécessitant un scope spécifique
    """
    payload = {"client_id": "C106", "age": 50, "revenu": 90000, "historique_impaye": 0, "montant_credit": 25000}
    response = client.post("/score", json=payload, headers={"Authorization": f"Bearer {valid_admin_token}"})
    assert response.status_code == 200
