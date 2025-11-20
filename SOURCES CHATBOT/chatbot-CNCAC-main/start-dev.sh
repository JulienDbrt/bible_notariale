#!/bin/bash

# Script de démarrage pour l'environnement de développement
echo "🚀 Démarrage de ChatDocAI en mode développement"

# Vérifier si le fichier .env existe
if [ ! -f ".env" ]; then
    echo "❌ Fichier .env manquant dans le répertoire racine"
    echo "Créez un fichier .env avec les variables Supabase :"
    echo "SUPABASE_URL=supabase.chatbotpro.fr"
    echo "SUPABASE_ANON_KEY=your_anon_key"
    echo "SUPABASE_SERVICE_ROLE_KEY=your_service_key"
    exit 1
fi

# Charger les variables d'environnement
source .env

# Vérifier les variables essentielles
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_ANON_KEY" ]; then
    echo "❌ Variables Supabase manquantes dans .env"
    exit 1
fi

echo "✅ Configuration Supabase trouvée"
echo "📊 Supabase URL: $SUPABASE_URL"

# Arrêter les conteneurs existants
echo "🛑 Arrêt des conteneurs existants..."
docker-compose -f docker-compose.dev.yml down

# Construire et démarrer les services
echo "🏗️  Construction et démarrage des services..."
docker-compose -f docker-compose.dev.yml up --build

echo "🎉 Services démarrés !"
echo ""
echo "📱 Frontend: http://localhost:9002"
echo "🔧 Backend API: http://localhost:8000"
echo "📄 Backend Docs: http://localhost:8000/docs"
echo "💾 Minio Console: http://localhost:9001 (minioadmin / minioadmin123)"
echo "📦 Minio API: http://localhost:9000"