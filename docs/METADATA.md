# Documentation des Métadonnées

## Vue d'ensemble

Ce document décrit la structure complète des métadonnées associées à chaque document de la Bible Notariale. Ces métadonnées sont conçues pour optimiser l'indexation, la recherche sémantique et l'utilisation par des outils d'intelligence artificielle (RAG, GraphRAG).

---

## Architecture des fichiers de métadonnées

Chaque document possède un fichier `.metadata.json` dans le répertoire `_metadata/documents/` avec la structure suivante :

### 1. Identification du document

```json
{
  "document_id": "identifiant_unique_du_document",
  "fichier": "sources_documentaires/categorie/nom_fichier.pdf",
  "nom_fichier": "nom_fichier.pdf"
}
```

**Champs :**
- **`document_id`** : Identifiant unique du document (format snake_case, sans accents)
- **`fichier`** : Chemin relatif complet depuis la racine du projet
- **`nom_fichier`** : Nom du fichier source (PDF, DOCX, XLSX)

---

### 2. Métadonnées administratives

```json
{
  "metadata": {
    "titre": "Titre complet du document",
    "titre_court": "Titre abrégé (50 caractères max)",
    "date_publication": "YYYY-MM-DD",
    "date_effet": "YYYY-MM-DD",
    "version": "1.0",
    "langue": "fr",
    "auteur": "Organisme émetteur",
    "statut": "en_vigueur"
  }
}
```

**Champs :**
- **`titre`** : Titre complet extrait du document ou du nom de fichier
- **`titre_court`** : Version courte pour affichage (limité à 50 caractères)
- **`date_publication`** : Date de publication officielle (format ISO 8601)
- **`date_effet`** : Date d'entrée en vigueur du document
- **`version`** : Numéro de version du document (si applicable)
- **`langue`** : Code ISO 639-1 (généralement "fr")
- **`auteur`** : Organisme émetteur (CSN, Chambre des Notaires, etc.)
- **`statut`** : État du document
  - `en_vigueur` : Document actuellement applicable
  - `remplace` : Document remplacé par une version plus récente
  - `archive` : Document archivé

---

### 3. Classification documentaire

```json
{
  "classification": {
    "type_document": "circulaire_csn",
    "label": "Circulaire CSN",
    "domaines_juridiques": [
      "droit social",
      "immobilier"
    ],
    "public_cible": [
      "notaires",
      "clercs",
      "comptables offices"
    ],
    "annee_reference": 2025,
    "categorie_dossier": "CSN2025"
  }
}
```

**Champs :**
- **`type_document`** : Type normalisé (snake_case) parmi :
  - `circulaire_csn` : Instructions officielles du CSN
  - `avenant_ccn` : Modifications de la Convention Collective
  - `accord_branche` : Accords négociés entre partenaires sociaux
  - `fil_info` : Bulletins d'actualité
  - `guide_pratique` : Guides et manuels
  - `decret_ordonnance` : Textes réglementaires officiels
  - `assurance` : Contrats et garanties professionnelles
  - `immobilier` : Observatoires et guides immobiliers
  - `conformite` : LCB-FT, RGPD, cyber-sécurité

- **`label`** : Nom lisible du type de document (avec majuscules et accents)

- **`domaines_juridiques`** : Liste des domaines concernés
  - droit social
  - droit immobilier
  - droit des sociétés
  - droit de la famille
  - droit fiscal
  - conformité réglementaire
  - actualité juridique
  - veille professionnelle

- **`public_cible`** : Destinataires du document
  - notaires
  - clercs
  - collaborateurs d'office
  - comptables offices
  - direction d'office

- **`annee_reference`** : Année de publication ou de référence
- **`categorie_dossier`** : Nom du dossier source dans `sources_documentaires/`

---

### 4. Référence documentaire

```json
{
  "reference": {
    "type": "circulaire",
    "numero": "01-25",
    "année": "2025"
  }
}
```

**Champs :**
- **`type`** : Type de référence (circulaire, avenant, accord, fil_info)
- **`numero`** : Numéro de référence officiel
- **`année`** : Année de référence (si différente de l'année de publication)

---

### 5. Vocabulaire spécifique

```json
{
  "vocabulaire_specifique": [
    {
      "terme": "Convention Collective Nationale",
      "synonymes": [
        "CCN",
        "IDCC 2205",
        "convention du notariat"
      ],
      "definition": "Accord collectif régissant les conditions de travail et d'emploi dans le notariat",
      "contexte_utilisation": "Mentionné 5 fois dans le document"
    }
  ]
}
```

**Objectif :** Enrichir les embeddings pour améliorer la recherche sémantique (+30% de pertinence)

**Champs :**
- **`terme`** : Terme technique ou juridique principal
- **`synonymes`** : Liste des variantes, abréviations, formulations alternatives
- **`definition`** : Explication claire et concise du terme
- **`contexte_utilisation`** : Fréquence et contexte d'apparition dans le document

---

### 6. Questions typiques

```json
{
  "questions_typiques": [
    "Quelles sont les nouvelles obligations introduites ?",
    "À partir de quelle date cette circulaire s'applique-t-elle ?",
    "Quels articles de la CCN sont modifiés ?"
  ]
}
```

**Objectif :** Améliorer le matching RAG en anticipant les questions des utilisateurs

**Contenu :**
- Questions fréquemment posées par les professionnels du notariat
- Questions contextuelles spécifiques au type de document
- Questions pratiques d'application

---

### 7. Relations documentaires

```json
{
  "relations_documentaires": {
    "remplace": [
      "sources_documentaires/CSN2024/ancien_document.pdf"
    ],
    "modifie": [
      "sources_documentaires/Convention Collective/ccn_article_12.pdf"
    ],
    "reference": [
      "Code civil",
      "Convention Collective Nationale"
    ],
    "complete": [
      "sources_documentaires/CSN2025/document_complementaire.pdf"
    ]
  }
}
```

**Objectif :** Construire un graphe de connaissances (GraphRAG)

**Types de relations :**
- **`remplace`** : Documents rendus obsolètes par ce document
- **`modifie`** : Documents ou articles modifiés par ce document
- **`reference`** : Textes de loi, réglementations ou documents cités
- **`complete`** : Documents complémentaires ou connexes

---

### 8. Résumé et mots-clés

```json
{
  "resume": "Résumé en 2-3 phrases du contenu principal et de l'objectif du document.",
  "mots_cles": [
    "rémunération",
    "convention collective",
    "salaires",
    "grille salariale"
  ]
}
```

**Champs :**
- **`resume`** : Synthèse concise du document (2-3 phrases max)
- **`mots_cles`** : Liste de termes principaux pour l'indexation et la recherche

---

### 9. Dates mentionnées

```json
{
  "dates_mentionnees": [
    "2025-01-01",
    "2025-06-30",
    "2025-12-31"
  ]
}
```

**Contenu :** Dates importantes extraites du document (échéances, entrées en vigueur, dates limites)

---

## Fichiers complémentaires

### Index complet (`_metadata/index_complet.json`)

Fichier global contenant tous les documents avec leurs métadonnées complètes.

```json
{
  "generated_at": "2025-11-15T09:44:50.817053",
  "total_documents": 245,
  "documents": [
    { /* métadonnées complètes du document 1 */ },
    { /* métadonnées complètes du document 2 */ }
  ]
}
```

---

### Vocabulaire notarial (`_metadata/vocabulaire_notarial.json`)

Lexique global des termes professionnels avec synonymes, utilisé pour enrichir les recherches.

```json
[
  {
    "terme": "Convention Collective Nationale",
    "synonymes": ["CCN", "IDCC 2205", "convention du notariat"],
    "definition": "Accord collectif régissant les conditions de travail",
    "domaine": "droit social"
  }
]
```

**Contenu actuel :** 15 termes principaux couvrant :
- Institutions (CSN, CCN)
- Actes juridiques (acte authentique, minute)
- Organisation (office, SMO)
- Conformité (LCB-FT)
- Formation (OPCO)
- Tarification (ACS, BE, TPF)

---

### Rapport de validation (`_metadata/validation_report.json`)

Rapport de contrôle qualité des métadonnées.

```json
{
  "validation_date": "2025-11-15T09:45:00",
  "total_documents": 245,
  "errors": [],
  "warnings": []
}
```

---

## Utilisation pour RAG / GraphRAG

### 1. Ingestion des métadonnées

```python
import json

# Charger l'index global
with open('_metadata/index_complet.json', 'r', encoding='utf-8') as f:
    index = json.load(f)

# Charger le vocabulaire
with open('_metadata/vocabulaire_notarial.json', 'r', encoding='utf-8') as f:
    vocabulaire = json.load(f)
```

### 2. Enrichissement des embeddings

Utiliser les champs `vocabulaire_specifique` et le vocabulaire global pour :
- Ajouter les synonymes aux textes avant génération des embeddings
- Améliorer la couverture sémantique (+30% de pertinence)
- Gérer les abréviations professionnelles (CCN, CSN, LCB-FT, etc.)

### 3. Matching des questions

Exploiter `questions_typiques` pour :
- Pré-entraîner le modèle sur les questions fréquentes
- Améliorer le matching sémantique entre question utilisateur et document
- Identifier les documents pertinents plus rapidement

### 4. Construction du graphe

Utiliser `relations_documentaires` pour :
- Créer des liens entre nœuds (documents)
- Tracer l'historique des modifications (remplace, modifie)
- Suggérer des documents connexes (complete, reference)

### 5. Filtrage et recherche

Exploiter `classification`, `domaines_juridiques` et `mots_cles` pour :
- Filtrer par type de document
- Rechercher par domaine juridique
- Cibler le public pertinent

---

## Maintenance et mise à jour

### Régénération automatique

Le script `index_bible_notariale.py` automatise :
- Scan des fichiers dans `sources_documentaires/`
- Extraction des métadonnées depuis les noms de fichiers
- Classification automatique par type et domaine
- Génération des fichiers JSON
- Mise à jour du README et des vues

### Commande

```bash
python3 index_bible_notariale.py
```

### Enrichissement manuel

Pour les documents prioritaires, enrichir manuellement :
- `vocabulaire_specifique` : Ajouter les termes techniques spécifiques
- `questions_typiques` : Contextualiser les questions
- `resume` : Rédiger un résumé précis après lecture
- `relations_documentaires` : Identifier les liens entre documents

---

## Standards et bonnes pratiques

### Encodage
- UTF-8 pour gérer les caractères français (accents, cédilles, œ)

### Format des dates
- ISO 8601 : `YYYY-MM-DD`
- Toujours en format UTC pour cohérence

### IDs documents
- Format : `snake_case`
- Sans accents ni caractères spéciaux
- Unique et stable dans le temps

### Chemins de fichiers
- Relatifs depuis la racine du repo
- Portables (Linux/macOS/Windows)
- Utiliser `/` comme séparateur

### Langue
- Métadonnées en français
- Code langue ISO 639-1 : `"fr"`

---

## Questions fréquentes

### Comment ajouter un nouveau document ?

1. Placer le fichier PDF/DOCX dans `sources_documentaires/categorie/`
2. Exécuter `python3 index_bible_notariale.py`
3. Les métadonnées de base seront générées automatiquement
4. Enrichir manuellement si nécessaire

### Comment modifier les métadonnées d'un document ?

1. Éditer le fichier `_metadata/documents/{document_id}.metadata.json`
2. Vérifier la cohérence avec `python3 validate_metadata.py`
3. Régénérer l'index global avec `python3 index_bible_notariale.py`

### Quels champs sont obligatoires ?

**Obligatoires :**
- `document_id`, `fichier`, `nom_fichier`
- `metadata.titre`, `metadata.date_publication`
- `classification.type_document`, `classification.annee_reference`

**Recommandés :**
- `vocabulaire_specifique` (au moins 3 termes)
- `questions_typiques` (au moins 3 questions)
- `resume`, `mots_cles`

**Optionnels :**
- `relations_documentaires` (si pas de lien identifié)
- `dates_mentionnees` (si pas d'échéance particulière)

---

*Dernière mise à jour : 2025-11-19*
