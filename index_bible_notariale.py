#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Index Bible Notariale - Génération d'index et métadonnées KM
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Configuration
BASE_DIR = Path(__file__).parent
SOURCES_DIR = BASE_DIR / "sources_documentaires"
METADATA_DIR = BASE_DIR / "_metadata"
DOCS_METADATA_DIR = METADATA_DIR / "documents"

# Patterns de détection
DATE_PATTERNS = [
    (r'(\d{4})(\d{2})(\d{2})', r'\1-\2-\3'),  # YYYYMMDD
    (r'(\d{2})[\./](\d{2})[\./](\d{4})', r'\3-\2-\1'),  # DD/MM/YYYY ou DD.MM.YYYY
]

REFERENCE_PATTERNS = {
    'avenant': r'[Aa]venant\s*n?[°º]?\s*(\d+)',
    'circulaire': r'[Cc]irculaire\s*(?:N[°º]?)?\s*(\d{4}[-/]\d+|\d+[-/]\d+)',
    'fil_info': r'fil-info-(\d+)',
}

# Classification par type de document
DOCUMENT_TYPES = {
    'circulaire_csn': {
        'patterns': [r'[Cc]irculaire', r'CIRCULAIRE'],
        'label': 'Circulaire CSN',
        'domaines': ['réglementation notariale', 'instructions professionnelles']
    },
    'avenant_ccn': {
        'patterns': [r'[Aa]venant\s*n?[°º]?\s*\d+', r'avenant_n\d+'],
        'label': 'Avenant CCN',
        'domaines': ['convention collective', 'droit social']
    },
    'accord_branche': {
        'patterns': [r'[Aa]ccord', r'accord.*branche', r'accord.*salaire'],
        'label': 'Accord de branche',
        'domaines': ['négociation collective', 'droit social']
    },
    'fil_info': {
        'patterns': [r'fil-info'],
        'label': 'Fil-Info',
        'domaines': ['actualité juridique', 'veille professionnelle']
    },
    'guide_pratique': {
        'patterns': [r'[Gg]uide', r'[Mm]anuel', r'[Bb]rochure', r'fiche.*pratique'],
        'label': 'Guide pratique',
        'domaines': ['documentation métier', 'bonnes pratiques']
    },
    'decret_ordonnance': {
        'patterns': [r'[Dd][ée]cret', r'[Oo]rdonnance', r'd_\d+', r'JO\s*ORDO'],
        'label': 'Décret / Ordonnance',
        'domaines': ['textes réglementaires', 'législation']
    },
    'assurance': {
        'patterns': [r'[Aa]ssurance', r'[Cc]ontrat.*[Cc]yber', r'FLIPBOOK'],
        'label': 'Assurance',
        'domaines': ['assurance professionnelle', 'prévoyance']
    },
    'immobilier': {
        'patterns': [r'[Ii]mmobili[eè]re?', r'observatoire', r'CID\d+'],
        'label': 'Immobilier',
        'domaines': ['transactions immobilières', 'observatoire']
    },
    'formation': {
        'patterns': [r'[Ff]ormation', r'OPCO', r'alternance'],
        'label': 'Formation',
        'domaines': ['formation professionnelle', 'développement compétences']
    },
    'conformite': {
        'patterns': [r'LCB-?FT', r'[Cc]yber', r'RGPD', r'vigilance'],
        'label': 'Conformité',
        'domaines': ['conformité', 'sécurité', 'anti-blanchiment']
    }
}

# Vocabulaire notarial avec synonymes
VOCABULAIRE_NOTARIAL = [
    {
        "terme": "Convention Collective Nationale",
        "synonymes": ["CCN", "IDCC 2205", "convention du notariat", "accord de branche"],
        "definition": "Accord collectif régissant les conditions de travail et d'emploi dans le notariat",
        "domaine": "droit social"
    },
    {
        "terme": "Conseil Supérieur du Notariat",
        "synonymes": ["CSN", "instance nationale", "conseil supérieur"],
        "definition": "Instance représentative de la profession notariale au niveau national",
        "domaine": "institution"
    },
    {
        "terme": "Avenant",
        "synonymes": ["modification CCN", "amendement", "révision conventionnelle"],
        "definition": "Acte juridique modifiant ou complétant la convention collective",
        "domaine": "droit social"
    },
    {
        "terme": "Circulaire",
        "synonymes": ["instruction CSN", "note d'information", "directive professionnelle"],
        "definition": "Communication officielle du CSN donnant des instructions aux notaires",
        "domaine": "réglementation"
    },
    {
        "terme": "Fil-Info",
        "synonymes": ["bulletin d'actualité", "flash info", "newsletter notariale"],
        "definition": "Publication périodique d'actualités juridiques pour les notaires",
        "domaine": "veille juridique"
    },
    {
        "terme": "LCB-FT",
        "synonymes": ["lutte anti-blanchiment", "LAB", "compliance", "vigilance financière"],
        "definition": "Lutte contre le Blanchiment de Capitaux et le Financement du Terrorisme",
        "domaine": "conformité"
    },
    {
        "terme": "OPCO",
        "synonymes": ["opérateur de compétences", "financement formation", "OPCO EP"],
        "definition": "Organisme finançant la formation professionnelle des salariés",
        "domaine": "formation"
    },
    {
        "terme": "Société multi-offices",
        "synonymes": ["SMO", "holding notariale", "structure multi-offices"],
        "definition": "Structure permettant à un notaire de détenir des parts dans plusieurs offices",
        "domaine": "organisation"
    },
    {
        "terme": "Clerc de notaire",
        "synonymes": ["collaborateur", "employé d'office", "assistant notarial"],
        "definition": "Salarié qualifié travaillant dans une étude notariale",
        "domaine": "ressources humaines"
    },
    {
        "terme": "Acte authentique",
        "synonymes": ["acte notarié", "instrumentum", "acte public"],
        "definition": "Acte reçu par un officier public avec force probante et exécutoire",
        "domaine": "acte juridique"
    },
    {
        "terme": "Minute",
        "synonymes": ["original de l'acte", "archive notariale", "acte minuté"],
        "definition": "Original de l'acte authentique conservé par le notaire",
        "domaine": "conservation"
    },
    {
        "terme": "Office notarial",
        "synonymes": ["étude notariale", "office", "étude"],
        "definition": "Lieu d'exercice de la profession de notaire",
        "domaine": "organisation"
    },
    {
        "terme": "Actes courants",
        "synonymes": ["ACS", "actes simples", "actes standard"],
        "definition": "Actes notariés de complexité modérée avec tarification encadrée",
        "domaine": "tarification"
    },
    {
        "terme": "Biens d'exception",
        "synonymes": ["BE", "biens de prestige", "transactions exceptionnelles"],
        "definition": "Biens immobiliers de grande valeur avec honoraires spécifiques",
        "domaine": "tarification"
    },
    {
        "terme": "Taxe de Publicité Foncière",
        "synonymes": ["TPF", "droits d'enregistrement", "taxe immobilière"],
        "definition": "Impôt perçu lors des mutations immobilières",
        "domaine": "fiscalité"
    }
]

def extract_date_from_filename(filename):
    """Extrait la date du nom de fichier."""
    for pattern, replacement in DATE_PATTERNS:
        match = re.search(pattern, filename)
        if match:
            try:
                date_str = re.sub(pattern, replacement, match.group(0))
                # Valider la date
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                continue
    return None

def extract_reference(filename):
    """Extrait la référence du document."""
    for ref_type, pattern in REFERENCE_PATTERNS.items():
        match = re.search(pattern, filename)
        if match:
            return {
                'type': ref_type,
                'numero': match.group(1) if match.groups() else match.group(0)
            }
    return None

def classify_document(filename, folder_path):
    """Classifie le document selon son type."""
    # Vérifier d'abord le dossier parent
    folder_name = folder_path.name if folder_path != SOURCES_DIR else ""

    # Fil-infos
    if 'fil-info' in folder_name.lower() or 'fil-info' in filename.lower():
        return 'fil_info'

    # Convention Collective
    if 'convention collective' in folder_name.lower():
        if re.search(r'avenant', filename, re.IGNORECASE):
            return 'avenant_ccn'
        return 'accord_branche'

    # CSN par année
    if re.match(r'CSN\d{4}', folder_name):
        # Déterminer le sous-type
        if re.search(r'[Cc]irculaire', filename):
            return 'circulaire_csn'
        if re.search(r'[Aa]venant', filename):
            return 'avenant_ccn'
        if re.search(r'[Aa]ccord', filename):
            return 'accord_branche'
        return 'circulaire_csn'  # Par défaut pour CSN

    # Assurances
    if 'assurance' in folder_name.lower():
        return 'assurance'

    # Observatoire immobilier
    if 'observatoire' in folder_name.lower() or 'immobilier' in folder_name.lower():
        return 'immobilier'

    # RPN
    if 'rpn' in folder_name.lower():
        return 'guide_pratique'

    # Bonnes pratiques
    if 'bonnes pratiques' in folder_name.lower() or 'fiche' in folder_name.lower():
        return 'guide_pratique'

    # Recherche par pattern dans le nom de fichier
    for doc_type, config in DOCUMENT_TYPES.items():
        for pattern in config['patterns']:
            if re.search(pattern, filename):
                return doc_type

    return 'guide_pratique'  # Type par défaut

def generate_document_id(filename, folder_path):
    """Génère un ID unique pour le document."""
    # Nettoyer le nom
    base_name = Path(filename).stem
    # Enlever les accents et caractères spéciaux
    doc_id = base_name.lower()
    doc_id = re.sub(r'[àáâãäå]', 'a', doc_id)
    doc_id = re.sub(r'[èéêë]', 'e', doc_id)
    doc_id = re.sub(r'[ìíîï]', 'i', doc_id)
    doc_id = re.sub(r'[òóôõö]', 'o', doc_id)
    doc_id = re.sub(r'[ùúûü]', 'u', doc_id)
    doc_id = re.sub(r'[ýÿ]', 'y', doc_id)
    doc_id = re.sub(r'[ç]', 'c', doc_id)
    doc_id = re.sub(r'[ñ]', 'n', doc_id)
    doc_id = re.sub(r'[^a-z0-9]', '_', doc_id)
    doc_id = re.sub(r'_+', '_', doc_id)
    doc_id = doc_id.strip('_')

    # Ajouter le dossier parent si pertinent
    if folder_path != SOURCES_DIR:
        folder_clean = folder_path.name.lower()
        folder_clean = re.sub(r'[^a-z0-9]', '_', folder_clean)
        doc_id = f"{folder_clean}_{doc_id}"

    return doc_id[:100]  # Limiter la longueur

def generate_title(filename):
    """Génère un titre lisible à partir du nom de fichier."""
    base_name = Path(filename).stem
    # Nettoyer
    title = base_name.replace('_', ' ').replace('-', ' ')
    # Supprimer les dates en début
    title = re.sub(r'^\d{8}\s*', '', title)
    title = re.sub(r'^\d{4}\s*\d{2}\s*\d{2}\s*', '', title)
    # Nettoyer les espaces multiples
    title = re.sub(r'\s+', ' ', title).strip()
    return title if title else base_name

def extract_year_from_path(folder_path, filename):
    """Extrait l'année de référence."""
    # Depuis le dossier (CSN2025, etc.)
    folder_match = re.search(r'(\d{4})', folder_path.name)
    if folder_match:
        return int(folder_match.group(1))

    # Depuis le nom de fichier
    date = extract_date_from_filename(filename)
    if date:
        return int(date[:4])

    # Depuis la date dans le nom
    year_match = re.search(r'20(19|2[0-5])', filename)
    if year_match:
        return int('20' + year_match.group(1))

    return 2025  # Par défaut

def generate_questions_typiques(doc_type, reference=None):
    """Génère des questions typiques selon le type de document."""
    questions = {
        'circulaire_csn': [
            "Quelles sont les nouvelles obligations introduites par cette circulaire ?",
            "À quelle date cette circulaire entre-t-elle en vigueur ?",
            "Quels offices sont concernés par ces instructions ?"
        ],
        'avenant_ccn': [
            "Quels articles de la convention collective sont modifiés ?",
            "Quel impact sur les conditions de travail des salariés ?",
            "À partir de quand cet avenant s'applique-t-il ?"
        ],
        'accord_branche': [
            "Quelles sont les nouvelles dispositions négociées ?",
            "Qui sont les parties signataires de cet accord ?",
            "Quelle est la durée de validité de cet accord ?"
        ],
        'fil_info': [
            "Quelles sont les actualités juridiques importantes de ce numéro ?",
            "Y a-t-il des alertes ou points de vigilance pour les notaires ?",
            "Quelles sont les échéances mentionnées ?"
        ],
        'guide_pratique': [
            "Quelles sont les recommandations principales de ce guide ?",
            "Comment appliquer ces bonnes pratiques au quotidien ?",
            "Quels sont les points de vigilance à retenir ?"
        ],
        'decret_ordonnance': [
            "Quelles modifications réglementaires sont introduites ?",
            "Quelle est la date d'entrée en vigueur ?",
            "Quels articles du code sont concernés ?"
        ],
        'assurance': [
            "Quelles garanties sont couvertes par ce contrat ?",
            "Quels sont les montants de franchise ?",
            "Comment déclarer un sinistre ?"
        ],
        'immobilier': [
            "Quelles sont les tendances du marché immobilier ?",
            "Quels indicateurs sont suivis ?",
            "Comment interpréter ces données pour mon secteur ?"
        ],
        'formation': [
            "Quelles formations sont éligibles au financement ?",
            "Comment faire une demande de prise en charge ?",
            "Quels sont les délais de traitement ?"
        ],
        'conformite': [
            "Quelles sont les obligations de vigilance ?",
            "Comment mettre en place les procédures internes ?",
            "Quels contrôles effectuer ?"
        ]
    }
    return questions.get(doc_type, [
        "Quel est l'objet principal de ce document ?",
        "Quelles informations clés contient-il ?",
        "Comment s'applique-t-il à ma pratique ?"
    ])

def extract_keywords(filename, doc_type):
    """Extrait des mots-clés du nom de fichier."""
    keywords = set()

    # Mots-clés depuis le type
    type_config = DOCUMENT_TYPES.get(doc_type, {})
    if 'domaines' in type_config:
        keywords.update(type_config['domaines'])

    # Patterns spécifiques
    keyword_patterns = {
        r'salaire': 'rémunération',
        r'formation': 'formation professionnelle',
        r'licenciement': 'procédure disciplinaire',
        r'cyber': 'cybersécurité',
        r'harcèlement': 'harcèlement au travail',
        r'égalité': 'égalité professionnelle',
        r'intéressement': 'participation aux bénéfices',
        r'santé': 'complémentaire santé',
        r'retraite': 'prévoyance',
        r'congés': 'congés payés',
        r'période.*essai': 'période d\'essai',
    }

    filename_lower = filename.lower()
    for pattern, keyword in keyword_patterns.items():
        if re.search(pattern, filename_lower):
            keywords.add(keyword)

    return list(keywords)

def scan_documents():
    """Scanne tous les documents et génère les métadonnées."""
    documents = []

    for root, dirs, files in os.walk(SOURCES_DIR):
        root_path = Path(root)
        for filename in files:
            if filename.startswith('.'):
                continue

            file_path = root_path / filename
            relative_path = file_path.relative_to(BASE_DIR)

            # Extraire les métadonnées
            doc_type = classify_document(filename, root_path)
            doc_id = generate_document_id(filename, root_path)
            date_pub = extract_date_from_filename(filename)
            reference = extract_reference(filename)
            year = extract_year_from_path(root_path, filename)

            # Construire les métadonnées KM
            doc_metadata = {
                "document_id": doc_id,
                "fichier": str(relative_path),
                "nom_fichier": filename,
                "metadata": {
                    "titre": generate_title(filename),
                    "titre_court": generate_title(filename)[:50],
                    "date_publication": date_pub or f"{year}-01-01",
                    "date_effet": date_pub or f"{year}-01-01",
                    "version": "1.0",
                    "langue": "fr",
                    "auteur": "CSN" if 'csn' in doc_type or doc_type == 'circulaire_csn' else "Profession notariale",
                    "statut": "en_vigueur"
                },
                "classification": {
                    "type_document": doc_type,
                    "label": DOCUMENT_TYPES.get(doc_type, {}).get('label', doc_type),
                    "domaines_juridiques": DOCUMENT_TYPES.get(doc_type, {}).get('domaines', []),
                    "public_cible": ["notaires", "clercs", "collaborateurs d'office"],
                    "annee_reference": year,
                    "categorie_dossier": root_path.name if root_path != SOURCES_DIR else "racine"
                },
                "reference": reference,
                "vocabulaire_specifique": [],  # À enrichir manuellement
                "questions_typiques": generate_questions_typiques(doc_type, reference),
                "relations_documentaires": {
                    "remplace": [],
                    "modifie": [],
                    "reference": [],
                    "complete": []
                },
                "resume": f"Document de type {DOCUMENT_TYPES.get(doc_type, {}).get('label', doc_type)}",
                "mots_cles": extract_keywords(filename, doc_type)
            }

            documents.append(doc_metadata)

    return documents

def save_individual_metadata(documents):
    """Sauvegarde les métadonnées individuelles."""
    DOCS_METADATA_DIR.mkdir(parents=True, exist_ok=True)

    for doc in documents:
        filepath = DOCS_METADATA_DIR / f"{doc['document_id']}.metadata.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

def save_global_index(documents):
    """Sauvegarde l'index global."""
    index = {
        "generated_at": datetime.now().isoformat(),
        "total_documents": len(documents),
        "documents": documents
    }

    with open(METADATA_DIR / "index_complet.json", 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

def save_vocabulary():
    """Sauvegarde le vocabulaire notarial."""
    with open(METADATA_DIR / "vocabulaire_notarial.json", 'w', encoding='utf-8') as f:
        json.dump(VOCABULAIRE_NOTARIAL, f, ensure_ascii=False, indent=2)

def generate_readme(documents):
    """Génère le README.md avec l'index navigable."""

    # Statistiques
    stats = defaultdict(int)
    by_type = defaultdict(list)
    by_year = defaultdict(list)

    for doc in documents:
        doc_type = doc['classification']['type_document']
        year = doc['classification']['annee_reference']
        stats[doc_type] += 1
        by_type[doc_type].append(doc)
        by_year[year].append(doc)

    # Trier les documents par date
    for doc_list in by_type.values():
        doc_list.sort(key=lambda x: x['metadata']['date_publication'], reverse=True)

    readme = []
    readme.append("# Bible Notariale - Index Documentaire")
    readme.append("")
    readme.append("Base documentaire complète pour les professionnels du notariat français.")
    readme.append("")
    readme.append(f"**{len(documents)} documents** | **2019-2025** | Mise à jour : {datetime.now().strftime('%d/%m/%Y')}")
    readme.append("")
    readme.append("---")
    readme.append("")
    readme.append("## Statistiques")
    readme.append("")

    # Ordre d'affichage des types
    type_order = [
        'circulaire_csn', 'avenant_ccn', 'accord_branche', 'fil_info',
        'guide_pratique', 'decret_ordonnance', 'assurance', 'immobilier',
        'formation', 'conformite'
    ]

    for doc_type in type_order:
        if doc_type in stats:
            label = DOCUMENT_TYPES.get(doc_type, {}).get('label', doc_type)
            readme.append(f"- **{label}** : {stats[doc_type]} documents")

    readme.append("")
    readme.append("---")
    readme.append("")
    readme.append("## Navigation par catégorie")
    readme.append("")

    # Sections par type
    for doc_type in type_order:
        if doc_type not in by_type:
            continue

        docs = by_type[doc_type]
        label = DOCUMENT_TYPES.get(doc_type, {}).get('label', doc_type)

        readme.append(f"### {label}")
        readme.append("")
        readme.append("| Date | Référence | Document | Catégorie |")
        readme.append("|------|-----------|----------|-----------|")

        for doc in docs[:50]:  # Limiter à 50 par type pour lisibilité
            date = doc['metadata']['date_publication']
            ref = ""
            if doc['reference']:
                ref = f"{doc['reference']['type']} {doc['reference']['numero']}"
            titre = doc['metadata']['titre'][:60]
            if len(doc['metadata']['titre']) > 60:
                titre += "..."
            lien = f"[{titre}]({doc['fichier']})"
            categorie = doc['classification']['categorie_dossier']

            readme.append(f"| {date} | {ref} | {lien} | {categorie} |")

        if len(docs) > 50:
            readme.append(f"\n*... et {len(docs) - 50} autres documents*\n")

        readme.append("")

    readme.append("---")
    readme.append("")
    readme.append("## Index chronologique")
    readme.append("")

    for year in sorted(by_year.keys(), reverse=True):
        readme.append(f"### {year}")
        readme.append(f"*{len(by_year[year])} documents*")
        readme.append("")

    readme.append("---")
    readme.append("")
    readme.append("## Métadonnées KM")
    readme.append("")
    readme.append("Les métadonnées structurées pour l'outil de Knowledge Management sont disponibles dans :")
    readme.append("")
    readme.append("- `_metadata/index_complet.json` - Index global de tous les documents")
    readme.append("- `_metadata/documents/*.metadata.json` - Métadonnées détaillées par document")
    readme.append("- `_metadata/vocabulaire_notarial.json` - Lexique notarial avec synonymes")
    readme.append("")
    readme.append("---")
    readme.append("")
    readme.append("## Utilisation")
    readme.append("")
    readme.append("- **Navigation** : Cliquez sur les liens pour consulter les documents directement sur GitHub")
    readme.append("- **Recherche** : Utilisez `Ctrl+F` pour rechercher par mot-clé")
    readme.append("- **Téléchargement** : Cliquez sur le document puis sur le bouton de téléchargement")
    readme.append("")
    readme.append("---")
    readme.append("")
    readme.append("*Généré automatiquement par `index_bible_notariale.py`*")
    readme.append("")

    return "\n".join(readme)

def main():
    print("Indexation de la Bible Notariale...")
    print(f"Dossier source : {SOURCES_DIR}")
    print(f"Dossier métadonnées : {METADATA_DIR}")
    print()

    # 1. Scanner les documents
    print("1. Scan des documents...")
    documents = scan_documents()
    print(f"   {len(documents)} documents trouvés")
    print()

    # 2. Sauvegarder les métadonnées individuelles
    print("2. Génération des métadonnées KM individuelles...")
    save_individual_metadata(documents)
    print(f"   {len(documents)} fichiers .metadata.json créés")
    print()

    # 3. Sauvegarder l'index global
    print("3. Génération de l'index global...")
    save_global_index(documents)
    print("   index_complet.json créé")
    print()

    # 4. Sauvegarder le vocabulaire
    print("4. Export du vocabulaire notarial...")
    save_vocabulary()
    print("   vocabulaire_notarial.json créé")
    print()

    # 5. Générer le README
    print("5. Génération du README.md...")
    readme_content = generate_readme(documents)
    with open(BASE_DIR / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("   README.md créé")
    print()

    print("Indexation terminée !")
    print(f"Total : {len(documents)} documents indexés")

if __name__ == "__main__":
    main()
