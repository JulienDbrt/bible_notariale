#!/bin/bash
# PHASE 6.1 - DÉPLOIEMENT PRODUCTION

set -e

echo "🚀 DÉPLOIEMENT PRODUCTION CHATDOCAI"

# Vérification des prérequis
command -v docker >/dev/null 2>&1 || { echo "❌ Docker requis"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose requis"; exit 1; }

# Vérification des variables d'environnement
if [ ! -f backend/.env ]; then
    echo "❌ backend/.env manquant"
    echo "Copiez backend/.env.example et configurez les clés API"
    exit 1
fi

# Build des images
echo "📦 Construction des images Docker..."
docker-compose build --no-cache

# Démarrage des services de base
echo "🗄️ Démarrage Neo4j et MinIO..."
docker-compose up -d neo4j minio supabase

# Attendre que les services soient prêts
echo "⏳ Attente des services..."
sleep 10

# Initialisation Neo4j
echo "🔧 Configuration Neo4j..."
docker exec -it chatdocai-neo4j cypher-shell -u neo4j -p neo4j \
    "ALTER USER neo4j SET PASSWORD 'ChangeMeInProduction'"

# Création du bucket MinIO
echo "📁 Configuration MinIO..."
docker exec -it chatdocai-minio mc alias set local http://localhost:9000 minioadmin minioadmin
docker exec -it chatdocai-minio mc mb local/documents --ignore-existing

# Démarrage de l'application
echo "🎯 Lancement de l'application..."
docker-compose up -d

# Vérification santé
echo "🏥 Vérification de santé..."
sleep 5
curl -f http://localhost:8000/health || echo "⚠️ Backend pas encore prêt"
curl -f http://localhost:3000 || echo "⚠️ Frontend pas encore prêt"

echo "✅ DÉPLOIEMENT TERMINÉ"
echo ""
echo "📍 URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   Neo4j Browser: http://localhost:7474"
echo "   MinIO Console: http://localhost:9001"
echo ""
echo "⚠️  IMPORTANT:"
echo "   1. Changez TOUS les mots de passe par défaut"
echo "   2. Configurez SSL/TLS pour la production"
echo "   3. Mettez en place les backups automatiques"
echo "   4. Activez le monitoring"