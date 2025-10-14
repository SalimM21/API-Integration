# 📘 Sections — Logging & Monitoring, Tests, Postman

## 🧾 Logging & Monitoring

### Format des logs
- **Type** : JSON structuré  
- **Champs recommandés** :  
  - `timestamp` — date et heure de l’événement  
  - `level` — niveau du log (`INFO`, `ERROR`, `WARNING`, etc.)  
  - `logger` — nom du module ou service  
  - `message` — message principal du log  
  - `metadata` — métadonnées utiles (sans données sensibles)

### Destination
- **Système de stockage** : Elasticsearch  
- **Index dédié** : `api-logs-*`  
- **Visualisation** : Kibana (dashboards de suivi des requêtes, erreurs et performances)

### Exemples de métriques à exposer
- `auth_failures_count` → nombre d’échecs d’authentification  
- `forbidden_count` → accès refusés (erreurs 403)  
- `score_requests_count` → nombre total de requêtes `/score`  
- `fraud_requests_count` → nombre total de requêtes `/fraude`  
- `request_latency_ms` → latence moyenne par endpoint  

### Bonnes pratiques de logging
- 🚫 **Ne jamais** écrire de tokens JWT complets ni de données personnelles sensibles (PII) en clair.  
- ✅ Logger systématiquement :  
  - `request_id`  
  - `user_id` *(si autorisé et non sensible)*  
  - `endpoint`  
  - `status_code`  
  - `latence (ms)`  
- 🔁 Ajouter un **correlation id** (`X-Request-ID`) pour tracer les requêtes dans la stack complète (API → DB → monitoring).

---

## 🧪 Tests

### Framework
- **Outil principal** : `pytest`  
- **Objectif** : garantir la fiabilité des fonctionnalités métier et la sécurité des endpoints (auth, RBAC, validation de payloads).

### Cas à couvrir (exemples)
| Catégorie | Description | Code attendu |
|------------|--------------|---------------|
| 🔐 Authentification | JWT expirés / mal signés | `401 Unauthorized` |
| 👥 RBAC | Rôle insuffisant pour accéder à une ressource | `403 Forbidden` |
| ⚙️ Métier | Validation des règles de scoring et fraude (valeurs limites, outliers) | `200 OK` / `400 Bad Request` |
| 🧱 Sécurité | Payloads malveillants (injection SQL/NoSQL, structures invalides) | `400` / `422` |

Exemple de test Pytest :
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_score_requires_role_admin_or_analyst():
    token_viewer = "Bearer <jwt_with_viewer_role>"
    resp = client.post('/score', json={"age": 30}, headers={"Authorization": token_viewer})
    assert resp.status_code == 403
```

---

## 🧰 Postman

### Fichiers associés
- **Collection principale** : `postman/API_Scoring_Fraude.postman_collection.json`  
- **Tests automatisés** : `postman/API_Scoring_Fraude_Tests.postman_collection.json`  
- **Environnement local** : `postman/environment_local.postman_environment.json`

### Contenu recommandé
Inclure dans les scripts Postman :
- 🔁 **Génération / rafraîchissement de tokens** via Keycloak ou Okta.  
- ⏳ **Tests d’expiration de JWT** pour vérifier la gestion des tokens invalides.  
- 👥 **Tests RBAC** pour s’assurer qu’un utilisateur sans rôle suffisant reçoit bien une erreur `403`.  

Exemple de structure Postman :
```
API_Scoring_Fraude.postman_collection.json
├── Authentification
│   ├── Login Keycloak
│   ├── Refresh Token
├── Scoring
│   ├── POST /score (admin)
│   └── POST /score (viewer) — doit échouer
├── Fraude
│   ├── POST /fraude (admin)
│   └── POST /fraude (analyst)
└── Admin
    └── GET /admin/logs
```
