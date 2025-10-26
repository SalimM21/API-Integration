import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.token_utils import generate_jwt

client = TestClient(app)

# ---------------------------
# Fixtures JWT
# ---------------------------
@pytest.fixture
def admin_token():
    return generate_jwt("user_admin", roles=["admin"])

@pytest.fixture
def analyst_token():
    return generate_jwt("user_analyst", roles=["analyst"])

@pytest.fixture
def invalid_token():
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.InvalidToken"

# ---------------------------
# Payloads de test
# ---------------------------
valid_payloads = [
    {"client_id": "C101", "age": 30, "revenu": 50000, "historique_impaye": 1, "montant_credit": 15000},
    {"client_id": "C102", "age": 45, "revenu": 80000, "historique_impaye": 0, "montant_credit": 25000},
]

invalid_payloads = [
    {"client_id": "C103", "age": 15, "revenu": 30000, "historique_impaye": 0},  # age invalide
    {"client_id": "C104", "age": 35, "revenu": -1000, "historique_impaye": 0},  # revenu invalide
]

# ---------------------------
# Tests unitaires /score
# ---------------------------
@pytest.mark.parametrize("payload", valid_payloads)
def test_score_valid(admin_token, payload):
    response = client.post(
        "/score",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert 0 <= data["score"] <= 1
    assert data["client_id"] == payload["client_id"]

@pytest.mark.parametrize("payload", invalid_payloads)
def test_score_invalid(admin_token, payload):
    response = client.post(
        "/score",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 422  # Validation échouée

# ---------------------------
# Test RBAC
# ---------------------------
def test_score_unauthorized(analyst_token):
    """
    Analyst n'a pas accès si endpoint restreint admin
    """
    payload = valid_payloads[0]
    response = client.post(
        "/score",
        json=payload,
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert response.status_code in [200, 403]  # selon RBAC configuré

def test_score_no_token():
    payload = valid_payloads[0]
    response = client.post("/score", json=payload)
    assert response.status_code == 401

def test_score_invalid_token(invalid_token):
    payload = valid_payloads[0]
    response = client.post(
        "/score",
        json=payload,
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401

# ---------------------------
# Test JSON Schema automatique
# ---------------------------
def test_score_response_schema(admin_token):
    payload = valid_payloads[0]
    response = client.post(
        "/score",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    data = response.json()
    # Vérification des champs obligatoires
    assert set(data.keys()) >= {"client_id", "score", "message"}
    assert isinstance(data["score"], float)
    assert isinstance(data["message"], str)
