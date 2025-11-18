#!/usr/bin/env python3
"""
Script d'ajout du champ confiance_attendue au dataset v2.0
Calibre le niveau de confiance attendu pour chaque réponse basé sur:
- Difficulté de la question
- Présence de sources documentaires
- Nécessité de multi-documents
"""

import json
from pathlib import Path

DATASET_PATH = Path("tests/datasets/chatbot_test_dataset.json")

def load_dataset():
    """Charge le dataset de test"""
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_dataset(data):
    """Sauvegarde le dataset de test"""
    with open(DATASET_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calculate_confidence(question):
    """
    Calcule le niveau de confiance attendu basé sur plusieurs critères

    Règles:
    - Facile + source unique → Haute
    - Moyen + sources → Haute
    - Moyen + multi-doc → Moyenne
    - Pointu + sources → Moyenne
    - Pointu + multi-doc → Moyenne ou Faible
    - Edge cases → Généralement Faible
    - Questions sans sources → Moyenne ou Faible
    """
    difficulte = question['difficulte']
    has_sources = len(question['documents_sources_attendus']) > 0
    multi_doc = question['necessite_multi_documents']
    categorie = question['categorie']

    # Edge cases → généralement faible confiance
    if categorie == 'edge_cases':
        return 'faible'

    # Questions faciles avec sources → haute confiance
    if difficulte == 'facile' and has_sources and not multi_doc:
        return 'haute'

    # Questions moyennes avec sources uniques → haute confiance
    if difficulte == 'moyen' and has_sources and not multi_doc:
        return 'haute'

    # Questions moyennes multi-doc → moyenne confiance
    if difficulte == 'moyen' and multi_doc:
        return 'moyenne'

    # Questions pointues avec sources → moyenne confiance
    if difficulte == 'pointu' and has_sources:
        return 'moyenne'

    # Questions sans sources documentaires → moyenne ou faible
    if not has_sources:
        if difficulte == 'facile':
            return 'moyenne'  # Connaissance générale
        else:
            return 'faible'

    # Par défaut → moyenne
    return 'moyenne'

def add_confiance_attendue():
    """Ajoute le champ confiance_attendue à toutes les questions"""
    data = load_dataset()

    stats = {
        'haute': 0,
        'moyenne': 0,
        'faible': 0
    }

    for question in data['qa_pairs']:
        confiance = calculate_confidence(question)
        question['confiance_attendue'] = confiance
        stats[confiance] += 1

        # Affichage pour vérification
        qid = question['id']
        diff = question['difficulte']
        multi = "multi" if question['necessite_multi_documents'] else "single"
        sources = len(question['documents_sources_attendus'])
        print(f"{qid}: {confiance:8} ({diff}, {multi}, {sources} sources)")

    # Sauvegarder
    save_dataset(data)

    # Rapport
    total = len(data['qa_pairs'])
    print("\n" + "="*60)
    print("RAPPORT - Ajout confiance_attendue")
    print("="*60)
    print(f"Haute confiance:   {stats['haute']:2d} ({stats['haute']*100//total}%)")
    print(f"Moyenne confiance: {stats['moyenne']:2d} ({stats['moyenne']*100//total}%)")
    print(f"Faible confiance:  {stats['faible']:2d} ({stats['faible']*100//total}%)")
    print("="*60)
    print(f"\nTOTAL: {total} questions traitées")
    print("="*60)

if __name__ == "__main__":
    add_confiance_attendue()
