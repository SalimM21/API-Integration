#!/bin/bash

# Script de configuration du Feature Store Feast
# Utilisation: ./setup-feast.sh

set -e

echo "🍽️  Configuration du Feature Store Feast"
echo "========================================"

# Vérifier que les services sont disponibles
echo "1️⃣ Vérification des services..."

# PostgreSQL
if kubectl exec -n storage postgresql-0 -- pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
  echo "✅ PostgreSQL accessible"
else
  echo "❌ PostgreSQL non accessible"
  exit 1
fi

# Redis (si déployé)
if kubectl get svc redis-service > /dev/null 2>&1; then
  echo "✅ Redis service trouvé"
else
  echo "⚠️  Redis service non trouvé - déploiement séparé requis"
fi

# MinIO pour le registry
if kubectl get svc minio-service -n storage > /dev/null 2>&1; then
  echo "✅ MinIO accessible"
else
  echo "❌ MinIO non accessible"
  exit 1
fi

echo ""

# Créer le schéma Feast dans PostgreSQL
echo "2️⃣ Configuration de la base de données PostgreSQL..."
kubectl exec -n storage postgresql-0 -- bash -c "PGPASSWORD=iaxVrMCI8y psql -U postgres -d scoring_db -c 'CREATE SCHEMA IF NOT EXISTS feast;'"

echo "✅ Schema 'feast' créé"

echo ""

# Déployer Feast
echo "3️⃣ Déploiement de Feast..."
kubectl apply -f feast-configmap.yaml
kubectl apply -f feast-deployment.yaml

echo "✅ Déploiement appliqué"

# Attendre que Feast soit prêt
echo "4️⃣ Attente du démarrage de Feast..."
kubectl wait --for=condition=ready pod -l app=feast-feature-server --timeout=300s

echo "✅ Feast opérationnel"

echo ""

# Initialiser le Feature Store
echo "5️⃣ Initialisation du Feature Store..."

# Créer un job temporaire pour l'initialisation
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: feast-init-job
  namespace: default
spec:
  template:
    spec:
      containers:
      - name: feast-init
        image: feastdev/feature-server:0.34.0
        command: ["feast", "apply"]
        env:
        - name: FEAST_REPO_PATH
          value: "/opt/feast/repo"
        volumeMounts:
        - name: feast-repo
          mountPath: /opt/feast/repo
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
      volumes:
      - name: feast-repo
        configMap:
          name: feast-feature-repo
      restartPolicy: Never
EOF

# Attendre la fin du job
echo "Attente de l'initialisation..."
kubectl wait --for=condition=complete job/feast-init-job --timeout=300s

# Vérifier les logs
echo "Vérification des logs d'initialisation:"
kubectl logs job/feast-init-job

# Nettoyer le job
kubectl delete job feast-init-job

echo ""

# Tester le Feature Store
echo "6️⃣ Tests du Feature Store..."

# Port-forward pour les tests
kubectl port-forward svc/feast-feature-server-service 80:80 &
PORT_FORWARD_PID=$!

sleep 5

# Test de santé
if curl -s http://localhost/health > /dev/null; then
  echo "✅ Feature Store accessible"
else
  echo "❌ Feature Store non accessible"
  kill $PORT_FORWARD_PID
  exit 1
fi

# Test des features (si données disponibles)
echo "Test des features disponibles:"
curl -s http://localhost/api/v1/features | jq '.' || echo "⚠️  Aucune feature trouvée (données à charger)"

kill $PORT_FORWARD_PID

echo ""

# Instructions finales
echo "🎉 Feature Store Feast configuré avec succès!"
echo ""
echo "📋 Informations importantes:"
echo "   Service: feast-feature-server-service"
echo "   Port gRPC: 6566"
echo "   Port HTTP: 80"
echo "   Registry: s3://data-lake/feast/registry.db"
echo "   Offline Store: PostgreSQL (schema: feast)"
echo "   Online Store: Redis"
echo ""
echo "🚀 Prochaines étapes:"
echo "   1. Charger les données historiques dans MinIO"
echo "   2. Exécuter la materialization: feast materialize-incremental"
echo "   3. Intégrer avec l'API de scoring"
echo "   4. Configurer les jobs de materialization automatique"
echo ""
echo "📖 Commandes utiles:"
echo "   Port-forward: kubectl port-forward svc/feast-feature-server-service 80:80"
echo "   Materialize: kubectl exec -it deployment/feast-materialization-job -- feast materialize-incremental"
echo "   Status: curl http://localhost/api/v1/features"