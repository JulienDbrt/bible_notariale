#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrections finales de qualité - Priorité 1 à 5
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
DOCS_METADATA_DIR = BASE_DIR / "_metadata" / "documents"

# =============================================================================
# PRIORITÉ 1 : Dates spécifiques pour documents restants
# =============================================================================

SPECIFIC_DATES = {
    "note_de_me_bonte_ventes_immo": "2025-07-31",  # "Rennes, le 31 juillet 2025"
    "observatoire_immobilier_cid14_2025m1": "2025-01-31",  # 2025M1 = janvier
    "observatoire_immobilier_cid50_2025m1": "2025-01-31",
    "observatoire_immobilier_cid61_2025m1": "2025-01-31",
}

# =============================================================================
# PRIORITÉ 2 : Définitions du vocabulaire notarial
# =============================================================================

VOCABULAIRE_DEFINITIONS = {
    "lcb-ft": "Lutte Contre le Blanchiment et le Financement du Terrorisme. Ensemble des obligations légales imposées aux notaires pour prévenir l'utilisation du système financier à des fins de blanchiment de capitaux.",
    "ccn": "Convention Collective Nationale du Notariat (IDCC 2205). Texte régissant les relations de travail entre employeurs (notaires) et salariés de la profession.",
    "convention collective": "Convention Collective Nationale du Notariat (IDCC 2205). Texte régissant les relations de travail entre employeurs (notaires) et salariés de la profession.",
    "csn": "Conseil Supérieur du Notariat. Instance nationale représentant la profession auprès des pouvoirs publics et coordonnant les chambres départementales.",
    "conseil supérieur du notariat": "Conseil Supérieur du Notariat. Instance nationale représentant la profession auprès des pouvoirs publics et coordonnant les chambres départementales.",
    "avenant": "Acte juridique modifiant les clauses d'un accord ou d'une convention existante. Dans le contexte notarial, modification de la CCN négociée entre partenaires sociaux.",
    "minute": "Original d'un acte authentique conservé par le notaire. Document source qui ne peut quitter l'étude et dont seules des copies (expéditions) sont délivrées.",
    "acte authentique": "Acte reçu par un officier public (notaire) conférant foi publique à son contenu. Il a date certaine et force exécutoire.",
    "opco": "Opérateur de Compétences. Organisme agréé pour financer l'apprentissage et la formation professionnelle. Pour le notariat : OPCO EP (Entreprises de Proximité).",
    "rgpd": "Règlement Général sur la Protection des Données. Réglementation européenne encadrant le traitement des données personnelles.",
    "prévoyance": "Système de protection sociale complémentaire (décès, invalidité, incapacité) couvrant les risques non pris en charge par la Sécurité Sociale.",
    "émoluments": "Rémunération tarifée du notaire pour les actes soumis à tarif réglementé. À distinguer des honoraires (actes à tarif libre).",
    "tarification": "Barème réglementé fixant les émoluments des actes notariés. Défini par décret et applicable uniformément sur le territoire.",
    "cybersécurité": "Ensemble des mesures techniques et organisationnelles visant à protéger les systèmes informatiques de l'office contre les menaces numériques.",
    "harcèlement": "Comportements répétés portant atteinte à la dignité du salarié ou créant un environnement hostile. Peut être moral ou sexuel.",
    "circulaire": "Document émis par le CSN donnant des instructions ou recommandations aux notaires sur l'application de dispositions légales ou réglementaires.",
    "intéressement": "Dispositif d'épargne salariale permettant d'associer les collaborateurs aux résultats de l'office.",
    "formation professionnelle": "Obligation légale de formation continue pour les notaires (30h/2 ans) et leurs collaborateurs (développement des compétences).",
    "congés payés": "Droits à repos rémunéré des salariés. Régime spécifique dans la CCN du notariat avec majoration pour ancienneté.",
    "égalité professionnelle": "Principe garantissant l'égalité de traitement entre femmes et hommes en matière de recrutement, formation, rémunération et évolution.",
    "clerc de notaire": "Collaborateur qualifié d'un office notarial, participant à la rédaction des actes sous la responsabilité du notaire.",
    "clerc": "Collaborateur qualifié d'un office notarial, participant à la rédaction des actes sous la responsabilité du notaire.",
    "rémunération": "Ensemble des contreparties financières du travail : salaire de base + primes + avantages. Minima fixés par la CCN selon classification.",
    "salaire": "Ensemble des contreparties financières du travail : salaire de base + primes + avantages. Minima fixés par la CCN selon classification.",
    "notaire": "Officier public et ministériel nommé par le garde des Sceaux, investi d'une mission d'authentification des actes juridiques.",
    "office notarial": "Structure professionnelle où exerce le notaire. Peut être individuel ou en société (SCP, SEL, SELARL).",
    "acte": "Document juridique établi par le notaire. Peut être authentique (force probante) ou sous seing privé (conseillé).",
    "succession": "Transmission du patrimoine d'une personne décédée. Le notaire assure le règlement successoral et la liquidation.",
    "donation": "Acte par lequel une personne transmet de son vivant un bien à une autre, à titre gratuit.",
    "vente immobilière": "Transaction portant sur un bien immobilier nécessitant l'intervention du notaire pour sa validité.",
    "hypothèque": "Sûreté réelle immobilière garantissant le paiement d'une dette. Inscrite au fichier immobilier.",
    "publicité foncière": "Système d'enregistrement des droits immobiliers permettant leur opposabilité aux tiers.",
    "authentification": "Processus par lequel le notaire confère force probante et date certaine à un acte.",
}

# =============================================================================
# PRIORITÉ 3 : Questions à supprimer par type de document
# =============================================================================

QUESTIONS_TO_REMOVE = {
    "assurance": [
        "Quel est l'impact sur la rémunération",
        "Quelles sont les nouvelles grilles de salaires",
        "Comment financer ces formations",
        "classification des emplois",
    ],
    "immobilier": [
        "Comment financer ces formations",
        "grilles de salaires",
        "classification des emplois",
    ],
    "decret_ordonnance": [
        "Comment financer ces formations",
    ],
    "conformite": [
        "grilles de salaires",
        "classification des emplois",
    ],
}

# =============================================================================
# FONCTIONS DE CORRECTION
# =============================================================================

def fix_specific_dates():
    """Corrige les dates spécifiques pour les documents identifiés."""
    print("\n1. CORRECTION DES DATES SPÉCIFIQUES")
    print("-" * 50)

    fixed = 0
    for meta_file in DOCS_METADATA_DIR.glob("*.metadata.json"):
        with open(meta_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        doc_id = metadata.get('document_id', '')

        # Vérifier si ce document a une date spécifique à corriger
        for key, new_date in SPECIFIC_DATES.items():
            if key in doc_id:
                old_date = metadata['metadata'].get('date_publication', '')
                if old_date != new_date:
                    metadata['metadata']['date_publication'] = new_date
                    metadata['metadata']['date_effet'] = new_date

                    with open(meta_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)

                    print(f"✓ {doc_id[:40]:40} {old_date} → {new_date}")
                    fixed += 1
                break

    print(f"\n   Total dates corrigées: {fixed}")
    return fixed


def enrich_vocabulary_definitions():
    """Ajoute les définitions aux termes du vocabulaire."""
    print("\n2. ENRICHISSEMENT DES DÉFINITIONS DU VOCABULAIRE")
    print("-" * 50)

    enriched_count = 0
    terms_enriched = 0

    for meta_file in DOCS_METADATA_DIR.glob("*.metadata.json"):
        with open(meta_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        vocab = metadata.get('vocabulaire_specifique', [])
        if not vocab:
            continue

        modified = False
        for item in vocab:
            terme = item.get('terme', '').lower()
            current_def = item.get('definition', '')

            # Si définition vide ou trop courte, enrichir
            if len(current_def) < 20:
                # Chercher dans notre dictionnaire
                for key, definition in VOCABULAIRE_DEFINITIONS.items():
                    if key in terme or terme in key:
                        item['definition'] = definition
                        modified = True
                        terms_enriched += 1
                        break

        if modified:
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            enriched_count += 1

    print(f"   Documents enrichis: {enriched_count}")
    print(f"   Termes avec définitions ajoutées: {terms_enriched}")
    return enriched_count


def filter_irrelevant_questions():
    """Supprime les questions non pertinentes selon le type de document."""
    print("\n3. FILTRAGE DES QUESTIONS NON PERTINENTES")
    print("-" * 50)

    filtered_count = 0
    questions_removed = 0

    for meta_file in DOCS_METADATA_DIR.glob("*.metadata.json"):
        with open(meta_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        doc_type = metadata['classification']['type_document']
        questions = metadata.get('questions_typiques', [])

        if doc_type not in QUESTIONS_TO_REMOVE or not questions:
            continue

        patterns_to_remove = QUESTIONS_TO_REMOVE[doc_type]

        new_questions = []
        removed = 0

        for q in questions:
            should_keep = True
            for pattern in patterns_to_remove:
                if pattern.lower() in q.lower():
                    should_keep = False
                    removed += 1
                    break
            if should_keep:
                new_questions.append(q)

        if removed > 0:
            metadata['questions_typiques'] = new_questions
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            filtered_count += 1
            questions_removed += removed

    print(f"   Documents filtrés: {filtered_count}")
    print(f"   Questions supprimées: {questions_removed}")
    return filtered_count


def enrich_document_relations():
    """Enrichit les relations entre documents."""
    print("\n4. ENRICHISSEMENT DES RELATIONS DOCUMENTAIRES")
    print("-" * 50)

    # Charger tous les documents pour trouver les relations
    all_docs = {}
    for meta_file in DOCS_METADATA_DIR.glob("*.metadata.json"):
        with open(meta_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        all_docs[metadata['document_id']] = {
            'file': meta_file,
            'metadata': metadata
        }

    # Trouver les avenants et créer des liens
    avenants = {}
    for doc_id, doc_data in all_docs.items():
        if 'avenant' in doc_id.lower():
            # Extraire le numéro
            match = re.search(r'avenant[_\s]*n?°?\s*(\d+)', doc_id, re.IGNORECASE)
            if match:
                num = int(match.group(1))
                avenants[num] = doc_id

    # Créer les relations pour les avenants
    relations_created = 0
    for num in sorted(avenants.keys()):
        doc_id = avenants[num]
        doc_data = all_docs[doc_id]
        metadata = doc_data['metadata']

        # Chercher les avenants précédents
        relations = metadata.get('relations_documentaires', {})
        if 'modifie' not in relations:
            relations['modifie'] = []

        # Lier aux avenants proches (1-5 numéros avant)
        modified = False
        for prev_num in range(num - 5, num):
            if prev_num in avenants and prev_num > 0:
                prev_id = avenants[prev_num]
                if prev_id not in relations['modifie']:
                    relations['modifie'].append(prev_id)
                    modified = True
                    relations_created += 1

        if modified:
            metadata['relations_documentaires'] = relations
            with open(doc_data['file'], 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"   Relations créées: {relations_created}")
    return relations_created


def check_and_fix_truncated_summaries():
    """Vérifie et corrige les résumés tronqués."""
    print("\n5. VÉRIFICATION DES RÉSUMÉS TRONQUÉS")
    print("-" * 50)

    truncated = 0
    short_summaries = 0

    for meta_file in DOCS_METADATA_DIR.glob("*.metadata.json"):
        with open(meta_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        resume = metadata.get('resume', '')
        titre = metadata['metadata']['titre']

        if 'truncated' in resume.lower() or '[...]' in resume:
            print(f"   ⚠️  Tronqué: {titre[:50]}")
            truncated += 1
        elif len(resume) < 100:
            print(f"   ⚠️  Court ({len(resume)} chars): {titre[:50]}")
            short_summaries += 1

    print(f"\n   Résumés tronqués: {truncated}")
    print(f"   Résumés courts (<100 chars): {short_summaries}")
    return truncated + short_summaries


def main():
    print("=" * 60)
    print("CORRECTIONS FINALES DE QUALITÉ")
    print("=" * 60)

    stats = {
        'dates': fix_specific_dates(),
        'vocab': enrich_vocabulary_definitions(),
        'questions': filter_irrelevant_questions(),
        'relations': enrich_document_relations(),
        'summaries': check_and_fix_truncated_summaries(),
    }

    print("\n" + "=" * 60)
    print("RÉSUMÉ DES CORRECTIONS")
    print("=" * 60)
    print(f"Dates spécifiques corrigées    : {stats['dates']}")
    print(f"Documents avec vocab enrichi   : {stats['vocab']}")
    print(f"Documents avec questions filtrées: {stats['questions']}")
    print(f"Relations documentaires créées : {stats['relations']}")
    print(f"Résumés à vérifier             : {stats['summaries']}")
    print()


if __name__ == "__main__":
    main()
