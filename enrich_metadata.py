#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enrichissement des métadonnées par extraction de contenu PDF
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from collections import Counter
from PyPDF2 import PdfReader

BASE_DIR = Path(__file__).parent
SOURCES_DIR = BASE_DIR / "sources_documentaires"
METADATA_DIR = BASE_DIR / "_metadata"
DOCS_METADATA_DIR = METADATA_DIR / "documents"

# Termes juridiques notariaux à détecter
TERMES_NOTARIAUX = {
    "acte authentique": ["acte notarié", "instrumentum"],
    "minute": ["original de l'acte", "archive notariale"],
    "convention collective": ["CCN", "IDCC 2205"],
    "conseil supérieur du notariat": ["CSN"],
    "avenant": ["modification", "amendement"],
    "circulaire": ["instruction", "note d'information"],
    "LCB-FT": ["lutte contre le blanchiment", "anti-blanchiment"],
    "OPCO": ["opérateur de compétences"],
    "période d'essai": ["essai professionnel"],
    "licenciement": ["rupture contrat", "procédure disciplinaire"],
    "formation professionnelle": ["formation continue", "développement compétences"],
    "rémunération": ["salaire", "traitement", "émoluments"],
    "congés payés": ["congés annuels", "droits à congés"],
    "prévoyance": ["protection sociale", "assurance"],
    "harcèlement": ["harcèlement moral", "harcèlement sexuel"],
    "égalité professionnelle": ["égalité femmes-hommes"],
    "intéressement": ["participation aux bénéfices"],
    "RGPD": ["protection des données", "données personnelles"],
    "cybersécurité": ["sécurité informatique", "cyber-risques"],
    "tarification": ["émoluments", "honoraires"],
}

# Patterns pour extraire des informations
PATTERNS = {
    'date': r'\b(\d{1,2})\s*(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s*(\d{4})\b',
    'article': r'\b[Aa]rticle\s+(\d+(?:\.\d+)?)\b',
    'decret': r'\b[Dd]écret\s*n?°?\s*(\d{4}-\d+)\b',
    'loi': r'\b[Ll]oi\s*n?°?\s*(\d{4}-\d+)\b',
    'montant': r'\b(\d+(?:\s?\d{3})*(?:,\d+)?)\s*(?:€|euros?)\b',
    'pourcentage': r'\b(\d+(?:,\d+)?)\s*%\b',
}


def extract_pdf_text(pdf_path, max_pages=10):
    """Extrait le texte des premières pages d'un PDF."""
    try:
        text = ""
        reader = PdfReader(pdf_path)
        num_pages = min(len(reader.pages), max_pages)

        for i in range(num_pages):
            page_text = reader.pages[i].extract_text()
            if page_text:
                text += page_text + "\n\n"
        return text.strip()
    except Exception as e:
        print(f"   Erreur extraction {pdf_path.name}: {str(e)[:50]}")
        return ""


def generate_summary(text, max_sentences=3):
    """Génère un résumé à partir du texte extrait."""
    if not text:
        return ""

    # Nettoyer le texte
    text = re.sub(r'\s+', ' ', text)

    # Extraire les premières phrases significatives
    sentences = re.split(r'[.!?]\s+', text)
    summary_sentences = []

    for sentence in sentences:
        sentence = sentence.strip()
        # Ignorer les phrases trop courtes ou trop longues
        if 20 < len(sentence) < 300:
            # Ignorer les en-têtes/pieds de page
            if not re.match(r'^(page\s+\d+|fil-info|csn|circulaire)', sentence.lower()):
                summary_sentences.append(sentence)
                if len(summary_sentences) >= max_sentences:
                    break

    if summary_sentences:
        return ". ".join(summary_sentences) + "."
    return ""


def extract_key_terms(text):
    """Extrait les termes clés notariaux du texte."""
    if not text:
        return []

    text_lower = text.lower()
    found_terms = []

    for term, synonyms in TERMES_NOTARIAUX.items():
        # Chercher le terme principal
        if term.lower() in text_lower:
            found_terms.append({
                "terme": term,
                "synonymes": synonyms,
                "frequence": text_lower.count(term.lower())
            })
        else:
            # Chercher les synonymes
            for syn in synonyms:
                if syn.lower() in text_lower:
                    found_terms.append({
                        "terme": term,
                        "synonymes": synonyms,
                        "frequence": text_lower.count(syn.lower())
                    })
                    break

    # Trier par fréquence
    found_terms.sort(key=lambda x: x["frequence"], reverse=True)
    return found_terms[:10]


def extract_dates_mentioned(text):
    """Extrait les dates mentionnées dans le document."""
    if not text:
        return []

    dates = []
    matches = re.findall(PATTERNS['date'], text, re.IGNORECASE)

    mois_map = {
        'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
        'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
        'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
    }

    for jour, mois, annee in matches:
        mois_num = mois_map.get(mois.lower(), '01')
        date_str = f"{annee}-{mois_num}-{jour.zfill(2)}"
        if date_str not in dates:
            dates.append(date_str)

    return sorted(dates)[:5]


def extract_references(text):
    """Extrait les références légales mentionnées."""
    if not text:
        return []

    refs = []

    # Articles de loi
    articles = re.findall(PATTERNS['article'], text)
    for art in articles[:5]:
        refs.append(f"Article {art}")

    # Décrets
    decrets = re.findall(PATTERNS['decret'], text)
    for dec in decrets[:3]:
        refs.append(f"Décret {dec}")

    # Lois
    lois = re.findall(PATTERNS['loi'], text)
    for loi in lois[:3]:
        refs.append(f"Loi {loi}")

    return list(set(refs))


def generate_questions_from_content(text, doc_type):
    """Génère des questions typiques basées sur le contenu."""
    if not text:
        return []

    questions = []
    text_lower = text.lower()

    # Questions génériques basées sur les thèmes détectés
    if "salaire" in text_lower or "rémunération" in text_lower:
        questions.append("Quelles sont les nouvelles grilles de salaires ?")
        questions.append("Quel est l'impact sur la rémunération des salariés ?")

    if "formation" in text_lower:
        questions.append("Quelles formations sont concernées par ce document ?")
        questions.append("Comment financer ces formations ?")

    if "licenciement" in text_lower or "rupture" in text_lower:
        questions.append("Quelle est la procédure de licenciement applicable ?")
        questions.append("Quels sont les délais à respecter ?")

    if "congés" in text_lower or "congé" in text_lower:
        questions.append("Comment sont calculés les droits à congés ?")
        questions.append("Quelles sont les modalités de prise de congés ?")

    if "harcèlement" in text_lower:
        questions.append("Quelles sont les mesures de prévention du harcèlement ?")
        questions.append("Comment signaler un cas de harcèlement ?")

    if "cyber" in text_lower or "informatique" in text_lower:
        questions.append("Quelles sont les obligations de sécurité informatique ?")
        questions.append("Comment se protéger contre les cyberattaques ?")

    if "assurance" in text_lower or "garantie" in text_lower:
        questions.append("Quelles garanties sont couvertes ?")
        questions.append("Quels sont les montants de franchise ?")

    if "immobilier" in text_lower or "transaction" in text_lower:
        questions.append("Quelles sont les tendances du marché immobilier ?")
        questions.append("Comment analyser ces données pour mon secteur ?")

    # Ajouter des questions basées sur les montants/pourcentages détectés
    if re.search(PATTERNS['montant'], text):
        questions.append("Quels sont les montants mentionnés dans ce document ?")

    if re.search(PATTERNS['pourcentage'], text):
        questions.append("Quels pourcentages sont applicables ?")

    # Limiter à 5 questions uniques et pertinentes
    return list(set(questions))[:5]


def extract_important_numbers(text):
    """Extrait les montants et pourcentages importants."""
    if not text:
        return {}

    numbers = {}

    # Montants en euros
    montants = re.findall(PATTERNS['montant'], text)
    if montants:
        numbers['montants_euros'] = list(set(montants))[:5]

    # Pourcentages
    pourcentages = re.findall(PATTERNS['pourcentage'], text)
    if pourcentages:
        numbers['pourcentages'] = list(set(pourcentages))[:5]

    return numbers


def enrich_metadata(metadata, pdf_text):
    """Enrichit les métadonnées avec le contenu extrait du PDF."""

    if not pdf_text:
        return metadata

    # 1. Générer un meilleur résumé
    summary = generate_summary(pdf_text)
    if summary and len(summary) > 50:
        metadata['resume'] = summary

    # 2. Extraire le vocabulaire spécifique
    key_terms = extract_key_terms(pdf_text)
    if key_terms:
        metadata['vocabulaire_specifique'] = [
            {
                "terme": t["terme"],
                "synonymes": t["synonymes"],
                "definition": "",  # À enrichir manuellement
                "contexte_utilisation": f"Mentionné {t['frequence']} fois dans le document"
            }
            for t in key_terms
        ]

    # 3. Extraire les dates importantes
    dates = extract_dates_mentioned(pdf_text)
    if dates:
        metadata['dates_mentionnees'] = dates
        # Mettre à jour la date d'effet si trouvée
        if dates and dates[0] > metadata['metadata'].get('date_publication', '2000-01-01'):
            metadata['metadata']['date_effet'] = dates[0]

    # 4. Générer de meilleures questions typiques
    doc_type = metadata['classification']['type_document']
    new_questions = generate_questions_from_content(pdf_text, doc_type)
    if new_questions:
        # Combiner avec les questions existantes
        existing = metadata.get('questions_typiques', [])
        all_questions = list(set(existing + new_questions))
        metadata['questions_typiques'] = all_questions[:8]

    # 5. Extraire les références légales
    refs = extract_references(pdf_text)
    if refs:
        metadata['relations_documentaires']['reference'] = refs

    # 6. Extraire les chiffres importants
    numbers = extract_important_numbers(pdf_text)
    if numbers:
        metadata['donnees_chiffrees'] = numbers

    # 7. Enrichir les mots-clés
    existing_keywords = set(metadata.get('mots_cles', []))

    # Ajouter des mots-clés basés sur le contenu
    text_lower = pdf_text.lower()
    keyword_triggers = {
        'salaire': 'rémunération',
        'formation': 'formation professionnelle',
        'licenciement': 'procédure disciplinaire',
        'congé': 'congés payés',
        'cyber': 'cybersécurité',
        'rgpd': 'protection des données',
        'immobilier': 'transactions immobilières',
        'assurance': 'assurance professionnelle',
        'harcèlement': 'prévention harcèlement',
    }

    for trigger, keyword in keyword_triggers.items():
        if trigger in text_lower:
            existing_keywords.add(keyword)

    metadata['mots_cles'] = sorted(list(existing_keywords))

    return metadata


def process_all_documents():
    """Traite tous les documents et enrichit leurs métadonnées."""

    print("Enrichissement des métadonnées par analyse de contenu PDF")
    print("=" * 60)
    print()

    # Charger tous les fichiers metadata
    metadata_files = list(DOCS_METADATA_DIR.glob("*.metadata.json"))
    total = len(metadata_files)

    print(f"Documents à traiter : {total}")
    print()

    processed = 0
    errors = 0
    skipped = 0

    for i, meta_file in enumerate(metadata_files, 1):
        # Charger les métadonnées existantes
        with open(meta_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # Trouver le fichier PDF correspondant
        pdf_path = BASE_DIR / metadata['fichier']

        print(f"[{i}/{total}] {metadata['nom_fichier'][:60]}...")

        # Vérifier si c'est un PDF
        if not pdf_path.suffix.lower() == '.pdf':
            print(f"   Ignoré (non-PDF)")
            skipped += 1
            continue

        if not pdf_path.exists():
            print(f"   Fichier non trouvé")
            errors += 1
            continue

        # Extraire le texte du PDF
        pdf_text = extract_pdf_text(pdf_path, max_pages=5)

        if not pdf_text:
            print(f"   Pas de texte extrait")
            skipped += 1
            continue

        # Enrichir les métadonnées
        metadata = enrich_metadata(metadata, pdf_text)

        # Sauvegarder les métadonnées enrichies
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"   ✓ Enrichi (résumé: {len(metadata.get('resume', ''))} chars, "
              f"{len(metadata.get('vocabulaire_specifique', []))} termes)")

        processed += 1

    print()
    print("=" * 60)
    print(f"Traitement terminé !")
    print(f"  - Documents enrichis : {processed}")
    print(f"  - Ignorés (non-PDF) : {skipped}")
    print(f"  - Erreurs : {errors}")


if __name__ == "__main__":
    process_all_documents()
