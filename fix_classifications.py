#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction des classifications incorrectes
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
DOCS_METADATA_DIR = BASE_DIR / "_metadata" / "documents"

# Corrections manuelles basées sur l'analyse
CORRECTIONS = {
    # DOS = Dossiers documentaires → guide_pratique
    "csn2023_dos_av_2023.metadata.json": {
        "type": "guide_pratique",
        "label": "Guide pratique",
        "domaines": ["documentation métier", "bonnes pratiques"]
    },
    "csn2023_dos_be_2023.metadata.json": {
        "type": "guide_pratique",
        "label": "Guide pratique",
        "domaines": ["documentation métier", "bonnes pratiques"]
    },
    "csn2023_dos_acs_tm_2023.metadata.json": {
        "type": "guide_pratique",
        "label": "Guide pratique",
        "domaines": ["documentation métier", "bonnes pratiques"]
    },
    # Brochures = guides pratiques
    "csn2022_calculs_financiers_brochure_explicative_de_l_outil.metadata.json": {
        "type": "guide_pratique",
        "label": "Guide pratique",
        "domaines": ["documentation métier", "calculs financiers"]
    },
    "csn2025_brochure_csn_cm_2025.metadata.json": {
        "type": "guide_pratique",
        "label": "Guide pratique",
        "domaines": ["œuvres sociales", "comité mixte"]
    },
    "csn2025_brochure_2025_oeuvres_sociales_du_notariat_comite_mixte.metadata.json": {
        "type": "guide_pratique",
        "label": "Guide pratique",
        "domaines": ["œuvres sociales", "comité mixte"]
    },
    # Fiches réflexes = guides pratiques
    "csn2023_cyber_attaque_fiche_reflexes_csn_03_02_2023.metadata.json": {
        "type": "guide_pratique",
        "label": "Guide pratique",
        "domaines": ["cybersécurité", "procédures d'urgence"]
    },
    # Notes d'information = guides/instructions
    "csn2025_20250123_partage_de_la_valeur_au_sein_des_offices_de_11_a_49_salaries.metadata.json": {
        "type": "guide_pratique",
        "label": "Guide pratique",
        "domaines": ["partage de la valeur", "intéressement"]
    },
    # Ordonnances = décrets
    "csn2023_ordonnance_plr_8_02_23.metadata.json": {
        "type": "decret_ordonnance",
        "label": "Décret / Ordonnance",
        "domaines": ["textes réglementaires", "législation"]
    },
    # Tableaux récapitulatifs = guides
    "csn2023_tableau_recapitulatif_annexe_circulaire_n_2023_2.metadata.json": {
        "type": "guide_pratique",
        "label": "Guide pratique",
        "domaines": ["documentation métier", "synthèse"]
    },
    # Appel à vigilance = conformité
    "csn2022_appel_a_vigilance_de_la_direction_generale_du_tresor.metadata.json": {
        "type": "conformite",
        "label": "Conformité",
        "domaines": ["conformité", "vigilance financière"]
    },
    # Manuel d'utilisation = guide pratique
    "csn2025_manuel_d_utilisation_salarie.metadata.json": {
        "type": "guide_pratique",
        "label": "Guide pratique",
        "domaines": ["documentation métier", "outils"]
    },
    # Analyse risques = conformité
    "csn2019_analyse_nationale_des_risques_lcb_ft_en_france_septembre_2019.metadata.json": {
        "type": "conformite",
        "label": "Conformité",
        "domaines": ["LCB-FT", "anti-blanchiment"]
    },
    # Processus = guide pratique
    "csn2021_processus_ciclade_septembre_2021.metadata.json": {
        "type": "guide_pratique",
        "label": "Guide pratique",
        "domaines": ["procédures", "comptes inactifs"]
    },
    # Acte électronique = guide
    "csn2019_acte_electro_ssp.metadata.json": {
        "type": "guide_pratique",
        "label": "Guide pratique",
        "domaines": ["acte électronique", "procédures"]
    },
    # Accord F/H = accord de branche
    "csn2019_accord_f_h.metadata.json": {
        "type": "accord_branche",
        "label": "Accord de branche",
        "domaines": ["égalité professionnelle", "droit social"]
    },
}


def apply_corrections():
    """Applique les corrections de classification."""

    print("Correction des classifications")
    print("=" * 60)
    print()

    corrected = 0

    for filename, correction in CORRECTIONS.items():
        filepath = DOCS_METADATA_DIR / filename

        if not filepath.exists():
            print(f"⚠️  Fichier non trouvé: {filename}")
            continue

        # Charger le fichier
        with open(filepath, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        old_type = metadata['classification']['type_document']
        new_type = correction['type']

        if old_type == new_type:
            print(f"✓  {filename[:50]} - déjà correct")
            continue

        # Appliquer la correction
        metadata['classification']['type_document'] = correction['type']
        metadata['classification']['label'] = correction['label']
        metadata['classification']['domaines_juridiques'] = correction['domaines']

        # Sauvegarder
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"✓  {filename[:50]}")
        print(f"   {old_type} → {new_type}")
        corrected += 1

    print()
    print(f"Corrections appliquées: {corrected}")


if __name__ == "__main__":
    apply_corrections()
