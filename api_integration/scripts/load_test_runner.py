"""
Test de charge / stress test pour l'API FastAPI
Endpoints : /score et /fraude
Utilise HTTPX async pour simuler des requêtes concurrentes
"""

import asyncio
import httpx
import json
import random
from datetime import datetime, timedelta

# ---------------------------
# Config
# ---------------------------
API_BASE_URL = "http://localhost:8000"
NUM_REQUESTS = 100
CONCURRENCY = 10

# Fichiers JSON générés avec generate_fake_transactions.py
SCORE_PAYLOAD_FILE = "fake_score_payloads.json"
FRAUDE_PAYLOAD_FILE = "fake_fraude_payloads.json"

# Token mocké (à remplacer si auth réel)
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fake_token"

HEADERS = {
    "Authorization": AUTH_TOKEN,
    "Content-Type": "application/json"
}

# ---------------------------
# Charger payloads
# ---------------------------
with open(SCORE_PAYLOAD_FILE, "r", encoding="utf-8") as f:
    score_payloads = json.load(f)

with open(FRAUDE_PAYLOAD_FILE, "r", encoding="utf-8") as f:
    fraude_payloads = json.load(f)

# ---------------------------
# Fonctions async
# ---------------------------
async def post_score(client: httpx.AsyncClient, payload: dict):
    try:
        resp = await client.post(f"{API_BASE_URL}/score", json=payload, headers=HEADERS, timeout=10)
        return resp.status_code, resp.json() if resp.status_code == 200 else resp.text
    except Exception as e:
        return "ERROR", str(e)

async def post_fraude(client: httpx.AsyncClient, payload: dict):
    try:
        resp = await client.post(f"{API_BASE_URL}/fraude", json=payload, headers=HEADERS, timeout=10)
        return resp.status_code, resp.json() if resp.status_code == 200 else resp.text
    except Exception as e:
        return "ERROR", str(e)

async def run_load_test():
    """
    Exécute les requêtes en parallèle (concurrent)
    """
    async with httpx.AsyncClient() as client:
        tasks = []
        for _ in range(NUM_REQUESTS):
            # Choisir aléatoirement score ou fraude
            if random.random() < 0.5:
                payload = random.choice(score_payloads)
                tasks.append(post_score(client, payload))
            else:
                payload = random.choice(fraude_payloads)
                tasks.append(post_fraude(client, payload))
        
        # Chunk par concurrency
        results = []
        for i in range(0, len(tasks), CONCURRENCY):
            chunk = tasks[i:i+CONCURRENCY]
            res = await asyncio.gather(*chunk)
            results.extend(res)
            print(f"[{i+len(chunk)}/{NUM_REQUESTS}] Batch terminé")

        return results

# ---------------------------
# Entrée principale
# ---------------------------
if __name__ == "__main__":
    print("[*] Démarrage test de charge")
    start_time = datetime.now()
    results = asyncio.run(run_load_test())
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Statistiques simples
    success = sum(1 for status, _ in results if status == 200)
    errors = sum(1 for status, _ in results if status != 200)
    print(f"[+] Test terminé en {duration:.2f}s : {success} succès, {errors} erreurs")
