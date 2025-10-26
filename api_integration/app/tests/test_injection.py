"""
Tests de robustesse contre payloads malveillants (SQL injection, JSON injection, XSS-like payloads).
Objectifs :
 - Vérifier que les endpoints ne retournent pas d'erreur serveur (500) face à des payloads malveillants.
 - Vérifier que les validations Pydantic refusent les types invalides (ex : age non numérique).
 - Vérifier que l'API retourne des réponses claires (422/400/200) et ne divulgue pas de tracebacks.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.token_utils import generate_jwt

client = TestClient(app)

@pytest.fixture
def admin_token():
    return generate_jwt("admin_user", roles=["admin"])

# ---------------------------
# Cas 1 : injection SQL dans un champ numérique (age) -> doit donner 422 (validation)
# ---------------------------
def test_score_sql_injection_in_age(admin_token):
    malicious_payload = {
        "client_id": "C999",
        "age": "25; DROP TABLE users;",      # injection attempt in numeric field
        "revenu": 50000,
        "historique_impaye": 0,
        "montant_credit": 10000
    }
    resp = client.post("/score", json=malicious_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 422, f"Expected 422 for invalid age, got {resp.status_code}: {resp.text}"
    # No server error / no traceback
    assert resp.status_code < 500
    assert "traceback" not in resp.text.lower()

# ---------------------------
# Cas 2 : injection SQL dans un champ string (client_id) -> ne doit pas provoquer d'erreur 500
#          et l'API doit répondre proprement (200 ou 422 selon schéma). Ici client_id est a priori accepté.
# ---------------------------
def test_score_sql_injection_in_client_id(admin_token):
    malicious_client_id = "C101; DROP TABLE users; --"
    payload = {
        "client_id": malicious_client_id,
        "age": 35,
        "revenu": 45000,
        "historique_impaye": 1,
        "montant_credit": 15000
    }
    resp = client.post("/score", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    # Should not be a server error
    assert resp.status_code != 500, f"Server error on malicious client_id: {resp.status_code} {resp.text}"
    # If accepted, ensure returned client_id matches input (no unexpected mutation)
    if resp.status_code == 200:
        data = resp.json()
        assert data.get("client_id") == malicious_client_id

    assert "traceback" not in resp.text.lower()

# ---------------------------
# Cas 3 : JSON injection / malformed JSON value in montant for /fraude -> validation should reject
# ---------------------------
def test_fraude_json_injection_montant(admin_token):
    malicious_payload = {
        "transaction_id": "TSQL001",
        "client_id": "C200",
        "montant": "1000; DROP TABLE transactions;",  # montant should be numeric -> validation error
        "type": "virement",
        "devise": "USD",
        "date_transaction": "2025-10-01T12:00:00",
    }
    resp = client.post("/fraude", json=malicious_payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 422, f"Expected 422 for invalid montant, got {resp.status_code}"
    assert "traceback" not in resp.text.lower()

# ---------------------------
# Cas 4 : XSS-like payloads in string fields -> API should return safely and not produce server error
# ---------------------------
@pytest.mark.parametrize("field_name", ["client_id", "transaction_id"])
def test_xss_like_payloads_do_not_crash(admin_token, field_name):
    malicious_value = "<script>alert('xss')</script>"
    payload_score = {
        "client_id": malicious_value if field_name == "client_id" else "C300",
        "age": 30,
        "revenu": 30000,
        "historique_impaye": 0
    }
    payload_fraude = {
        "transaction_id": malicious_value if field_name == "transaction_id" else "T300",
        "client_id": "C300",
        "montant": 1000,
        "type": "paiement",
        "devise": "EUR",
        "date_transaction": "2025-10-01T12:00:00"
    }

    # Score endpoint
    resp_s = client.post("/score", json=payload_score, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp_s.status_code != 500
    assert "traceback" not in resp_s.text.lower()
    if resp_s.status_code == 200:
        # ensure response JSON is valid and doesn't contain raw HTML execution (it's JSON)
        data = resp_s.json()
        assert isinstance(data, dict)

    # Fraude endpoint
    resp_f = client.post("/fraude", json=payload_fraude, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp_f.status_code != 500
    assert "traceback" not in resp_f.text.lower()
    if resp_f.status_code == 200:
        data = resp_f.json()
        assert isinstance(data, dict)

# ---------------------------
# Cas 5 : Suite de payloads malveillants (divers) -> aucun ne doit causer d'HTTP 500
# ---------------------------
def test_bulk_malicious_payloads_do_not_cause_500(admin_token):
    malicious_payloads = [
        # SQL-style attempts in various fields
        ("/score", {"client_id": "C400", "age": 40, "revenu": "50000; DROP", "historique_impaye": 0}),
        ("/score", {"client_id": "C401; --", "age": 45, "revenu": 60000, "historique_impaye": 0}),
        ("/fraude", {"transaction_id": "T400", "client_id": "C400", "montant": 1000, "type": "virement; DROP", "devise": "USD"}),
        ("/fraude", {"transaction_id": "T401; --", "client_id": "C401", "montant": 2000, "type": "paiement", "devise": "EUR"}),
        # Large payload attempt
        ("/score", {"client_id": "C_BIG", "age": 30, "revenu": 1e9, "historique_impaye": 0}),
    ]
    for path, payload in malicious_payloads:
        resp = client.post(path, json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code != 500, f"500 error for payload on {path}: {payload} -> {resp.text}"
        assert "traceback" not in resp.text.lower()

# ---------------------------
# Cas 6 : Sanity check - ensure validation rejects obviously malformed JSON structures
# ---------------------------
def test_malformed_json_body(admin_token):
    # Send a raw invalid JSON string (simulating broken client)
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    resp = client.post("/score", data='{"age": 30, "revenu": 50000, "historique_impaye": 0', headers=headers)  # missing closing brace
    # Starlette/FastAPI should return 400 Bad Request for malformed JSON
    assert resp.status_code in (400, 422)
    assert "traceback" not in resp.text.lower()


# 7. Injection dans champs numériques limites / négatifs

@pytest.mark.parametrize("field,value", [("age",-1), ("revenu",-1000), ("montant",-500)])
def test_negative_numbers_do_not_crash(admin_token, field, value):
    payload_score = {"client_id":"C500", "age":30, "revenu":50000, "historique_impaye":0, "montant_credit":15000}
    payload_fraude = {"transaction_id":"T500","client_id":"C500","montant":1000,"type":"virement","devise":"USD","date_transaction":"2025-10-01T12:00:00"}
    payload_score[field] = value if field in payload_score else payload_score["age"]
    payload_fraude[field] = value if field in payload_fraude else payload_fraude["montant"]
    
    resp_s = client.post("/score", json=payload_score, headers={"Authorization": f"Bearer {admin_token}"})
    resp_f = client.post("/fraude", json=payload_fraude, headers={"Authorization": f"Bearer {admin_token}"})
    
    # Doit renvoyer 422 et ne jamais 500
    assert resp_s.status_code in (422,200)
    assert resp_f.status_code in (422,200)


# 8. Payloads extrêmement volumineux (Stress / Fuzzing)

def test_large_payloads(admin_token):
    large_client_id = "C" + "X"*10000  # 10k chars
    payload = {"client_id": large_client_id, "age":35, "revenu":50000, "historique_impaye":0, "montant_credit":10000}
    resp = client.post("/score", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code != 500
    assert "traceback" not in resp.text.lower()

# 9.Injection JSON imbriquée / types inattendus

def test_nested_json_injection(admin_token):
    payload = {
        "client_id": "C600",
        "age": {"$gt": 0},   # tentative Mongo-like injection
        "revenu": 50000,
        "historique_impaye": 0,
        "montant_credit": 15000
    }
    resp = client.post("/score", json=payload, headers={"Authorization": f"Bearer {admin_token}"})
    # Pydantic doit rejeter ça
    assert resp.status_code == 422

# 10. Injection caractères spéciaux / Unicode

@pytest.mark.parametrize("field,value", [("client_id","C\u202E1234"), ("transaction_id","\u202EXYZ")])
def test_unicode_and_special_chars(admin_token, field, value):
    payload_score = {"client_id":"C700", "age":30, "revenu":50000, "historique_impaye":0, "montant_credit":15000}
    payload_fraude = {"transaction_id":"T700","client_id":"C700","montant":1000,"type":"virement","devise":"USD","date_transaction":"2025-10-01T12:00:00"}
    payload_score[field] = value if field in payload_score else payload_score["client_id"]
    payload_fraude[field] = value if field in payload_fraude else payload_fraude["transaction_id"]

    resp_s = client.post("/score", json=payload_score, headers={"Authorization": f"Bearer {admin_token}"})
    resp_f = client.post("/fraude", json=payload_fraude, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp_s.status_code != 500
    assert resp_f.status_code != 500

# 11. Combiner plusieurs attaques en batch (SQL + JSON + XSS)
def test_combined_attack_payloads(admin_token):
    attack_payloads = [
        {"client_id":"C800; DROP TABLE users;","age":30,"revenu":50000,"historique_impaye":0,"montant_credit":15000},
        {"client_id":"<script>alert('xss')</script>","age":"35; DELETE FROM transactions","revenu":60000,"historique_impaye":1,"montant_credit":20000},
        {"transaction_id":"T800","client_id":"C800","montant":"1000; DROP TABLE transactions;","type":"virement","devise":"USD","date_transaction":"2025-10-01T12:00:00"}
    ]
    endpoints = ["/score", "/score", "/fraude"]
    for ep, payload in zip(endpoints, attack_payloads):
        resp = client.post(ep, json=payload, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code != 500
        assert "traceback" not in resp.text.lower()
