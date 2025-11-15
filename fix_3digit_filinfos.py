#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction des Fil-Infos avec numéros à 3 chiffres (erreurs de nommage).
Ces numéros semblent être 2XXX mais ont perdu le "2" initial.
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent
DOCS_METADATA_DIR = BASE_DIR / "_metadata" / "documents"

REFERENCE_NUM = 2870
REFERENCE_DATE = datetime(2024, 7, 15)

def estimate_date_from_number(fil_info_num):
    """Estime la date basée sur le numéro du Fil-Info."""
    diff = fil_info_num - REFERENCE_NUM
    estimated_date = REFERENCE_DATE + timedelta(weeks=diff)
    return estimated_date.strftime("%Y-%m-%d")


def fix_3digit_filinfos():
    """Corrige les Fil-Infos avec des numéros à 3 chiffres."""
    # Mapping des numéros à 3 chiffres vers les vrais numéros 2XXX
    # Basé sur le pattern et le contenu moderne des documents
    corrections = {
        '272': '2872',  # Content mentions 2007 partnership
        '255': '2855',
        '235': '2835',
        '226': '2826',
        '265': '2865',
        '240': '2840',
        '279': '2879',
    }

    stats = {'fixed': 0}

    for meta_file in DOCS_METADATA_DIR.glob("*.metadata.json"):
        with open(meta_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        if metadata['classification']['type_document'] != 'fil_info':
            continue

        date = metadata['metadata'].get('date_publication', '')
        if not date.startswith('197'):  # Not an incorrectly dated doc
            continue

        titre = metadata['metadata']['titre']

        # Extraire le numéro à 3 chiffres
        num_match = re.search(r'N°(\d{3})\b', titre)
        if num_match:
            old_num = num_match.group(1)
            if old_num in corrections:
                new_num = corrections[old_num]

                # Mettre à jour le titre
                new_titre = titre.replace(f"N°{old_num}", f"N°{new_num}")
                metadata['metadata']['titre'] = new_titre

                # Mettre à jour le titre court
                titre_court = metadata['metadata'].get('titre_court', '')
                new_titre_court = titre_court.replace(f" {old_num} ", f" {new_num} ")
                metadata['metadata']['titre_court'] = new_titre_court

                # Calculer la nouvelle date
                new_date = estimate_date_from_number(int(new_num))
                metadata['metadata']['date_publication'] = new_date
                metadata['metadata']['date_effet'] = new_date
                metadata['classification']['annee_reference'] = int(new_date[:4])

                with open(meta_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)

                print(f"✓ N°{old_num} → N°{new_num} ({new_date})")
                print(f"  {titre[:50]}...")
                stats['fixed'] += 1

    return stats


def main():
    print("=" * 60)
    print("CORRECTION DES FIL-INFOS AVEC NUMÉROS À 3 CHIFFRES")
    print("=" * 60)
    print()

    stats = fix_3digit_filinfos()

    print()
    print(f"Total corrigé: {stats['fixed']}")


if __name__ == "__main__":
    main()
