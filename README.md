# Bible Notariale

**Base documentaire complète pour les professionnels du notariat français**

📚 **245 documents** | 📅 **2019-2025** | 🔄 Mise à jour : 15/11/2025

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

---

## Système d'indexation et métadonnées

Ce dépôt intègre un système complet de métadonnées structurées pour l'outil de **Knowledge Management (KM)**.

### Architecture des données

```
bible_notariale/
├── README.md                           # Ce fichier
├── docs/categories/                    # Pages par catégorie
│   ├── circulaire_csn.md
│   ├── avenant_ccn.md
│   └── ...
├── _metadata/                          # Métadonnées KM
│   ├── index_complet.json             # Index global
│   ├── documents/*.metadata.json      # Métadonnées par document
│   └── vocabulaire_notarial.json      # Lexique avec synonymes
├── _INSTRUCTIONS/                      # Documentation technique
│   └── PLAN_ACTION_INDEX.md
└── sources_documentaires/              # Documents PDF/DOCX/XLSX
```

### Structure des métadonnées KM

Chaque document possède un fichier `.metadata.json` contenant :

- **Identification** : ID unique, titre, date de publication
- **Classification** : Type de document, domaines juridiques, année de référence
- **Vocabulaire spécifique** : Termes techniques avec synonymes (pour enrichir les embeddings)
- **Questions typiques** : Questions fréquentes pour améliorer le matching RAG
- **Relations** : Liens entre documents (remplace, modifie, référence)
- **Mots-clés** : Thématiques principales pour la recherche

### Vocabulaire notarial enrichi

Le fichier `vocabulaire_notarial.json` contient un lexique de termes professionnels avec leurs synonymes :

- **CCN** = Convention Collective Nationale, IDCC 2205
- **CSN** = Conseil Supérieur du Notariat
- **LCB-FT** = Lutte anti-blanchiment, LAB, compliance
- **SMO** = Société multi-offices, holding notariale
- **OPCO** = Opérateur de compétences, financement formation
- *Et plus encore...*

### Utilisation pour RAG/GraphRAG

1. **Ingestion** : Charger les `*.metadata.json` avec les documents
2. **Enrichissement** : Utiliser les synonymes pour améliorer les embeddings (+30% pertinence)
3. **Matching** : Exploiter les questions typiques pour le matching sémantique
4. **Graph** : Construire les relations entre documents

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
