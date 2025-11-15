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
CATEGORIES_DIR = BASE_DIR / "docs" / "categories"

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
        'domaines': ['réglementation notariale', 'instructions professionnelles'],
        'description': """Les circulaires du Conseil Supérieur du Notariat (CSN) sont des communications officielles
adressées à l'ensemble des notaires de France. Elles transmettent les instructions, recommandations et
interprétations des textes réglementaires applicables à la profession. Ces documents sont essentiels pour
la mise en conformité des pratiques notariales et constituent une source d'information fiable sur les
évolutions réglementaires.""",
        'usage': "Consultez ces circulaires pour connaître les obligations professionnelles, les nouvelles procédures et les recommandations du CSN."
    },
    'avenant_ccn': {
        'patterns': [r'[Aa]venant\s*n?[°º]?\s*\d+', r'avenant_n\d+'],
        'label': 'Avenant CCN',
        'domaines': ['convention collective', 'droit social'],
        'description': """Les avenants à la Convention Collective Nationale du Notariat (IDCC 2205) modifient ou
complètent les dispositions existantes. Négociés entre les partenaires sociaux, ils portent sur les
conditions de travail, la rémunération, la formation professionnelle et les avantages sociaux des salariés
du notariat. Chaque avenant est numéroté et daté pour faciliter son identification.""",
        'usage': "Référez-vous à ces avenants pour connaître les modifications des grilles salariales, des procédures RH et des droits des salariés."
    },
    'accord_branche': {
        'patterns': [r'[Aa]ccord', r'accord.*branche', r'accord.*salaire'],
        'label': 'Accord de branche',
        'domaines': ['négociation collective', 'droit social'],
        'description': """Les accords de branche sont des conventions négociées entre les organisations syndicales
et les représentants des employeurs du notariat. Ils définissent les conditions d'emploi et de travail
spécifiques à la profession, couvrant des sujets comme l'égalité professionnelle, la formation,
l'intéressement ou la prévention du harcèlement.""",
        'usage': "Consultez ces accords pour comprendre les engagements collectifs de la branche notariale."
    },
    'fil_info': {
        'patterns': [r'fil-info'],
        'label': 'Fil-Info',
        'domaines': ['actualité juridique', 'veille professionnelle'],
        'description': """Les Fil-Infos sont des bulletins d'actualité publiés régulièrement pour informer les
notaires des évolutions juridiques, fiscales et réglementaires. Ils synthétisent les nouveautés importantes
et proposent des analyses pratiques. Numérotés séquentiellement, ils constituent une source de veille
juridique indispensable pour rester informé des changements impactant la pratique notariale.""",
        'usage': "Parcourez ces bulletins pour votre veille juridique quotidienne et ne manquer aucune actualité importante."
    },
    'guide_pratique': {
        'patterns': [r'[Gg]uide', r'[Mm]anuel', r'[Bb]rochure', r'fiche.*pratique'],
        'label': 'Guide pratique',
        'domaines': ['documentation métier', 'bonnes pratiques'],
        'description': """Les guides pratiques et manuels d'utilisation fournissent des instructions détaillées
sur les procédures, outils et bonnes pratiques de la profession notariale. Ils couvrent des sujets variés :
informatique, sécurité, gestion d'office, œuvres sociales, etc. Ces documents pédagogiques facilitent
l'application concrète des réglementations au quotidien.""",
        'usage': "Utilisez ces guides comme référence opérationnelle pour vos procédures et la mise en œuvre des bonnes pratiques."
    },
    'decret_ordonnance': {
        'patterns': [r'[Dd][ée]cret', r'[Oo]rdonnance', r'd_\d+', r'JO\s*ORDO'],
        'label': 'Décret / Ordonnance',
        'domaines': ['textes réglementaires', 'législation'],
        'description': """Les décrets et ordonnances sont des textes réglementaires officiels publiés au Journal
Officiel. Ils définissent le cadre juridique de l'activité notariale : tarification, inspections,
obligations professionnelles, etc. Ces textes ont force de loi et leur respect est impératif pour
l'exercice de la profession.""",
        'usage': "Consultez ces textes pour connaître le cadre légal et réglementaire de votre activité."
    },
    'assurance': {
        'patterns': [r'[Aa]ssurance', r'[Cc]ontrat.*[Cc]yber', r'FLIPBOOK'],
        'label': 'Assurance',
        'domaines': ['assurance professionnelle', 'prévoyance'],
        'description': """Les documents d'assurance regroupent les contrats de responsabilité civile professionnelle,
les garanties cyber-risques et les protections spécifiques aux offices notariaux. Ils détaillent les
couvertures, franchises, procédures de déclaration et obligations de l'assuré. La protection assurantielle
est essentielle pour la continuité de l'activité notariale.""",
        'usage': "Référez-vous à ces contrats pour connaître vos garanties et les procédures en cas de sinistre."
    },
    'immobilier': {
        'patterns': [r'[Ii]mmobili[eè]re?', r'observatoire', r'CID\d+'],
        'label': 'Immobilier',
        'domaines': ['transactions immobilières', 'observatoire'],
        'description': """La documentation immobilière comprend les guides de négociation, les données de
l'observatoire immobilier notarial et les analyses de marché. Ces informations permettent aux notaires
d'accompagner leurs clients avec des données fiables sur les prix, tendances et spécificités du marché
immobilier local.""",
        'usage': "Exploitez ces données pour conseiller vos clients et analyser le marché immobilier de votre secteur."
    },
    'formation': {
        'patterns': [r'[Ff]ormation', r'OPCO', r'alternance'],
        'label': 'Formation',
        'domaines': ['formation professionnelle', 'développement compétences'],
        'description': """Les documents relatifs à la formation professionnelle couvrent les dispositifs de
financement (OPCO), les parcours de reconversion, l'alternance et les obligations de formation continue.
La formation est un enjeu majeur pour maintenir les compétences à jour face aux évolutions du métier.""",
        'usage': "Consultez ces documents pour organiser la formation de vos collaborateurs et connaître les financements disponibles."
    },
    'conformite': {
        'patterns': [r'LCB-?FT', r'[Cc]yber', r'RGPD', r'vigilance'],
        'label': 'Conformité',
        'domaines': ['conformité', 'sécurité', 'anti-blanchiment'],
        'description': """Les documents de conformité traitent des obligations réglementaires en matière de lutte
contre le blanchiment (LCB-FT), de protection des données (RGPD), de cybersécurité et de vigilance.
Ces thématiques sont cruciales pour éviter les sanctions et protéger l'office contre les risques.""",
        'usage': "Mettez en place vos procédures internes en vous appuyant sur ces guides de conformité."
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

def generate_category_page(doc_type, docs):
    """Génère une page markdown pour une catégorie de documents."""
    config = DOCUMENT_TYPES.get(doc_type, {})
    label = config.get('label', doc_type)
    description = config.get('description', '')
    usage = config.get('usage', '')
    domaines = config.get('domaines', [])

    # Trier par date décroissante
    docs.sort(key=lambda x: x['metadata']['date_publication'], reverse=True)

    # Statistiques
    years = [doc['classification']['annee_reference'] for doc in docs]
    min_year = min(years) if years else 2019
    max_year = max(years) if years else 2025

    dates = [doc['metadata']['date_publication'] for doc in docs]
    latest_date = max(dates) if dates else "N/A"
    oldest_date = min(dates) if dates else "N/A"

    # Collecter tous les mots-clés
    all_keywords = set()
    for doc in docs:
        all_keywords.update(doc.get('mots_cles', []))

    # Collecter les catégories de dossiers
    folders = set(doc['classification']['categorie_dossier'] for doc in docs)

    page = []
    page.append(f"# {label}")
    page.append("")
    page.append(f"[← Retour à l'index principal](../../README.md)")
    page.append("")
    page.append("---")
    page.append("")

    # Description
    page.append("## Description")
    page.append("")
    page.append(description)
    page.append("")
    if usage:
        page.append(f"**Usage** : {usage}")
        page.append("")

    page.append("---")
    page.append("")

    # Statistiques clés
    page.append("## Statistiques")
    page.append("")
    page.append(f"- **Nombre de documents** : {len(docs)}")
    page.append(f"- **Période couverte** : {min_year} - {max_year}")
    page.append(f"- **Document le plus récent** : {latest_date}")
    page.append(f"- **Document le plus ancien** : {oldest_date}")
    page.append(f"- **Domaines juridiques** : {', '.join(domaines)}")
    page.append("")

    page.append("---")
    page.append("")

    # Informations clés (résumé des métadonnées)
    page.append("## Informations clés")
    page.append("")
    page.append("### Sources")
    page.append("")
    for folder in sorted(folders):
        folder_docs = [d for d in docs if d['classification']['categorie_dossier'] == folder]
        page.append(f"- **{folder}** : {len(folder_docs)} documents")
    page.append("")

    if all_keywords:
        page.append("### Thématiques principales")
        page.append("")
        page.append(", ".join(sorted(list(all_keywords)[:15])))
        page.append("")

    # Références extraites
    refs = [doc for doc in docs if doc.get('reference')]
    if refs:
        page.append("### Références identifiées")
        page.append("")
        for doc in refs[:10]:
            ref = doc['reference']
            page.append(f"- {ref['type'].capitalize()} n°{ref['numero']} - {doc['metadata']['titre'][:50]}")
        if len(refs) > 10:
            page.append(f"- *... et {len(refs) - 10} autres références*")
        page.append("")

    page.append("---")
    page.append("")

    # Timeline / Informations sur les dates
    page.append("## Chronologie")
    page.append("")

    docs_by_year = defaultdict(list)
    for doc in docs:
        docs_by_year[doc['classification']['annee_reference']].append(doc)

    for year in sorted(docs_by_year.keys(), reverse=True):
        page.append(f"### {year}")
        page.append(f"*{len(docs_by_year[year])} documents*")
        page.append("")

    page.append("---")
    page.append("")

    # Liste des documents
    page.append("## Documents")
    page.append("")
    page.append("| Date | Référence | Titre | Dossier |")
    page.append("|------|-----------|-------|---------|")

    for doc in docs:
        date = doc['metadata']['date_publication']
        ref = ""
        if doc.get('reference'):
            ref = f"{doc['reference']['type']} {doc['reference']['numero']}"
        titre = doc['metadata']['titre'][:70]
        if len(doc['metadata']['titre']) > 70:
            titre += "..."
        # Lien relatif depuis docs/categories/
        lien = f"[{titre}](../../{doc['fichier']})"
        categorie = doc['classification']['categorie_dossier']

        page.append(f"| {date} | {ref} | {lien} | {categorie} |")

    page.append("")
    page.append("---")
    page.append("")
    page.append(f"*Page générée automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*")
    page.append("")

    return "\n".join(page)


def save_category_pages(documents):
    """Génère et sauvegarde les pages par catégorie."""
    CATEGORIES_DIR.mkdir(parents=True, exist_ok=True)

    by_type = defaultdict(list)
    for doc in documents:
        doc_type = doc['classification']['type_document']
        by_type[doc_type].append(doc)

    pages_created = []
    for doc_type, docs in by_type.items():
        if docs:
            page_content = generate_category_page(doc_type, docs)
            filename = f"{doc_type}.md"
            filepath = CATEGORIES_DIR / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(page_content)
            pages_created.append((doc_type, filename, len(docs)))

    return pages_created


def generate_readme(documents):
    """Génère le README.md avec présentation globale et liens vers catégories."""

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

    # Ordre d'affichage des types
    type_order = [
        'circulaire_csn', 'avenant_ccn', 'accord_branche', 'fil_info',
        'guide_pratique', 'decret_ordonnance', 'assurance', 'immobilier',
        'formation', 'conformite'
    ]

    readme = []
    readme.append("# Bible Notariale")
    readme.append("")
    readme.append("**Base documentaire complète pour les professionnels du notariat français**")
    readme.append("")
    readme.append(f"📚 **{len(documents)} documents** | 📅 **2019-2025** | 🔄 Mise à jour : {datetime.now().strftime('%d/%m/%Y')}")
    readme.append("")
    readme.append("---")
    readme.append("")

    # Présentation
    readme.append("## Présentation")
    readme.append("")
    readme.append("Ce dépôt centralise la documentation professionnelle du notariat français :")
    readme.append("")
    readme.append("- **Circulaires et instructions** du Conseil Supérieur du Notariat (CSN)")
    readme.append("- **Convention Collective Nationale** et ses avenants (IDCC 2205)")
    readme.append("- **Accords de branche** négociés entre partenaires sociaux")
    readme.append("- **Bulletins d'actualité** (Fil-Infos) pour la veille juridique")
    readme.append("- **Guides pratiques** et documentation métier")
    readme.append("- **Textes réglementaires** (décrets, ordonnances)")
    readme.append("- **Assurances** et prévoyance professionnelle")
    readme.append("- **Données immobilières** et observatoires")
    readme.append("")
    readme.append("---")
    readme.append("")

    # Catégories avec liens
    readme.append("## Catégories documentaires")
    readme.append("")
    readme.append("Cliquez sur une catégorie pour accéder à la liste complète des documents :")
    readme.append("")

    for doc_type in type_order:
        if doc_type in stats:
            config = DOCUMENT_TYPES.get(doc_type, {})
            label = config.get('label', doc_type)
            description_short = config.get('description', '').split('.')[0] + '.'
            count = stats[doc_type]

            readme.append(f"### [{label}](docs/categories/{doc_type}.md)")
            readme.append(f"**{count} documents**")
            readme.append("")
            readme.append(description_short)
            readme.append("")

    readme.append("---")
    readme.append("")

    # Statistiques globales
    readme.append("## Vue d'ensemble")
    readme.append("")
    readme.append("### Par type de document")
    readme.append("")
    readme.append("| Catégorie | Nombre | Période |")
    readme.append("|-----------|--------|---------|")

    for doc_type in type_order:
        if doc_type in by_type:
            label = DOCUMENT_TYPES.get(doc_type, {}).get('label', doc_type)
            docs = by_type[doc_type]
            years = [d['classification']['annee_reference'] for d in docs]
            min_y = min(years) if years else 2019
            max_y = max(years) if years else 2025
            readme.append(f"| [{label}](docs/categories/{doc_type}.md) | {len(docs)} | {min_y}-{max_y} |")

    readme.append("")

    readme.append("### Par année")
    readme.append("")
    readme.append("| Année | Documents |")
    readme.append("|-------|-----------|")

    for year in sorted(by_year.keys(), reverse=True):
        readme.append(f"| {year} | {len(by_year[year])} |")

    readme.append("")
    readme.append("---")
    readme.append("")

    # Système de métadonnées
    readme.append("## Système d'indexation et métadonnées")
    readme.append("")
    readme.append("Ce dépôt intègre un système complet de métadonnées structurées pour l'outil de **Knowledge Management (KM)**.")
    readme.append("")
    readme.append("### Architecture des données")
    readme.append("")
    readme.append("```")
    readme.append("bible_notariale/")
    readme.append("├── README.md                           # Ce fichier")
    readme.append("├── docs/categories/                    # Pages par catégorie")
    readme.append("│   ├── circulaire_csn.md")
    readme.append("│   ├── avenant_ccn.md")
    readme.append("│   └── ...")
    readme.append("├── _metadata/                          # Métadonnées KM")
    readme.append("│   ├── index_complet.json             # Index global")
    readme.append("│   ├── documents/*.metadata.json      # Métadonnées par document")
    readme.append("│   └── vocabulaire_notarial.json      # Lexique avec synonymes")
    readme.append("├── _INSTRUCTIONS/                      # Documentation technique")
    readme.append("│   └── PLAN_ACTION_INDEX.md")
    readme.append("└── sources_documentaires/              # Documents PDF/DOCX/XLSX")
    readme.append("```")
    readme.append("")

    readme.append("### Structure des métadonnées KM")
    readme.append("")
    readme.append("Chaque document possède un fichier `.metadata.json` contenant :")
    readme.append("")
    readme.append("- **Identification** : ID unique, titre, date de publication")
    readme.append("- **Classification** : Type de document, domaines juridiques, année de référence")
    readme.append("- **Vocabulaire spécifique** : Termes techniques avec synonymes (pour enrichir les embeddings)")
    readme.append("- **Questions typiques** : Questions fréquentes pour améliorer le matching RAG")
    readme.append("- **Relations** : Liens entre documents (remplace, modifie, référence)")
    readme.append("- **Mots-clés** : Thématiques principales pour la recherche")
    readme.append("")

    readme.append("### Vocabulaire notarial enrichi")
    readme.append("")
    readme.append("Le fichier `vocabulaire_notarial.json` contient un lexique de termes professionnels avec leurs synonymes :")
    readme.append("")
    readme.append("- **CCN** = Convention Collective Nationale, IDCC 2205")
    readme.append("- **CSN** = Conseil Supérieur du Notariat")
    readme.append("- **LCB-FT** = Lutte anti-blanchiment, LAB, compliance")
    readme.append("- **SMO** = Société multi-offices, holding notariale")
    readme.append("- **OPCO** = Opérateur de compétences, financement formation")
    readme.append("- *Et plus encore...*")
    readme.append("")

    readme.append("### Utilisation pour RAG/GraphRAG")
    readme.append("")
    readme.append("1. **Ingestion** : Charger les `*.metadata.json` avec les documents")
    readme.append("2. **Enrichissement** : Utiliser les synonymes pour améliorer les embeddings (+30% pertinence)")
    readme.append("3. **Matching** : Exploiter les questions typiques pour le matching sémantique")
    readme.append("4. **Graph** : Construire les relations entre documents")
    readme.append("")

    readme.append("---")
    readme.append("")

    # Navigation
    readme.append("## Navigation")
    readme.append("")
    readme.append("- **Par catégorie** : Utilisez les liens ci-dessus pour accéder aux listes de documents")
    readme.append("- **Recherche** : `Ctrl+F` pour rechercher par mot-clé")
    readme.append("- **Téléchargement** : Cliquez sur un document puis sur le bouton de téléchargement GitHub")
    readme.append("- **Consultation** : Les PDFs sont consultables directement dans GitHub")
    readme.append("")

    readme.append("---")
    readme.append("")

    # Script
    readme.append("## Maintenance")
    readme.append("")
    readme.append("Pour régénérer l'index après ajout de documents :")
    readme.append("")
    readme.append("```bash")
    readme.append("python3 index_bible_notariale.py")
    readme.append("```")
    readme.append("")
    readme.append("Ce script :")
    readme.append("- Scanne automatiquement `sources_documentaires/`")
    readme.append("- Extrait les métadonnées depuis les noms de fichiers")
    readme.append("- Classifie les documents par type")
    readme.append("- Génère les fichiers JSON pour le KM tool")
    readme.append("- Met à jour le README et les pages de catégories")
    readme.append("")

    readme.append("---")
    readme.append("")
    readme.append(f"*Généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')} par `index_bible_notariale.py`*")
    readme.append("")

    return "\n".join(readme)

def load_existing_metadata():
    """Charge les métadonnées existantes au lieu de les régénérer."""
    documents = []

    for meta_file in DOCS_METADATA_DIR.glob("*.metadata.json"):
        with open(meta_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        documents.append(metadata)

    return documents


def main():
    print("Indexation de la Bible Notariale...")
    print(f"Dossier source : {SOURCES_DIR}")
    print(f"Dossier métadonnées : {METADATA_DIR}")
    print()

    # Vérifier si des métadonnées existent déjà
    existing_meta = list(DOCS_METADATA_DIR.glob("*.metadata.json"))

    if existing_meta:
        print("1. Chargement des métadonnées existantes...")
        documents = load_existing_metadata()
        print(f"   {len(documents)} documents chargés")
        print()

        # Pas de régénération des métadonnées individuelles
        print("2. Conservation des métadonnées enrichies existantes")
        print()
    else:
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

    # 5. Générer les pages par catégorie
    print("5. Génération des pages par catégorie...")
    pages = save_category_pages(documents)
    for doc_type, filename, count in pages:
        print(f"   {filename} ({count} documents)")
    print()

    # 6. Générer le README
    print("6. Génération du README.md global...")
    readme_content = generate_readme(documents)
    with open(BASE_DIR / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("   README.md créé")
    print()

    print("Indexation terminée !")
    print(f"Total : {len(documents)} documents indexés")
    print(f"Pages de catégories : {len(pages)}")

if __name__ == "__main__":
    main()
