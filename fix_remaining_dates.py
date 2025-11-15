#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction des dates restantes pour les Fil-Infos sans pattern standard.
Utilise le numéro du Fil-Info pour estimer la date approximative.
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent
DOCS_METADATA_DIR = BASE_DIR / "_metadata" / "documents"

# Référence connue: Fil-Info 2870 = Semaine du 15 juillet 2024
# Les Fil-Infos sont hebdomadaires
REFERENCE_NUM = 2870
REFERENCE_DATE = datetime(2024, 7, 15)

def estimate_date_from_number(fil_info_num):
    """Estime la date basée sur le numéro du Fil-Info."""
    diff = fil_info_num - REFERENCE_NUM
    # Chaque numéro = 1 semaine
    estimated_date = REFERENCE_DATE + timedelta(weeks=diff)
    return estimated_date.strftime("%Y-%m-%d")


def extract_year_from_content(resume, titre):
    """Extrait l'année depuis le contenu ou les références."""
    # Chercher des années dans le texte
    years = re.findall(r'\b(20\d{2})\b', resume + " " + titre)
    if years:
        # Prendre l'année la plus fréquente ou la plus récente
        from collections import Counter
        year_counts = Counter(years)
        most_common = year_counts.most_common(1)[0][0]
        return int(most_common)
    return None


def fix_remaining_dates():
    """Corrige les dates restantes des Fil-Infos."""
    stats = {'fixed': 0, 'errors': []}

    for meta_file in DOCS_METADATA_DIR.glob("*.metadata.json"):
        with open(meta_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        if metadata['classification']['type_document'] != 'fil_info':
            continue

        current_date = metadata['metadata'].get('date_publication', '')
        if current_date != '2025-01-01':
            continue  # Déjà corrigé

        titre = metadata['metadata']['titre']
        resume = metadata.get('resume', '')

        # Extraire le numéro du Fil-Info
        num_match = re.search(r'N°?(\d+)', titre)
        if not num_match:
            num_match = re.search(r'info[_\s](\d+)', meta_file.name.lower())

        if num_match:
            fil_num = int(num_match.group(1))

            # Estimer la date
            estimated_date = estimate_date_from_number(fil_num)

            # Vérifier si l'année extraite du contenu correspond
            content_year = extract_year_from_content(resume, titre)
            if content_year:
                # Ajuster si l'année estimée ne correspond pas
                est_year = int(estimated_date[:4])
                if abs(content_year - est_year) <= 1:
                    # Garder l'année du contenu mais utiliser la date estimée
                    estimated_date = str(content_year) + estimated_date[4:]

            metadata['metadata']['date_publication'] = estimated_date
            metadata['metadata']['date_effet'] = estimated_date
            # Mettre à jour l'année de référence
            metadata['classification']['annee_reference'] = int(estimated_date[:4])

            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print(f"✓ {titre[:50]} → {estimated_date}")
            stats['fixed'] += 1
        else:
            stats['errors'].append(meta_file.name)
            print(f"⚠️  Numéro non trouvé: {meta_file.name}")

    return stats


def main():
    print("=" * 60)
    print("CORRECTION DES DATES RESTANTES (Fil-Infos)")
    print("=" * 60)
    print()

    stats = fix_remaining_dates()

    print()
    print("=" * 60)
    print(f"Dates corrigées: {stats['fixed']}")
    if stats['errors']:
        print(f"Erreurs: {len(stats['errors'])}")
    print()


if __name__ == "__main__":
    main()
