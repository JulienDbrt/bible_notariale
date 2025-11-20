#!/bin/bash

# SCRIPT POST-INGESTION - DENSIFICATION SÉMANTIQUE AUTOMATIQUE
# Mission: Exécuter automatiquement la densification après chaque ingestion

set -e  # Arrêt en cas d'erreur

echo "========================================"
echo "DÉBUT DE LA DENSIFICATION SÉMANTIQUE"
echo "========================================"

# Chemin de base
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BACKEND_DIR"

# Activation de l'environnement virtuel si nécessaire
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Exécution du pipeline d'enrichissement
echo "[+] Lancement du pipeline d'enrichissement..."
python scripts/enrichment_pipeline.py

# Statistiques post-enrichissement
echo ""
echo "[+] Collecte des statistiques Neo4j..."
python -c "
import asyncio
from src.services.neo4j_service import get_neo4j_service

async def get_stats():
    neo4j_service = get_neo4j_service()
    await neo4j_service.initialize()
    
    # Statistiques du graphe
    stats = await neo4j_service.get_statistics()
    
    if stats:
        print(f'''
    ======================================
    RAPPORT DE DENSIFICATION
    ======================================
    Nœuds totaux:     {stats['nodes']}
    Relations:        {stats['relations']}
    Documents:        {stats['documents']}
    Chunks:           {stats['chunks']}
    Entités:          {stats.get('entities', 0)}
    
    Densité moyenne:  {stats['relations'] / max(stats['nodes'], 1):.2f} relations/nœud
    ======================================
        ''')
    
    await neo4j_service.close()

asyncio.run(get_stats())
"

echo "[✓] Densification sémantique terminée"
echo ""