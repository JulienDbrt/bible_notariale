#!/bin/bash

echo "🚀 LANCEMENT ÉVALUATION COMPLÈTE - PROTOCOLE BLINDÉ"
echo "======================================================"

# Se positionner à la racine du projet pour assurer la cohérence des chemins
cd "$(dirname "${BASH_SOURCE[0]}")"

# Activation de l'environnement virtuel
source venv/bin/activate

# Nom du fichier de log avec timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOGFILE="evaluation_complete_${TIMESTAMP}.log"

# Lancement de l'évaluation avec capture complète des logs
echo "📋 Début de l'évaluation : $(date)"
echo "📄 Logs sauvegardés dans : ${LOGFILE}"

# CORRECTION : Chemin et nom du script corrigés. Timeout retiré pour la robustesse.
python backend/evaluation/evaluation_process.py > "${LOGFILE}" 2>&1

EXIT_CODE=$?

echo ""
echo "======================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ ÉVALUATION TERMINÉE AVEC SUCCÈS"
    echo "📊 Résultats disponibles dans le fichier JSON généré"
else
    echo "❌ ÉVALUATION ÉCHOUÉE (Code de sortie: ${EXIT_CODE})"
fi

echo "📄 Logs complets disponibles dans : ${LOGFILE}"
echo "📅 Fin de mission : $(date)"

# Afficher un résumé des dernières lignes du log
if [ -f "${LOGFILE}" ]; then
    echo ""
    echo "--- SYNTHÈSE DE LA MISSION ---"
    # Cherche la section SYNTHÈSE dans le log et l'affiche
    grep -A 10 "SYNTHÈSE DE LA MISSION 'VÉRITÉ'" "${LOGFILE}"
fi