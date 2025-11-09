# ==========================
# Étape 1 : Builder
# ==========================
FROM python:3.12-slim as builder

# Variables d'environnement pour Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Créer le répertoire de l'application
WORKDIR /app

# Copier les fichiers requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# ==========================
# Étape 2 : Image finale
# ==========================
FROM python:3.12-slim

WORKDIR /app

# Copier les dépendances depuis le builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
# Copier les scripts d'exécution (console_scripts comme uvicorn)
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Exposer le port de l'API
EXPOSE 8000

# Commande par défaut pour démarrer FastAPI avec Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
