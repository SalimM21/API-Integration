"""
Génération automatique de payloads aléatoires pour endpoints /score et /fraude.

- Permet de créer N transactions clients et N profils clients
- Sauvegarde au format JSON pour Postman ou tests
"""

import json
import random
from datetime import datetime, timedelta
import uuid

# ---------------------------
# Paramètres
# ---------------------------
NUM_CLIENTS = 20
NUM_TRANSACTIONS = 50
OUTPUT_SCORE_FILE = "fake_score_payloads.json"
OUTPUT_FRAUDE_FILE = "fake_fraude_payloads.json"

# ---------------------------
# Fonctions utilitaires
# ---------------------------
def random_date(start, end):
    """Retourne une date aléatoire entre start et end (datetime)."""
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)

def random_client_id():
    return f"C{random.randint(1000,9999)}"

def random_transaction_id():
    return f"T{uuid.uuid4().hex[:8]}"

def random_type_transaction():
    return random.choice(["virement", "paiement", "retrait", "achat_en_ligne"])

def random_devise():
    return random.choice(["USD", "EUR", "MAD", "GBP", "JPY"])

# ---------------------------
# Génération payloads /score
# ---------------------------
score_payloads = []
for _ in range(NUM_CLIENTS):
    payload = {
        "client_id": random_client_id(),
        "age": random.randint(18, 75),
        "revenu": random.randint(15000, 150000),
        "historique_impaye": random.randint(0, 5),
        "montant_credit": random.randint(1000, 50000)
    }
    score_payloads.append(payload)

# Sauvegarde JSON
with open(OUTPUT_SCORE_FILE, "w", encoding="utf-8") as f:
    json.dump(score_payloads, f, indent=2)
print(f"[+] {len(score_payloads)} payloads /score générés dans {OUTPUT_SCORE_FILE}")

# ---------------------------
# Génération payloads /fraude
# ---------------------------
fraude_payloads = []
now = datetime.utcnow()
for _ in range(NUM_TRANSACTIONS):
    payload = {
        "transaction_id": random_transaction_id(),
        "client_id": random.choice(score_payloads)["client_id"],
        "montant": round(random.uniform(10, 5000), 2),
        "type": random_type_transaction(),
        "devise": random_devise(),
        "date_transaction": random_date(now - timedelta(days=30), now).isoformat()
    }
    fraude_payloads.append(payload)

# Sauvegarde JSON
with open(OUTPUT_FRAUDE_FILE, "w", encoding="utf-8") as f:
    json.dump(fraude_payloads, f, indent=2)
print(f"[+] {len(fraude_payloads)} payloads /fraude générés dans {OUTPUT_FRAUDE_FILE}")
