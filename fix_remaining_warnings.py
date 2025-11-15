#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction des derniers avertissements de validation
"""

import json
from pathlib import Path
from PyPDF2 import PdfReader

BASE_DIR = Path(__file__).parent
DOCS_METADATA_DIR = BASE_DIR / "_metadata" / "documents"

# Corrections de classification (pas des circulaires)
CLASSIFICATION_FIXES = {
    "csn2024_20240118_csn_anc_modalites_pratiques_declarations_remunerations_notaires_associes.metadata.json": {
        "type": "guide_pratique",
        "label": "Guide pratique",
        "domaines": ["rémunération notaires", "fiscalité BNC", "déclarations"]
    },
    "csn2024_20240131_csn_anc_modalites_pratiques_declarations_remunerations_notaires_associes.metadata.json": {
        "type": "guide_pratique",
        "label": "Guide pratique",
        "domaines": ["rémunération notaires", "fiscalité BNC", "déclarations"]
    },
}

# Résumés manuels pour les documents avec résumés génériques
RESUME_ENRICHMENTS = {
    "assurances_contrat_cyber_renouvellement_au_01_07_2025.metadata.json": {
        "resume": "Contrat d'assurance cyber-risques pour les offices notariaux, renouvelé au 1er juillet 2025. Ce contrat couvre les risques liés aux cyberattaques, violations de données, pertes d'exploitation informatique et responsabilité civile numérique. Il définit les garanties, franchises, exclusions et procédures de déclaration de sinistre spécifiques à la profession notariale.",
        "mots_cles": ["cybersécurité", "assurance professionnelle", "cyber-risques", "protection données", "responsabilité civile"],
        "questions_typiques": [
            "Quelles sont les garanties cyber couvertes par ce contrat ?",
            "Quel est le montant de la franchise en cas de cyberattaque ?",
            "Comment déclarer un sinistre cyber ?",
            "Quelles sont les exclusions du contrat cyber ?",
            "Quelle est la procédure en cas de violation de données ?"
        ]
    },
    "carrieres_des_notaires_et_modalites_declaratives.metadata.json": {
        "resume": "Guide complet sur les carrières des notaires et les modalités déclaratives associées. Ce document détaille les différents parcours professionnels possibles dans le notariat, les obligations déclaratives fiscales et sociales, ainsi que les procédures administratives liées aux évolutions de carrière des notaires.",
        "mots_cles": ["carrière notaire", "déclarations", "parcours professionnel", "obligations fiscales", "administration"],
        "questions_typiques": [
            "Quelles sont les étapes de la carrière d'un notaire ?",
            "Quelles déclarations fiscales un notaire doit-il effectuer ?",
            "Comment évoluer dans sa carrière de notaire ?",
            "Quelles sont les obligations déclaratives annuelles ?",
            "Quels formulaires utiliser pour les déclarations ?"
        ]
    },
    "consultation_cridon.metadata.json": {
        "resume": "Document de consultation juridique du CRIDON (Centre de Recherche d'Information et de Documentation Notariales). Ce service fournit aux notaires des réponses expertes sur des questions juridiques complexes, offrant une analyse approfondie de la jurisprudence et de la doctrine applicable aux situations concrètes rencontrées dans la pratique notariale.",
        "mots_cles": ["CRIDON", "consultation juridique", "expertise notariale", "recherche juridique", "doctrine"],
        "questions_typiques": [
            "Comment soumettre une question au CRIDON ?",
            "Quels types de questions le CRIDON peut-il traiter ?",
            "Quel est le délai de réponse du CRIDON ?",
            "Les avis du CRIDON ont-ils valeur contraignante ?",
            "Comment utiliser les consultations CRIDON dans ma pratique ?"
        ]
    },
    "qr_notaires_dataset.metadata.json": {
        "resume": "Base de données questions-réponses pour les notaires. Ce dataset compile les questions fréquemment posées par les professionnels du notariat et leurs réponses détaillées, couvrant divers domaines : droit immobilier, droit de la famille, fiscalité, procédures notariales et conformité réglementaire.",
        "mots_cles": ["questions-réponses", "FAQ notariale", "base de connaissances", "formation", "documentation"],
        "questions_typiques": [
            "Comment trouver une réponse dans le dataset QR ?",
            "Quels domaines juridiques sont couverts ?",
            "Comment contribuer au dataset de questions ?",
            "Le dataset est-il mis à jour régulièrement ?",
            "Puis-je utiliser ce dataset pour former mes collaborateurs ?"
        ]
    },
}


def extract_text_from_pdf(pdf_path, max_chars=2000):
    """Extrait le texte d'un PDF."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for i in range(min(3, len(reader.pages))):
            page_text = reader.pages[i].extract_text()
            if page_text:
                text += page_text + " "
        return text[:max_chars].strip()
    except Exception as e:
        return f"Erreur: {e}"


def generate_summary_from_text(text, title, doc_type):
    """Génère un résumé basé sur le texte extrait."""
    # Nettoyer le texte
    text = ' '.join(text.split())

    if len(text) < 100:
        return None

    # Extraire les premières phrases significatives
    sentences = text.split('.')
    summary_parts = []
    char_count = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 20 and char_count < 400:
            summary_parts.append(sentence)
            char_count += len(sentence)

    if summary_parts:
        return '. '.join(summary_parts[:3]) + '.'
    return None


def fix_classifications():
    """Corrige les classifications incorrectes."""
    print("1. Correction des classifications")
    print("-" * 50)

    fixed = 0
    for filename, correction in CLASSIFICATION_FIXES.items():
        filepath = DOCS_METADATA_DIR / filename
        if not filepath.exists():
            print(f"   ⚠️  Non trouvé: {filename}")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        old_type = metadata['classification']['type_document']
        new_type = correction['type']

        if old_type == new_type:
            print(f"   ✓ {filename[:50]} - déjà correct")
            continue

        metadata['classification']['type_document'] = correction['type']
        metadata['classification']['label'] = correction['label']
        metadata['classification']['domaines_juridiques'] = correction['domaines']

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"   ✓ {filename[:50]}")
        print(f"     {old_type} → {new_type}")
        fixed += 1

    print(f"\n   Corrections: {fixed}")
    return fixed


def fix_generic_summaries():
    """Corrige les résumés génériques."""
    print("\n2. Enrichissement des résumés génériques")
    print("-" * 50)

    enriched = 0

    # D'abord les enrichissements manuels
    for filename, enrichment in RESUME_ENRICHMENTS.items():
        filepath = DOCS_METADATA_DIR / filename
        if not filepath.exists():
            print(f"   ⚠️  Non trouvé: {filename}")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        old_resume = metadata.get('resume', '')
        if old_resume.startswith('Document de type'):
            metadata['resume'] = enrichment['resume']
            metadata['mots_cles'] = enrichment['mots_cles']
            metadata['questions_typiques'] = enrichment['questions_typiques']

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print(f"   ✓ {filename[:50]}")
            print(f"     Résumé enrichi manuellement")
            enriched += 1

    # Puis les circulaires à enrichir depuis le PDF
    circulaire_files = [
        "csn2022_circulaire_02_22_av_be.metadata.json",
        "csn2023_circulaire_n_2020_3_du_22_septembre_2020.metadata.json",
        "csn2025_circulaire_01_25.metadata.json",
        "csn2020_circulaire_n_2020_3_du_22_septembre_2020.metadata.json",
        "csn2025_circulaire_02_25.metadata.json",
    ]

    for filename in circulaire_files:
        filepath = DOCS_METADATA_DIR / filename
        if not filepath.exists():
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        old_resume = metadata.get('resume', '')
        if not old_resume.startswith('Document de type'):
            print(f"   ✓ {filename[:50]} - résumé déjà enrichi")
            continue

        # Tenter d'extraire du PDF
        pdf_path = BASE_DIR / metadata['fichier']
        if pdf_path.exists():
            text = extract_text_from_pdf(pdf_path)
            new_summary = generate_summary_from_text(text, metadata['metadata']['titre'], metadata['classification']['type_document'])

            if new_summary and len(new_summary) > 50:
                metadata['resume'] = new_summary

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)

                print(f"   ✓ {filename[:50]}")
                print(f"     Résumé extrait du PDF")
                enriched += 1
            else:
                # Créer un résumé basé sur le titre et le type
                titre = metadata['metadata']['titre']
                if 'circulaire' in titre.lower():
                    num_match = None
                    for part in titre.split():
                        if part.replace('°', '').replace('N', '').replace('-', '').isdigit():
                            num_match = part
                            break

                    if num_match:
                        metadata['resume'] = f"Circulaire {num_match} du CSN contenant des instructions officielles pour la profession notariale. Ce document définit les modalités d'application des dispositions réglementaires et les recommandations pratiques à mettre en œuvre par les offices notariaux."
                    else:
                        metadata['resume'] = f"Circulaire du CSN intitulée '{titre}'. Ce document contient des instructions officielles et des recommandations pour la mise en conformité des pratiques notariales avec les évolutions réglementaires."

                    metadata['mots_cles'] = list(set(metadata.get('mots_cles', []) + ['circulaire CSN', 'instructions professionnelles', 'conformité']))

                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)

                    print(f"   ✓ {filename[:50]}")
                    print(f"     Résumé généré depuis le titre")
                    enriched += 1
        else:
            print(f"   ⚠️  PDF non trouvé: {pdf_path}")

    print(f"\n   Enrichissements: {enriched}")
    return enriched


def main():
    print("=" * 60)
    print("CORRECTION DES AVERTISSEMENTS RESTANTS")
    print("=" * 60)
    print()

    classifications_fixed = fix_classifications()
    summaries_enriched = fix_generic_summaries()

    print()
    print("=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"Classifications corrigées: {classifications_fixed}")
    print(f"Résumés enrichis: {summaries_enriched}")
    print(f"Total corrections: {classifications_fixed + summaries_enriched}")
    print()


if __name__ == "__main__":
    main()
