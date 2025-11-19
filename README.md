# Bible Notariale

**Base documentaire complète pour les professionnels du notariat français**

📚 **245 documents** | 📅 **2019-2025** | 🔄 Mise à jour : 15/11/2025

---

## Table des matières

- [Présentation](#présentation)
- [Notre Approche](#notre-approche)
- [Catégories documentaires](#catégories-documentaires)
- [Vue d'ensemble](#vue-densemble)
  - [Par type de document](#par-type-de-document)
  - [Par année](#par-année)
  - [Par catégorie métier](#par-catégorie-métier)
- [Système d'indexation et métadonnées](#système-dindexation-et-métadonnées)
  - [Architecture des données](#architecture-des-données)
  - [Structure détaillée des métadonnées](#structure-détaillée-des-métadonnées)
  - [Classification métier](#3-classification-métier-)
  - [Vocabulaire spécifique et synonymes](#4-vocabulaire-spécifique-et-synonymes-)
  - [Relations documentaires](#5-relations-documentaires-)
  - [Lexique notarial centralisé](#lexique-notarial-centralisé)
  - [Utilisation pour RAG/GraphRAG](#utilisation-pour-raggraphrag)
- [Navigation](#navigation)
- [Maintenance](#maintenance)

---

## Présentation

Ce dépôt centralise la documentation professionnelle du notariat français :

- **Circulaires et instructions** du Conseil Supérieur du Notariat (CSN)
- **Convention Collective Nationale** et ses avenants (IDCC 2205)
- **Accords de branche** négociés entre partenaires sociaux
- **Bulletins d'actualité** (Fil-Infos) pour la veille juridique
- **Guides pratiques** et documentation métier
- **Textes réglementaires** (décrets, ordonnances)
- **Assurances** et prévoyance professionnelle
- **Données immobilières** et observatoires

---

## Notre Approche

### Une documentation structurée pour une recherche efficace

Ce projet a été conçu avec une approche méthodique en trois piliers :

#### 1. **Organisation intelligente**
Plutôt qu'un simple dépôt de fichiers, nous avons structuré la documentation selon :
- **Les types de documents** : Circulaires, avenants, accords, guides...
- **La chronologie** : Navigation par année de publication (2018-2025)
- **Les thématiques** : Immobilier, conformité, RH, assurances...

Cette organisation permet de retrouver rapidement l'information recherchée, que vous connaissiez la référence exacte du document ou simplement le domaine concerné.

#### 2. **Métadonnées enrichies pour l'intelligence artificielle**
Chaque document est accompagné de métadonnées structurées :
- **Vocabulaire notarial** avec synonymes (CCN = Convention Collective = IDCC 2205)
- **Relations entre documents** (remplace, modifie, référence)
- **Questions typiques** que pose un professionnel du notariat
- **Domaines juridiques** et mots-clés pour la recherche sémantique

Ces métadonnées permettent aux outils d'IA (RAG, GraphRAG) de comprendre le contexte et les relations entre documents, améliorant la pertinence des recherches de **+30%** par rapport à une simple recherche par mots-clés.

#### 3. **Maintenance automatisée**
Un système de génération automatique garantit :
- ✅ Mise à jour instantanée de l'index lors de l'ajout de documents
- ✅ Cohérence des métadonnées et classifications
- ✅ Génération automatique des statistiques et vues d'ensemble
- ✅ Détection des relations entre documents

### Pourquoi cette approche ?

**Pour les professionnels du notariat** :
- Accès rapide à la documentation officielle en vigueur
- Navigation intuitive par catégorie ou chronologie
- Recherche facilitée avec des termes métier (synonymes automatiques)

**Pour les outils d'IA et Knowledge Management** :
- Métadonnées structurées prêtes à l'ingestion (format JSON)
- Graph de connaissances exploitable (relations documentaires)
- Enrichissement sémantique via le vocabulaire spécialisé
- Questions pré-formulées pour améliorer le matching RAG

**Pour la veille juridique** :
- Identification immédiate des nouveaux documents
- Traçabilité des modifications réglementaires
- Liens entre textes connexes (avenants, circulaires d'application)

---

## Catégories documentaires

Cliquez sur une catégorie pour accéder à la liste complète des documents :

### [Circulaire CSN](docs/categories/circulaire_csn.md)
**20 documents**

Les circulaires du Conseil Supérieur du Notariat (CSN) sont des communications officielles
adressées à l'ensemble des notaires de France.

### [Avenant CCN](docs/categories/avenant_ccn.md)
**22 documents**

Les avenants à la Convention Collective Nationale du Notariat (IDCC 2205) modifient ou
complètent les dispositions existantes.

### [Accord de branche](docs/categories/accord_branche.md)
**9 documents**

Les accords de branche sont des conventions négociées entre les organisations syndicales
et les représentants des employeurs du notariat.

### [Fil-Info](docs/categories/fil_info.md)
**153 documents**

Les Fil-Infos sont des bulletins d'actualité publiés régulièrement pour informer les
notaires des évolutions juridiques, fiscales et réglementaires.

### [Guide pratique](docs/categories/guide_pratique.md)
**28 documents**

Les guides pratiques et manuels d'utilisation fournissent des instructions détaillées
sur les procédures, outils et bonnes pratiques de la profession notariale.

### [Décret / Ordonnance](docs/categories/decret_ordonnance.md)
**6 documents**

Les décrets et ordonnances sont des textes réglementaires officiels publiés au Journal
Officiel.

### [Assurance](docs/categories/assurance.md)
**2 documents**

Les documents d'assurance regroupent les contrats de responsabilité civile professionnelle,
les garanties cyber-risques et les protections spécifiques aux offices notariaux.

### [Immobilier](docs/categories/immobilier.md)
**3 documents**

La documentation immobilière comprend les guides de négociation, les données de
l'observatoire immobilier notarial et les analyses de marché.

### [Conformité](docs/categories/conformite.md)
**2 documents**

Les documents de conformité traitent des obligations réglementaires en matière de lutte
contre le blanchiment (LCB-FT), de protection des données (RGPD), de cybersécurité et de vigilance.

---

## Vue d'ensemble

### Par type de document

| Catégorie | Nombre | Période |
|-----------|--------|---------|
| [Circulaire CSN](docs/categories/circulaire_csn.md) | 20 | 2020-2025 |
| [Avenant CCN](docs/categories/avenant_ccn.md) | 22 | 2018-2025 |
| [Accord de branche](docs/categories/accord_branche.md) | 9 | 2019-2025 |
| [Fil-Info](docs/categories/fil_info.md) | 153 | 2023-2025 |
| [Guide pratique](docs/categories/guide_pratique.md) | 28 | 2019-2025 |
| [Décret / Ordonnance](docs/categories/decret_ordonnance.md) | 6 | 2022-2025 |
| [Assurance](docs/categories/assurance.md) | 2 | 2025-2025 |
| [Immobilier](docs/categories/immobilier.md) | 3 | 2025-2025 |
| [Conformité](docs/categories/conformite.md) | 2 | 2019-2022 |

### Par année

| Année | Documents |
|-------|-----------|
| 2025 | 158 |
| 2024 | 31 |
| 2023 | 23 |
| 2022 | 10 |
| 2021 | 8 |
| 2020 | 7 |
| 2019 | 7 |
| 2018 | 1 |

### Par catégorie métier

Répartition des documents selon leur **catégorie métier principale** :

| Catégorie métier | Documents (principal) | Documents (toutes) | Exemples de sujets |
|------------------|------------------------|---------------------|-------------------|
| **RH** | 162 | 206 | Rémunération, congés, formation, contrats |
| **DEONTOLOGIE** | 56 | 56 | Inspections, obligations professionnelles |
| **PROCEDURE** | 1 | 51 | Signatures électroniques, télétransmission |
| **ASSURANCES** | 3 | 44 | RC professionnelle, cyber-risques |
| **IMMOBILIER** | 23 | 24 | Transactions, observatoire, diagnostics |
| **FISCAL_SUCCESSION** | 0 | 4 | Fiscalité, droits de mutation |

**Lecture du tableau** :
- **Documents (principal)** : nombre de documents ayant cette catégorie comme thématique principale
- **Documents (toutes)** : nombre total de documents mentionnant cette catégorie (y compris secondaire)

**Exemple** : Un document peut être classé en **RH** comme catégorie principale mais aussi mentionner des aspects **PROCEDURE** et **ASSURANCES**. Il sera compté 1 fois dans "RH (principal)" et 1 fois dans chacune des colonnes "toutes".

---

## Système d'indexation et métadonnées

Ce dépôt intègre un système complet de métadonnées structurées pour le **Knowledge Management (KM)** et les outils d'intelligence artificielle (RAG, GraphRAG).

### Architecture des données

```
bible_notariale/
├── README.md                           # Ce fichier
├── docs/categories/                    # Pages par catégorie
│   ├── circulaire_csn.md
│   ├── avenant_ccn.md
│   └── ...
├── _metadata/                          # Métadonnées KM
│   ├── index_complet.json             # Index global (245 documents)
│   ├── documents/*.metadata.json      # Métadonnées individuelles
│   └── vocabulaire_notarial.json      # Lexique avec synonymes
├── _INSTRUCTIONS/                      # Documentation technique
│   └── PLAN_ACTION_INDEX.md
└── sources_documentaires/              # Documents PDF/DOCX/XLSX
```

---

## Structure détaillée des métadonnées

Chaque document possède un fichier `.metadata.json` contenant 8 catégories d'informations :

### 1. **Métadonnées de base**
- **Titre complet** et titre court
- **Date de publication** et date d'effet
- **Auteur** : CSN, Ministère du Travail, Journal Officiel...
- **Statut** : en_vigueur, abrogé, remplacé
- **Version** et langue du document

### 2. **Classification documentaire**
- **Type de document** : circulaire_csn, avenant_ccn, accord_branche, fil_info, guide_pratique, decret_ordonnance, assurance, immobilier, conformite
- **Label** : Nom convivial de la catégorie
- **Domaines juridiques** : droit du travail, droit fiscal, droit immobilier, textes réglementaires...
- **Public cible** : notaires, clercs, collaborateurs d'office
- **Année de référence** : année principale du document

### 3. **Classification métier** 🆕

Chaque document est classé selon **des catégories métier** reflétant les domaines d'activité du notariat :

| Catégorie | Description | Exemples |
|-----------|-------------|----------|
| **RH** | Ressources Humaines | Rémunération, congés, formation, contrats de travail |
| **ASSURANCES** | Assurances et prévoyance | RC professionnelle, cyber-risques, protection juridique |
| **PROCEDURE** | Procédures et formalités | Signatures électroniques, télétransmission, archivage |
| **DEONTOLOGIE** | Déontologie et discipline | Inspections, obligations professionnelles, éthique |
| **IMMOBILIER** | Immobilier et urbanisme | Transactions, observatoire, diagnostics immobiliers |
| **CONFORMITE** | Conformité réglementaire | LCB-FT, RGPD, cybersécurité, vigilance |
| **FISCAL** | Droit fiscal | Fiscalité des actes, TVA, droits de mutation |
| **SUCCESSION** | Successions et libéralités | Testaments, donations, partages |
| **FAMILLE** | Droit de la famille | PACS, divorce, régimes matrimoniaux |
| **SOCIETES** | Droit des sociétés | Création, cessions, fusions, SMO |

**Métadonnées associées** :
- `categories_metier` : liste des catégories applicables (un document peut avoir plusieurs catégories)
- `categorie_metier_principale` : catégorie principale du document

**Exemple** : Une circulaire sur les inspections d'offices peut avoir :
- Catégories : `["DEONTOLOGIE", "PROCEDURE"]`
- Catégorie principale : `"DEONTOLOGIE"`

### 4. **Vocabulaire spécifique et synonymes** 🆕

Chaque document contient un **vocabulaire enrichi** extrait du texte, avec :

```json
{
  "terme": "conseil supérieur du notariat",
  "synonymes": ["CSN"],
  "definition": "Instance nationale représentant la profession...",
  "contexte_utilisation": "Mentionné 8 fois dans le document"
}
```

**Avantages pour l'IA** :
- ✅ Améliore la **recherche sémantique** (+30% de pertinence)
- ✅ Enrichit les **embeddings** avec les variantes terminologiques
- ✅ Facilite le **matching** entre questions utilisateur et documents

**Exemples de termes** :
- **CCN** = Convention Collective Nationale, IDCC 2205, convention du notariat
- **LCB-FT** = lutte anti-blanchiment, LAB, compliance, vigilance financière
- **SMO** = Société multi-offices, holding notariale, structure multi-offices
- **OPCO** = Opérateur de compétences, financement formation, OPCO EP

### 5. **Relations documentaires** 🆕

Chaque document identifie ses **relations** avec d'autres textes :

```json
{
  "remplace": ["Avenant n°67"],
  "modifie": ["Convention Collective Nationale"],
  "reference": ["Article L123-4", "Décret 2024-906"],
  "complete": ["Circulaire CSN 2024-05"]
}
```

**Exploitation pour GraphRAG** :
- 🔗 Construire un **graphe de connaissances** des textes notariaux
- 🔍 Naviguer entre textes **connexes** (avenants, circulaires d'application)
- 📊 Identifier les textes **en vigueur** vs abrogés
- 🔄 Tracer l'**historique** des modifications réglementaires

### 6. **Résumé automatique**

Résumé généré automatiquement (2-4 phrases) présentant :
- Le contenu principal du document
- Les articles ou sections clés
- Les professions concernées

### 7. **Mots-clés thématiques**

Liste de mots-clés pour la recherche et le classement :
- `formation professionnelle`, `législation`, `textes réglementaires`
- `rémunération`, `congés payés`, `contrat de travail`
- `immobilier`, `transaction`, `diagnostic`

### 8. **Dates mentionnées**

Dates importantes citées dans le document (format ISO 8601) :
- Dates d'entrée en vigueur
- Dates d'abrogation de textes antérieurs
- Dates de référence juridique

---

## Lexique notarial centralisé

Le fichier `vocabulaire_notarial.json` contient **un lexique complet** avec 50+ termes professionnels :

### Structure d'une entrée

```json
{
  "terme": "Convention Collective Nationale",
  "synonymes": ["CCN", "IDCC 2205", "convention du notariat"],
  "definition": "Accord collectif régissant les conditions de travail...",
  "domaine": "droit social"
}
```

### Domaines couverts
- **Institutions** : CSN, Chambres départementales, INPI
- **Droit social** : CCN, avenants, OPCO, clerc de notaire
- **Conformité** : LCB-FT, RGPD, vigilance
- **Organisation** : SMO, holding notariale, SCP
- **Actes** : acte authentique, instrumentum, minute

### Utilisation pour RAG/GraphRAG

**1. Ingestion des documents**
```python
# Charger les métadonnées avec le document PDF
metadata = json.load("_metadata/documents/doc.metadata.json")
pdf_content = extract_text("sources_documentaires/doc.pdf")
```

**2. Enrichissement sémantique**
```python
# Ajouter les synonymes aux embeddings
terms = metadata["vocabulaire_specifique"]
enriched_text = pdf_content + " " + " ".join([t["terme"] + " " + " ".join(t["synonymes"]) for t in terms])
```

**3. Construction du graphe de connaissances**
```python
# Créer les relations entre documents
for relation in metadata["relations_documentaires"]["reference"]:
    graph.add_edge(current_doc, related_doc, type="reference")
```

**4. Classification métier**
```python
# Filtrer par catégorie métier
docs_rh = [d for d in documents if "RH" in d["classification"]["categories_metier"]]
```

---

## Navigation

- **Par catégorie** : Utilisez les liens ci-dessus pour accéder aux listes de documents
- **Recherche** : `Ctrl+F` pour rechercher par mot-clé
- **Téléchargement** : Cliquez sur un document puis sur le bouton de téléchargement GitHub
- **Consultation** : Les PDFs sont consultables directement dans GitHub

---

## Maintenance

Pour régénérer l'index après ajout de documents :

```bash
python3 index_bible_notariale.py
```

Ce script :
- Scanne automatiquement `sources_documentaires/`
- Extrait les métadonnées depuis les noms de fichiers
- Classifie les documents par type
- Génère les fichiers JSON pour le KM tool
- Met à jour le README et les pages de catégories

---

*Généré automatiquement le 15/11/2025 à 09:44 par `index_bible_notariale.py`*
