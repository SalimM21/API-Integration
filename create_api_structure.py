import os

# --- Définir la structure complète du projet ---
structure = {
    "api_integration": {
        "app": {
            "__init__.py": "",
            "main.py": "",
            "config.py": "",
            "models": {
                "__init__.py": "",
                "scoring_model.py": "",
                "fraude_model.py": ""
            },
            "schemas": {
                "__init__.py": "",
                "score_schema.py": "",
                "fraude_schema.py": ""
            },
            "routes": {
                "__init__.py": "",
                "score_routes.py": "",
                "fraude_routes.py": ""
            },
            "services": {
                "__init__.py": "",
                "scoring_service.py": "",
                "fraude_service.py": ""
            },
            "auth": {
                "__init__.py": "",
                "auth_handler.py": "",
                "rbac.py": ""
            },
            "logging": {
                "__init__.py": "",
                "elk_logger.py": "",
                "log_config.json": ""
            },
            "utils": {
                "__init__.py": "",
                "helpers.py": "",
                "validators.py": ""
            },
            "security": {
                "__init__.py": "",
                "token_utils.py": "",
                "keycloak_client.py": ""
            },
            "tests": {
                "__init__.py": "",
                "test_score_endpoint.py": "",
                "test_fraude_endpoint.py": "",
                "test_auth_security.py": "",
                "test_injection.py": "",
                "test_logger.py": "",
                "conftest.py": ""
            }
        },
        "scripts": {
            "generate_fake_transactions.py": "",
            "load_test_runner.py": ""
        },
        "postman": {
            "API_Scoring_Fraude.postman_collection.json": "",
            "API_Scoring_Fraude_Tests.postman_collection.json": "",
            "environment_local.postman_environment.json": "",
            "batch_profiles.json": ""
        },
        ".env.example": "",
        "requirements.txt": "",
        "Dockerfile": "",
        "docker-compose.yml": "",
        "config.yaml": "",
        "README.md": "",
        "run.sh": ""
    }
}


# --- Fonction récursive pour créer les dossiers et fichiers ---
def create_structure(base_path, structure_dict):
    for name, content in structure_dict.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, 'a').close()


# --- Exécution principale ---
if __name__ == "__main__":
    base_dir = os.getcwd()
    create_structure(base_dir, structure)
    print("✅ Arborescence du projet 'api_integration' créée avec succès !")
