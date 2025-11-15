#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correction des problèmes de qualité identifiés dans l'analyse
- Dates de publication incorrectes pour Fil-Infos
- Titres non-descriptifs
- Auteurs génériques
- Questions typiques non-pertinentes
"""

import json
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
DOCS_METADATA_DIR = BASE_DIR / "_metadata" / "documents"

# Mois français → numéro
MOIS_FR = {
    'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
    'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
    'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
}

def extract_filinfo_date(resume):
    """Extrait la date réelle depuis le résumé du Fil-Info."""
    # Pattern: "Semaine du DD MOIS YYYY au DD MOIS YYYY"
    pattern = r'Semaine du (\d{1,2})\s+(\w+)\s+(\d{4})'
    match = re.search(pattern, resume, re.IGNORECASE)

    if match:
        jour = match.group(1).zfill(2)
        mois_str = match.group(2).lower()
        annee = match.group(3)

        mois = MOIS_FR.get(mois_str, '01')
        return f"{annee}-{mois}-{jour}"

    # Pattern alternatif: "N° XXXX" avec année dans le contexte
    pattern2 = r'(\d{4})[^\d]*N°\s*(\d+)'
    match2 = re.search(pattern2, resume)
    if match2:
        annee = match2.group(1)
        return f"{annee}-01-01"

    return None


def extract_filinfo_subject(resume):
    """Extrait le sujet principal du Fil-Info depuis le résumé."""
    # Chercher après "N° XXXX" ou dans les premières lignes

    # Retirer les infos de semaine
    text = re.sub(r'Semaine du.*?N°\s*\d+\s*', '', resume, flags=re.IGNORECASE)
    text = re.sub(r'N°\s*\d+\s*', '', text)

    # Prendre les premiers mots significatifs
    text = text.strip()

    # Nettoyer et extraire
    if len(text) > 10:
        # Prendre la première phrase ou les 50 premiers caractères
        sentences = text.split('.')
        if sentences and len(sentences[0]) > 10:
            subject = sentences[0].strip()[:80]
            # Nettoyer
            subject = re.sub(r'\s+', ' ', subject)
            return subject

    return None


def determine_author(doc_type, categorie_dossier, titre):
    """Détermine l'auteur approprié selon le type de document."""
    if doc_type == 'fil_info':
        return "Chambre des Notaires de Normandie"
    elif doc_type in ['circulaire_csn', 'guide_pratique'] and 'CSN' in titre.upper():
        return "CSN"
    elif doc_type == 'avenant_ccn':
        return "Partenaires sociaux du notariat"
    elif doc_type == 'accord_branche':
        return "Partenaires sociaux du notariat"
    elif doc_type == 'decret_ordonnance':
        return "Journal Officiel"
    elif categorie_dossier == "Assurances":
        return "Compagnie d'assurance"
    elif 'CRIDON' in titre.upper():
        return "CRIDON"
    else:
        return "Profession notariale"


def filter_questions_by_type(questions, doc_type):
    """Filtre les questions non-pertinentes selon le type de document."""
    # Questions à supprimer pour certains types
    remove_patterns = {
        'assurance': [
            r'comment financer.*formation',
            r'grille.*salaire',
            r'classification.*emploi'
        ],
        'fil_info': [
            r'comment financer.*formation'
        ],
        'conformite': [
            r'grille.*salaire',
            r'classification.*emploi'
        ],
        'decret_ordonnance': [
            r'comment financer.*formation'
        ]
    }

    patterns_to_remove = remove_patterns.get(doc_type, [])

    filtered = []
    for q in questions:
        should_keep = True
        for pattern in patterns_to_remove:
            if re.search(pattern, q, re.IGNORECASE):
                should_keep = False
                break
        if should_keep:
            filtered.append(q)

    return filtered


def fix_all_metadata():
    """Corrige tous les problèmes de qualité identifiés."""
    stats = {
        'dates_fixed': 0,
        'titles_enriched': 0,
        'authors_fixed': 0,
        'questions_filtered': 0,
        'total_processed': 0
    }

    meta_files = list(DOCS_METADATA_DIR.glob("*.metadata.json"))
    print(f"Documents à traiter: {len(meta_files)}\n")

    for meta_file in meta_files:
        with open(meta_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        modified = False
        doc_type = metadata['classification']['type_document']
        titre = metadata['metadata']['titre']
        resume = metadata.get('resume', '')
        categorie = metadata['classification'].get('categorie_dossier', '')

        # 1. Corriger les dates pour les Fil-Infos
        if doc_type == 'fil_info':
            current_date = metadata['metadata'].get('date_publication', '')
            if current_date == '2025-01-01' or not current_date:
                new_date = extract_filinfo_date(resume)
                if new_date:
                    metadata['metadata']['date_publication'] = new_date
                    metadata['metadata']['date_effet'] = new_date
                    stats['dates_fixed'] += 1
                    modified = True

        # 2. Enrichir les titres des Fil-Infos
        if doc_type == 'fil_info':
            if titre.lower().startswith('fil info') or titre.lower().startswith('fil-info'):
                # Extraire le numéro
                num_match = re.search(r'(\d+)', titre)
                if num_match:
                    numero = num_match.group(1)
                    subject = extract_filinfo_subject(resume)
                    if subject:
                        new_title = f"Fil-Info N°{numero} - {subject}"
                        if len(new_title) > 100:
                            new_title = new_title[:97] + "..."
                        metadata['metadata']['titre'] = new_title
                        # Titre court
                        short_subject = subject[:30] + "..." if len(subject) > 30 else subject
                        metadata['metadata']['titre_court'] = f"Fil-Info {numero} - {short_subject}"
                        stats['titles_enriched'] += 1
                        modified = True

        # 3. Corriger les auteurs génériques
        current_author = metadata['metadata'].get('auteur', '')
        if current_author == 'Profession notariale' or not current_author:
            new_author = determine_author(doc_type, categorie, titre)
            if new_author != current_author:
                metadata['metadata']['auteur'] = new_author
                stats['authors_fixed'] += 1
                modified = True

        # 4. Filtrer les questions non-pertinentes
        questions = metadata.get('questions_typiques', [])
        if questions:
            filtered_questions = filter_questions_by_type(questions, doc_type)
            if len(filtered_questions) < len(questions):
                metadata['questions_typiques'] = filtered_questions
                stats['questions_filtered'] += 1
                modified = True

        # Sauvegarder si modifié
        if modified:
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            stats['total_processed'] += 1

    return stats


def main():
    print("=" * 60)
    print("CORRECTION DES PROBLÈMES DE QUALITÉ")
    print("=" * 60)
    print()

    stats = fix_all_metadata()

    print("\n" + "=" * 60)
    print("RÉSUMÉ DES CORRECTIONS")
    print("=" * 60)
    print(f"Dates corrigées (Fil-Infos)    : {stats['dates_fixed']}")
    print(f"Titres enrichis (Fil-Infos)    : {stats['titles_enriched']}")
    print(f"Auteurs corrigés                : {stats['authors_fixed']}")
    print(f"Questions filtrées              : {stats['questions_filtered']}")
    print(f"Total documents modifiés        : {stats['total_processed']}")
    print()


if __name__ == "__main__":
    main()
