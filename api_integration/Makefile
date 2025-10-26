# Makefile — tâches utilitaires pour dev / CI

.PHONY: help install start dev docker-build docker-up test test-quick lint fmt newman newman-report clean

SHELL := /bin/bash
PY := python3
PIP := pip
UVICORN_MODULE := app.main:app
HOST := 0.0.0.0
PORT := 8000

help:
	@echo "Usage:"
	@echo "  make install         # Installer dépendances (virtualenv recommandé)"
	@echo "  make start           # Lancer API (uvicorn) en production"
	@echo "  make dev             # Lancer API en mode dev (reload)"
	@echo "  make docker-build    # Build docker image"
	@echo "  make docker-up       # Lancer docker-compose (API + ELK + Keycloak)"
	@echo "  make test            # Lancer pytest complet"
	@echo "  make test-quick      # Lancer subset de tests rapides"
	@echo "  make lint            # Lancer flake8/isort/black checks (si installés)"
	@echo "  make fmt             # Formater le code (black/isort)"
	@echo "  make newman          # Lancer collection Postman via newman (requires npm/newman)"
	@echo "  make newman-report   # Lancer newman et générer rapport HTML"
	@echo "  make clean           # Nettoyer artefacts (pycache, venv caches, reports)"

install:
	$(PY) -m venv .venv
	. .venv/bin/activate && $(PIP) install --upgrade pip
	. .venv/bin/activate && $(PIP) install -r requirements.txt
	@echo "Virtualenv created at .venv — active with: source .venv/bin/activate"

start:
	UVICORN_WORKERS=$$([ -z "$${UVICORN_WORKERS}" ] && echo 1 || echo $$UVICORN_WORKERS) \
	. .venv/bin/activate && uvicorn $(UVICORN_MODULE) --host $(HOST) --port $(PORT) --workers $$UVICORN_WORKERS

dev:
	. .venv/bin/activate && uvicorn $(UVICORN_MODULE) --reload --host $(HOST) --port $(PORT)

docker-build:
	docker build -t ml-scoring-fraude-api .

docker-up:
	docker-compose up --build

test:
	. .venv/bin/activate && pytest -q --maxfail=1

test-quick:
	. .venv/bin/activate && pytest tests/test_score_endpoint.py tests/test_fraude_endpoint.py -q

lint:
	. .venv/bin/activate && (flake8 || true)

fmt:
	. .venv/bin/activate && (black . || true) && (isort . || true)

newman:
	# Requires npm and newman installed locally or via npx
	npx newman run ml_scoring_fraude_dynamic.postman_collection.json -e ml_scoring_env.postman_environment.json --iteration-count 100

newman-report:
	npx newman run ml_scoring_fraude_dynamic.postman_collection.json -e ml_scoring_env.postman_environment.json --iteration-count 100 --reporters cli,html --reporter-html-export newman-report.html

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .venv newman-report.html
