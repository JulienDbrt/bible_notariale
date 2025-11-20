#!/bin/bash
# Nettoyage brutal et sans pitié du repository

echo "🔥 NETTOYAGE TOTAL - AUCUNE PITIÉ"

# 1. ÉLIMINATION DES CACHES ET BUILDS
echo "💀 Suppression des caches..."
rm -rf front/.next/
rm -rf front/tsconfig.tsbuildinfo
rm -rf backend/venv/
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
find . -name ".DS_Store" -delete

# 2. EXTERMINATION DES FICHIERS EXPÉRIMENTAUX
echo "🗑️ Élimination des déchets expérimentaux..."
cd backend
rm -f test_*.py
rm -f evaluation_*.py evaluation_*.csv evaluation_*.json evaluation_*.txt
rm -f create_dockerfile_patch.py lightrag_patch.py post_install.py
rm -f setup_env.sh protocole_final.py debug_env.py
rm -f list_minio_buckets.py index_status.json mass_ingestion_log.txt
rm -rf lightrag_patches/ notaria_storage/ test_local_storage/ test_storage/
cd ..

# 3. SUPPRESSION DES BUILDS FRONTEND
echo "🧹 Nettoyage frontend..."
rm -rf front/node_modules/.package-lock.json

echo "✅ NETTOYAGE TERMINÉ - Repository propre"
echo "⚠️  N'oubliez pas de faire tourner les clés API compromises!"