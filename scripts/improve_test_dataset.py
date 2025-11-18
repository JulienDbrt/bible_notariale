#!/usr/bin/env python3
"""
Script d'amélioration du dataset de test v2.0
Corrige les problèmes identifiés dans l'analyse :
1. Ajoute les sources documentaires manquantes
2. Corrige les flags multi-documents
3. Améliore les éléments clés trop vagues
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

def find_question(data, qid):
    """Trouve une question par son ID"""
    for q in data['qa_pairs']:
        if q['id'] == qid:
            return q
    return None

def improve_dataset():
    """Applique toutes les améliorations"""
    data = load_dataset()
    stats = {
        'sources_added': 0,
        'multi_doc_fixed': 0,
        'elements_improved': 0
    }

    # ==========================================
    # 1. AJOUT DES SOURCES DOCUMENTAIRES MANQUANTES
    # ==========================================

    sources_fixes = {
        'Q012': ['rpn_rpn'],  # Relations notaires-généalogistes
        'Q018': ['rpn_rpn', 'fil_infos_fil_info_262'],  # Entrée en vigueur réforme déontologie
        'Q026': ['rpn_rpn'],  # Conditions édiction code déontologie
        'Q027': ['rpn_rpn'],  # Articulation secret pro et généalogistes
        'Q033': ['fiche_doctrine_smo_vd'],  # SMO (Société de Moyens et d'Organisation)
        'Q036': ['convention_collective_convention_collective_nationale_du_notariat_idcc_2205_actualisee_et_consolidee'],  # Clerc de notaire
    }

    for qid, sources in sources_fixes.items():
        q = find_question(data, qid)
        if q and not q['documents_sources_attendus']:
            q['documents_sources_attendus'] = sources
            stats['sources_added'] += len(sources)
            print(f"✓ {qid}: Ajout de {len(sources)} source(s)")

    # ==========================================
    # 2. CORRECTION DES FLAGS MULTI-DOCUMENTS
    # ==========================================

    multi_doc_fixes = [
        'Q007',  # Loi + ordonnances (hiérarchie normes)
        'Q010',  # Déontologie + discipline
        'Q018',  # Contexte réforme 2021-2024
        'Q028',  # Partenaires sociaux (multiples avenants)
    ]

    for qid in multi_doc_fixes:
        q = find_question(data, qid)
        if q and not q['necessite_multi_documents']:
            q['necessite_multi_documents'] = True
            stats['multi_doc_fixed'] += 1
            print(f"✓ {qid}: Marqué comme multi-documents")

    # ==========================================
    # 3. AMÉLIORATION DES ÉLÉMENTS CLÉS VAGUES
    # ==========================================

    # Q008: Rendre plus factuel
    q008 = find_question(data, 'Q008')
    if q008:
        q008['elements_cles_reponse'] = [
            "Notaires premiers contributeurs du secteur non-financier à Tracfin",
            "Déclarations de soupçon auprès de Tracfin",
            "Prévenir le blanchiment de capitaux et financement du terrorisme",
            "Obligation devenue pratique professionnelle quotidienne"
        ]
        stats['elements_improved'] += 1
        print(f"✓ Q008: Éléments clés améliorés")

    # Q012: Rendre plus objectif
    q012 = find_question(data, 'Q012')
    if q012:
        q012['elements_cles_reponse'] = [
            "Relations encadrées par le RPN",
            "Exigences de rigueur et professionnalisme mutuelles",
            "Respect du secret professionnel",
            "Encadrement des relations d'affaires"
        ]
        stats['elements_improved'] += 1
        print(f"✓ Q012: Éléments clés améliorés")

    # ==========================================
    # 4. MISE À JOUR DE LA VERSION
    # ==========================================

    data['dataset_version'] = "2.0"
    data['last_updated'] = "2025-11-18"

    # Sauvegarder
    save_dataset(data)

    # Rapport final
    print("\n" + "="*60)
    print("RAPPORT D'AMÉLIORATION - Dataset v2.0")
    print("="*60)
    print(f"Sources documentaires ajoutées: {stats['sources_added']}")
    print(f"Flags multi-documents corrigés: {stats['multi_doc_fixed']}")
    print(f"Éléments clés améliorés: {stats['elements_improved']}")
    print("="*60)

    # Calculer les nouveaux pourcentages
    total_questions = len(data['qa_pairs'])
    questions_with_sources = sum(1 for q in data['qa_pairs'] if q['documents_sources_attendus'])
    questions_multi_doc = sum(1 for q in data['qa_pairs'] if q['necessite_multi_documents'])

    print(f"\nNOUVEAUX INDICATEURS:")
    print(f"Questions avec sources: {questions_with_sources}/{total_questions} ({questions_with_sources*100//total_questions}%)")
    print(f"Questions multi-documents: {questions_multi_doc}/{total_questions} ({questions_multi_doc*100//total_questions}%)")
    print("="*60)

if __name__ == "__main__":
    improve_dataset()
