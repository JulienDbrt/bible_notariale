#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation de cohérence des métadonnées
"""

import os
import json
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent
METADATA_DIR = BASE_DIR / "_metadata"
DOCS_METADATA_DIR = METADATA_DIR / "documents"
SOURCES_DIR = BASE_DIR / "sources_documentaires"


def validate_document(metadata):
    """Valide la cohérence d'un document."""
    issues = []
    warnings = []

    # 1. Vérifier que le fichier existe
    file_path = BASE_DIR / metadata['fichier']
    if not file_path.exists():
        issues.append(f"Fichier manquant: {metadata['fichier']}")

    # 2. Vérifier la cohérence des dates
    date_pub = metadata['metadata'].get('date_publication', '')
    if not date_pub or date_pub == 'N/A':
        issues.append("Date de publication manquante")
    elif date_pub < '2018-01-01' or date_pub > '2026-01-01':
        warnings.append(f"Date suspecte: {date_pub}")

    # 3. Vérifier le résumé
    resume = metadata.get('resume', '')
    if not resume or resume.startswith('Document de type'):
        warnings.append("Résumé générique non enrichi")
    elif len(resume) < 50:
        warnings.append(f"Résumé trop court ({len(resume)} chars)")
    elif len(resume) > 1000:
        warnings.append(f"Résumé trop long ({len(resume)} chars)")

    # 4. Vérifier les questions typiques
    questions = metadata.get('questions_typiques', [])
    if len(questions) < 3:
        warnings.append(f"Peu de questions ({len(questions)})")
    elif len(questions) > 10:
        warnings.append(f"Trop de questions ({len(questions)})")

    # 5. Vérifier la classification
    doc_type = metadata['classification'].get('type_document', '')
    valid_types = [
        'circulaire_csn', 'avenant_ccn', 'accord_branche', 'fil_info',
        'guide_pratique', 'decret_ordonnance', 'assurance', 'immobilier',
        'formation', 'conformite'
    ]
    if doc_type not in valid_types:
        issues.append(f"Type de document invalide: {doc_type}")

    # 6. Vérifier la cohérence type/contenu
    titre = metadata['metadata'].get('titre', '').lower()
    if doc_type == 'avenant_ccn' and 'avenant' not in titre:
        warnings.append("Type avenant mais 'avenant' absent du titre")
    if doc_type == 'circulaire_csn' and 'circulaire' not in titre:
        warnings.append("Type circulaire mais 'circulaire' absent du titre")
    if doc_type == 'fil_info' and 'fil-info' not in metadata['nom_fichier'].lower():
        warnings.append("Type fil_info mais pattern absent du nom de fichier")

    # 7. Vérifier les mots-clés
    mots_cles = metadata.get('mots_cles', [])
    if len(mots_cles) < 2:
        warnings.append(f"Peu de mots-clés ({len(mots_cles)})")

    # 8. Vérifier le vocabulaire spécifique
    vocab = metadata.get('vocabulaire_specifique', [])
    if vocab:
        for term in vocab:
            if not term.get('synonymes'):
                warnings.append(f"Terme sans synonymes: {term.get('terme')}")

    # 9. Vérifier l'année de référence
    annee = metadata['classification'].get('annee_reference', 0)
    if annee < 2019 or annee > 2025:
        warnings.append(f"Année de référence suspecte: {annee}")

    # 10. Vérifier la cohérence titre/nom_fichier
    if metadata['metadata']['titre'] == metadata['nom_fichier']:
        warnings.append("Titre identique au nom de fichier (non nettoyé)")

    return issues, warnings


def analyze_all_documents():
    """Analyse tous les documents et génère un rapport."""

    print("Validation de cohérence des métadonnées")
    print("=" * 60)
    print()

    metadata_files = list(DOCS_METADATA_DIR.glob("*.metadata.json"))
    total = len(metadata_files)

    print(f"Documents à valider : {total}")
    print()

    # Statistiques
    docs_with_issues = []
    docs_with_warnings = []
    all_issues = defaultdict(int)
    all_warnings = defaultdict(int)

    # Statistiques par type
    type_stats = defaultdict(lambda: {'count': 0, 'issues': 0, 'warnings': 0})

    for meta_file in metadata_files:
        with open(meta_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        issues, warnings = validate_document(metadata)
        doc_type = metadata['classification']['type_document']

        type_stats[doc_type]['count'] += 1

        if issues:
            docs_with_issues.append({
                'file': meta_file.name,
                'title': metadata['metadata']['titre'][:50],
                'issues': issues
            })
            type_stats[doc_type]['issues'] += 1
            for issue in issues:
                all_issues[issue] += 1

        if warnings:
            docs_with_warnings.append({
                'file': meta_file.name,
                'title': metadata['metadata']['titre'][:50],
                'warnings': warnings
            })
            type_stats[doc_type]['warnings'] += 1
            for warning in warnings:
                all_warnings[warning] += 1

    # Rapport
    print("## Résumé")
    print()
    print(f"- Documents sans problème : {total - len(docs_with_issues) - len(docs_with_warnings)}")
    print(f"- Documents avec avertissements : {len(docs_with_warnings)}")
    print(f"- Documents avec erreurs : {len(docs_with_issues)}")
    print()

    print("## Erreurs critiques")
    if all_issues:
        for issue, count in sorted(all_issues.items(), key=lambda x: -x[1]):
            print(f"  - {issue} ({count}x)")
    else:
        print("  Aucune erreur critique !")
    print()

    print("## Avertissements fréquents")
    for warning, count in sorted(all_warnings.items(), key=lambda x: -x[1])[:10]:
        print(f"  - {warning} ({count}x)")
    print()

    print("## Statistiques par type de document")
    print()
    for doc_type in sorted(type_stats.keys()):
        stats = type_stats[doc_type]
        pct_ok = ((stats['count'] - stats['issues']) / stats['count'] * 100) if stats['count'] > 0 else 0
        print(f"  {doc_type}:")
        print(f"    - Total : {stats['count']}")
        print(f"    - Erreurs : {stats['issues']}")
        print(f"    - Avertissements : {stats['warnings']}")
        print(f"    - Taux OK : {pct_ok:.1f}%")
        print()

    # Détails des erreurs critiques
    if docs_with_issues:
        print("## Documents avec erreurs critiques")
        print()
        for doc in docs_with_issues[:20]:
            print(f"  {doc['file']}")
            print(f"    Titre: {doc['title']}")
            for issue in doc['issues']:
                print(f"    ❌ {issue}")
            print()

    # Sauvegarder le rapport
    report = {
        'total': total,
        'with_issues': len(docs_with_issues),
        'with_warnings': len(docs_with_warnings),
        'issues': dict(all_issues),
        'warnings': dict(all_warnings),
        'type_stats': {k: dict(v) for k, v in type_stats.items()},
        'documents_with_issues': docs_with_issues,
        'documents_with_warnings': docs_with_warnings[:50]  # Limiter
    }

    with open(METADATA_DIR / "validation_report.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"Rapport sauvegardé dans _metadata/validation_report.json")


if __name__ == "__main__":
    analyze_all_documents()
