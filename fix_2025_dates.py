#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction des documents avec '25' ou '2025' dans le titre.
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
DOCS_METADATA_DIR = BASE_DIR / "_metadata" / "documents"


def detect_year_in_title(titre):
    """Détecte l'année dans le titre."""
    # Pattern pour 2025
    if '2025' in titre:
        return '2025'

    # Pattern pour "XX 25" ou "25" seul (circulaire 01 25)
    match = re.search(r'\b(\d{2})\s+25\b', titre)
    if match:
        return '2025'

    # Pattern pour CSN2024, CSN2025, etc.
    match = re.search(r'CSN(20\d{2})', titre, re.IGNORECASE)
    if match:
        return match.group(1)

    return None


def fix_2025_dates():
    """Corrige les documents avec 2025 dans le titre."""
    stats = {'fixed': 0}

    for meta_file in DOCS_METADATA_DIR.glob("*.metadata.json"):
        with open(meta_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        current_date = metadata['metadata'].get('date_publication', '')
        if current_date != '2025-01-01':
            continue

        titre = metadata['metadata']['titre']
        year = detect_year_in_title(titre)

        if year:
            new_date = f"{year}-01-01"
            metadata['metadata']['date_publication'] = new_date
            metadata['metadata']['date_effet'] = new_date
            metadata['classification']['annee_reference'] = int(year)

            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print(f"✓ {titre[:45]:45} → {new_date}")
            stats['fixed'] += 1
        else:
            print(f"  {titre[:45]:45} (pas de date)")

    return stats


def main():
    print("Correction des dates '25' et '2025'")
    print("=" * 60)
    print()

    stats = fix_2025_dates()
    print()
    print(f"Corrigés: {stats['fixed']}")


if __name__ == "__main__":
    main()
