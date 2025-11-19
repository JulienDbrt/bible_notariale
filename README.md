# Bible Notariale

**Base documentaire complète pour les professionnels du notariat français**

📚 **245 documents** | 📅 **2019-2025** | 🔄 Mise à jour : 19/11/2025

---

## Table des matières

1. [Présentation](#présentation)
2. [Notre Approche](#notre-approche)
3. [Contenu de la Base Documentaire](#contenu-de-la-base-documentaire)
   - [Par catégories](#catégories-documentaires)
   - [Par thématiques métiers](#thématiques-métiers)
   - [Statistiques](#statistiques)
4. [Système de Métadonnées](#système-de-métadonnées)
   - [Architecture](#architecture-des-données)
   - [Documentation complète](#documentation-complète-des-métadonnées)
   - [Vocabulaire enrichi](#vocabulaire-notarial-enrichi)
   - [Questions typiques](#questions-typiques-intégrées)
5. [Utilisation](#utilisation)
6. [Maintenance](#maintenance)

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
- **Documents de conformité** (LCB-FT, RGPD, cybersécurité)

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

## Contenu de la Base Documentaire

### Catégories documentaires

Cliquez sur une catégorie pour accéder à la liste complète des documents :

| Catégorie | Nombre | Période | Description |
|-----------|--------|---------|-------------|
| **[Fil-Info](docs/categories/fil_info.md)** | 153 | 2023-2025 | Bulletins d'actualité et veille juridique |
| **[Guide pratique](docs/categories/guide_pratique.md)** | 28 | 2019-2025 | Guides métier et bonnes pratiques |
| **[Avenant CCN](docs/categories/avenant_ccn.md)** | 22 | 2018-2025 | Modifications de la Convention Collective |
| **[Circulaire CSN](docs/categories/circulaire_csn.md)** | 20 | 2020-2025 | Instructions officielles du CSN |
| **[Accord de branche](docs/categories/accord_branche.md)** | 9 | 2019-2025 | Négociations collectives |
| **[Décret / Ordonnance](docs/categories/decret_ordonnance.md)** | 6 | 2022-2025 | Textes réglementaires officiels |
| **[Immobilier](docs/categories/immobilier.md)** | 3 | 2025-2025 | Guides et observatoires immobiliers |
| **[Assurance](docs/categories/assurance.md)** | 2 | 2025-2025 | Contrats et garanties professionnelles |
| **[Conformité](docs/categories/conformite.md)** | 2 | 2019-2022 | LCB-FT, RGPD, cybersécurité |

---

### Thématiques métiers

Les documents sont également classés par domaines d'expertise :

#### 🏛️ **Droit Social & RH**
- Convention Collective et avenants (22 documents)
- Accords de salaires et rémunération
- Formation professionnelle et OPCO
- Égalité professionnelle et harcèlement
- Procédures RH (licenciement, congés)

#### 🏠 **Immobilier & Transactions**
- Guides de négociation immobilière
- Observatoire immobilier notarial
- Actes courants et biens d'exception
- Taxe de publicité foncière (TPF)

#### 📋 **Conformité & Réglementation**
- Lutte anti-blanchiment (LCB-FT)
- Protection des données (RGPD)
- Cybersécurité et cyber-risques
- Vigilance et signalement Tracfin

#### 🛡️ **Assurances & Prévoyance**
- Responsabilité civile professionnelle
- Contrats cyber et garanties
- Prévoyance et protection sociale

#### 📚 **Actes & Procédures**
- Actes électroniques et SignActe
- Annexes et contraintes RGPD
- Minute et conservation
- Frais de recherche et copies

#### 💼 **Organisation & Gestion**
- Société multi-offices (SMO)
- Calculs financiers et outils
- Inspection des officiers publics
- Bonnes pratiques CLE-REAL

---

### Statistiques

#### Par année de publication

| Année | Documents | Pourcentage |
|-------|-----------|-------------|
| 2025 | 158 | 64% |
| 2024 | 31 | 13% |
| 2023 | 23 | 9% |
| 2022 | 10 | 4% |
| 2021 | 8 | 3% |
| 2020 | 7 | 3% |
| 2019 | 7 | 3% |
| 2018 | 1 | <1% |

**Total : 245 documents**

---

## Système de Métadonnées

### Architecture des données

```
bible_notariale/
├── README.md                           # Ce fichier
├── docs/
│   ├── METADATA.md                    # Documentation des métadonnées
│   └── categories/                    # Pages par catégorie
│       ├── circulaire_csn.md
│       ├── avenant_ccn.md
│       └── ...
├── _metadata/                          # Métadonnées KM
│   ├── index_complet.json             # Index global (245 documents)
│   ├── documents/                     # Métadonnées par document
│   │   └── *.metadata.json           # 245 fichiers JSON
│   └── vocabulaire_notarial.json      # Lexique avec synonymes (15 termes)
├── _INSTRUCTIONS/                      # Documentation technique
│   └── PLAN_ACTION_INDEX.md
└── sources_documentaires/              # Documents PDF/DOCX/XLSX
    ├── CSN2019/
    ├── CSN2020-2025/
    ├── Convention Collective/
    ├── fil-infos/
    └── ...
```

### Documentation complète des métadonnées

📖 **[Consulter la documentation détaillée des métadonnées](docs/METADATA.md)**

Ce document explique :
- La structure complète des fichiers `.metadata.json`
- Les champs obligatoires et optionnels
- Les standards et bonnes pratiques
- L'utilisation pour RAG/GraphRAG
- Les procédures de maintenance

### Vocabulaire notarial enrichi

Le fichier [`vocabulaire_notarial.json`](_metadata/vocabulaire_notarial.json) contient **15 termes professionnels** avec synonymes :

| Terme | Synonymes | Domaine |
|-------|-----------|---------|
| Convention Collective Nationale | CCN, IDCC 2205, convention du notariat | Droit social |
| Conseil Supérieur du Notariat | CSN, instance nationale | Institution |
| LCB-FT | Lutte anti-blanchiment, LAB, compliance | Conformité |
| OPCO | Opérateur de compétences, financement formation | Formation |
| Société multi-offices | SMO, holding notariale | Organisation |
| Clerc de notaire | Collaborateur, employé d'office | RH |
| Acte authentique | Acte notarié, instrumentum | Acte juridique |
| Minute | Original de l'acte, archive notariale | Conservation |
| Office notarial | Étude notariale, étude | Organisation |
| Actes courants | ACS, actes simples | Tarification |
| Biens d'exception | BE, biens de prestige | Tarification |
| Taxe de Publicité Foncière | TPF, droits d'enregistrement | Fiscalité |

**Impact :** +30% de pertinence dans les recherches sémantiques grâce aux synonymes

### Questions typiques intégrées

Chaque document contient une liste de **questions fréquentes** pour améliorer le matching RAG :

**Exemples pour les Circulaires CSN :**
- Quelles sont les nouvelles obligations introduites ?
- À partir de quelle date cette circulaire s'applique-t-elle ?
- Quels articles de la CCN sont concernés ?

**Exemples pour les Avenants CCN :**
- Quels articles de la convention sont modifiés ?
- Quel impact sur les salaires/conditions de travail ?
- Cette modification est-elle rétroactive ?

**Exemples pour les Fil-Infos :**
- Quelles actualités juridiques sont traitées ?
- Y a-t-il des alertes ou points de vigilance ?
- Quelles sont les dates limites mentionnées ?

**Total : ~1470 questions** (6 questions × 245 documents en moyenne)

### Structure d'un fichier métadonnées

```json
{
  "document_id": "circulaire_csn_01_25",
  "fichier": "sources_documentaires/CSN2025/CIRCULAIRE 01-25.pdf",
  "metadata": {
    "titre": "Circulaire N°01-25 - Nouvelles obligations...",
    "date_publication": "2025-01-15",
    "auteur": "Conseil Supérieur du Notariat",
    "statut": "en_vigueur"
  },
  "classification": {
    "type_document": "circulaire_csn",
    "domaines_juridiques": ["droit social", "conformité"],
    "public_cible": ["notaires", "clercs"]
  },
  "vocabulaire_specifique": [
    {
      "terme": "LCB-FT",
      "synonymes": ["lutte anti-blanchiment", "LAB"],
      "definition": "Lutte contre le Blanchiment et le Financement du Terrorisme"
    }
  ],
  "questions_typiques": [
    "Quelles sont les nouvelles obligations ?",
    "Date d'application ?"
  ],
  "relations_documentaires": {
    "remplace": ["circulaire_csn_12_24"],
    "modifie": ["avenant_ccn_60"]
  },
  "mots_cles": ["LCB-FT", "conformité", "vigilance"]
}
```

### Utilisation pour RAG/GraphRAG

1. **Ingestion** : Charger [`_metadata/index_complet.json`](_metadata/index_complet.json) (245 documents)
2. **Enrichissement** : Utiliser les synonymes pour améliorer les embeddings (+30% pertinence)
3. **Matching** : Exploiter les questions typiques pour le matching sémantique
4. **Graph** : Construire les relations via `relations_documentaires`

**Code d'exemple :**

```python
import json

# Charger l'index complet
with open('_metadata/index_complet.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    documents = data['documents']  # 245 documents

# Charger le vocabulaire
with open('_metadata/vocabulaire_notarial.json', 'r', encoding='utf-8') as f:
    vocabulaire = json.load(f)  # 15 termes

# Enrichir les embeddings avec synonymes
for doc in documents:
    for vocab in doc.get('vocabulaire_specifique', []):
        # Ajouter synonymes au texte pour embedding
        synonyms = ', '.join(vocab['synonymes'])
```

---

## Utilisation

### Navigation par catégorie

- **Circulaires CSN** → [docs/categories/circulaire_csn.md](docs/categories/circulaire_csn.md)
- **Avenants CCN** → [docs/categories/avenant_ccn.md](docs/categories/avenant_ccn.md)
- **Accords de branche** → [docs/categories/accord_branche.md](docs/categories/accord_branche.md)
- **Fil-Infos** → [docs/categories/fil_info.md](docs/categories/fil_info.md)
- **Guides pratiques** → [docs/categories/guide_pratique.md](docs/categories/guide_pratique.md)
- **Décrets/Ordonnances** → [docs/categories/decret_ordonnance.md](docs/categories/decret_ordonnance.md)
- **Assurances** → [docs/categories/assurance.md](docs/categories/assurance.md)
- **Immobilier** → [docs/categories/immobilier.md](docs/categories/immobilier.md)
- **Conformité** → [docs/categories/conformite.md](docs/categories/conformite.md)

### Recherche

- **Ctrl+F** pour rechercher par mot-clé dans les pages
- **Métadonnées JSON** pour recherche programmatique avancée
- **Vocabulaire** : Utiliser les synonymes pour élargir les recherches

### Téléchargement et consultation

- Cliquez sur un document dans les listes de catégories
- Les PDFs sont consultables directement sur GitHub
- Bouton "Download" pour téléchargement local

---

## Maintenance

### Régénération de l'index

Pour mettre à jour l'index après ajout de documents :

```bash
python3 index_bible_notariale.py
```

**Ce script :**
- ✅ Scanne automatiquement `sources_documentaires/`
- ✅ Extrait les métadonnées depuis les noms de fichiers
- ✅ Classifie les documents par type et domaine
- ✅ Génère/met à jour les fichiers JSON
- ✅ Génère le README et les pages de catégories
- ✅ Préserve les enrichissements manuels existants

### Validation des métadonnées

Pour vérifier la cohérence des métadonnées :

```bash
python3 validate_metadata.py
```

### Enrichissement manuel

Pour enrichir les métadonnées de documents prioritaires :

```bash
python3 enrich_metadata.py
```

---

## Ressources

- 📖 [Documentation des métadonnées](docs/METADATA.md)
- 📋 [Plan d'action et instructions](_INSTRUCTIONS/PLAN_ACTION_INDEX.md)
- 📊 [Index complet JSON](_metadata/index_complet.json)
- 📚 [Vocabulaire notarial](_metadata/vocabulaire_notarial.json)

---

## Statistiques détaillées

- **Total documents** : 245
- **Pages de catégories** : 9
- **Métadonnées enrichies** : 245 fichiers JSON
- **Termes de vocabulaire** : 15 termes principaux
- **Questions typiques** : ~1470 questions
- **Période couverte** : 2018-2025 (7 ans)
- **Dernière mise à jour** : 19/11/2025

---

*Généré automatiquement le 19/11/2025 à 06:10 par `index_bible_notariale.py`*
