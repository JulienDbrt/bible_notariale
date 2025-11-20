#!/bin/bash

echo "🛑 Arrêt de ChatDocAI..."

# Arrêter et supprimer les conteneurs
docker-compose -f docker-compose.dev.yml down

# Option pour nettoyer les volumes (décommentez si nécessaire)
# docker-compose -f docker-compose.dev.yml down -v

echo "✅ Services arrêtés"