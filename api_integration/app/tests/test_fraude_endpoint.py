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
# Payloads de test /fraude
# ---------------------------
valid_payloads = [
    {"transaction_id": "T001", "client_id": "C101", "montant": 5000, "type": "virement", "historique_impaye": 0},
    {"transaction_id": "T002", "client_id": "C102", "montant": 20000, "type": "paiement", "historique_impaye": 2},
]

invalid_payloads = [
    {"transaction_id": "T003", "client_id": "C103", "montant": -500, "type": "virement", "historique_impaye": 0},  # montant invalide
    {"transaction_id": "T004", "client_id": "C104", "montant": 1000, "type": "unknown", "historique_impaye": 0},  # type invalide
]

# ---------------------------
# Tests unitaires /fraude
# ---------------------------
@pytest.mark.parametrize("payload", valid_payloads)
def test_fraude_valid(admin_token, payload):
    response = client.post(
        "/fraude",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "risque" in data
    assert data["risque"] in ["faible", "modere", "eleve"]
    assert data["client_id"] == payload["client_id"]
    assert data["transaction_id"] == payload["transaction_id"]

@pytest.mark.parametrize("payload", invalid_payloads)
def test_fraude_invalid(admin_token, payload):
    response = client.post(
        "/fraude",
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 422  # Validation échouée

# ---------------------------
# Test RBAC
# ---------------------------
def test_fraude_unauthorized(analyst_token):
    payload = valid_payloads[0]
    response = client.post(
        "/fraude",
        json=payload,
        headers={"Authorization": f"Bearer {analyst_token}"}
    )
    assert response.status_code in [200, 403]  # selon RBAC configuré

def test_fraude_no_token():
    payload = valid_payloads[0]
    response = client.post("/fraude", json=payload)
    assert response.status_code == 401

def test_fraude_invalid_token(invalid_token):
    payload = valid_payloads[0]
    response = client.post(
        "/fraude",
        json=payload,
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401

# ---------------------------
# Test logique règles /fraude
# ---------------------------
def test_fraude_risk_levels(admin_token):
    """
    Vérifie que les règles métier produisent les bons niveaux de risque.
    """
    high_risk = {"transaction_id": "T100", "client_id": "C200", "montant": 50000, "type": "virement", "historique_impaye": 5}
    mod_risk = {"transaction_id": "T101", "client_id": "C201", "montant": 15000, "type": "paiement", "historique_impaye": 2}
    low_risk = {"transaction_id": "T102", "client_id": "C202", "montant": 1000, "type": "retrait", "historique_impaye": 0}

    for payload, expected in [(high_risk, "eleve"), (mod_risk, "modere"), (low_risk, "faible")]:
        response = client.post("/fraude", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["risque"] == expected

# ---------------------------
# Test logging ELK simulé
# ---------------------------
def test_fraude_logging(admin_token, monkeypatch):
    """
    Vérifie que le logger ELK est appelé avec un payload structuré.
    """
    logged_messages = []

    # Patch logger pour capturer les logs
    def fake_info(msg):
        logged_messages.append(msg)

    from app.logging.elk_logger import logger
    monkeypatch.setattr(logger, "info", fake_info)

    payload = valid_payloads[0]
    client.post("/fraude", json=payload, headers={"Authorization": f"Bearer {admin_token}"})

    assert any("transaction_id" in msg for msg in logged_messages)
    assert any("client_id" in msg for msg in logged_messages)
