#!/bin/bash

# ==========================
# run.sh - Lancer API + Tests
# ==========================

# Charger les variables d'environnement
if [ -f .env ]; then
    export $(cat .env | xargs)
    echo "[INFO] Variables d'environnement chargées depuis .env"
else
    echo "[WARN] Fichier .env non trouvé, utilisez .env.example"
fi

# ==========================
# Construire et lancer l'API
# ==========================
echo "[INFO] Démarrage de l'API FastAPI..."
docker-compose up -d api
sleep 5  # Attendre que l'API démarre

# Vérifier si l'API répond
echo "[INFO] Vérification de l'API..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
if [ "$HTTP_CODE" -eq 200 ]; then
    echo "[INFO] API accessible à http://localhost:8000/docs"
else
    echo "[ERROR] API non accessible, code HTTP: $HTTP_CODE"
fi

# ==========================
# Lancer les tests unitaires
# ==========================
echo "[INFO] Exécution des tests unitaires..."
pytest -v --maxfail=1 --disable-warnings

# ==========================
# Générer des transactions fictives
# ==========================
echo "[INFO] Génération de transactions aléatoires..."
python generate_fake_transactions.py

# ==========================
# Nettoyage (optionnel)
# ==========================
echo "[INFO] Pour arrêter l'API: docker-compose down"
