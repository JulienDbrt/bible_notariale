#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction finale des dates - extraction depuis titre et nom de fichier.
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
DOCS_METADATA_DIR = BASE_DIR / "_metadata" / "documents"


def extract_date_from_context(titre, nom_fichier, resume, annee_reference):
    """Extrait la date depuis le contexte disponible."""

    # 1. Chercher l'année dans le titre
    year_match = re.search(r'\b(20\d{2})\b', titre)
    if year_match:
        year = year_match.group(1)
        return f"{year}-01-01"

    # 2. Chercher dans le nom de fichier
    year_match = re.search(r'\b(20\d{2})\b', nom_fichier)
    if year_match:
        year = year_match.group(1)
        return f"{year}-01-01"

    # 3. Chercher un pattern date complet dans le résumé
    date_match = re.search(r'(\d{1,2})[/.-](\d{1,2})[/.-](20\d{2})', resume)
    if date_match:
        jour = date_match.group(1).zfill(2)
        mois = date_match.group(2).zfill(2)
        annee = date_match.group(3)
        return f"{annee}-{mois}-{jour}"

    # 4. Utiliser l'année de référence de la catégorie
    if annee_reference and annee_reference != 2025:
        return f"{annee_reference}-01-01"

    # 5. Chercher un pattern "n°XX" pour les avenants
    avenant_match = re.search(r'n°?\s*(\d+)', titre, re.IGNORECASE)
    if avenant_match:
        num = int(avenant_match.group(1))
        # Avenants 47-53 sont probablement de 2018-2024
        if 47 <= num <= 53:
            year = 2018 + (num - 47)
            return f"{year}-01-01"

    return None


def fix_remaining_dates():
    """Corrige les dates restantes."""
    stats = {'fixed': 0, 'remaining': []}

    for meta_file in DOCS_METADATA_DIR.glob("*.metadata.json"):
        with open(meta_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        current_date = metadata['metadata'].get('date_publication', '')
        if current_date != '2025-01-01':
            continue

        titre = metadata['metadata']['titre']
        nom_fichier = metadata.get('nom_fichier', '')
        resume = metadata.get('resume', '')
        annee_ref = metadata['classification'].get('annee_reference', 2025)

        new_date = extract_date_from_context(titre, nom_fichier, resume, annee_ref)

        if new_date and new_date != '2025-01-01':
            metadata['metadata']['date_publication'] = new_date
            metadata['metadata']['date_effet'] = new_date
            metadata['classification']['annee_reference'] = int(new_date[:4])

            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print(f"✓ {titre[:40]:40} → {new_date}")
            stats['fixed'] += 1
        else:
            stats['remaining'].append((titre, meta_file.name))

    return stats


def main():
    print("=" * 60)
    print("CORRECTION FINALE DES DATES")
    print("=" * 60)
    print()

    stats = fix_remaining_dates()

    print()
    print(f"Dates corrigées: {stats['fixed']}")

    if stats['remaining']:
        print(f"\nDocuments sans date identifiable ({len(stats['remaining'])}):")
        for titre, fname in stats['remaining']:
            print(f"  - {titre[:50]}")


if __name__ == "__main__":
    main()
