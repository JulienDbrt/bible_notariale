# Plan d'Action - Indexation Bible Notariale

## Objectif
Créer un index navigable sur GitHub avec métadonnées structurées pour outil de Knowledge Management (RAG/GraphRAG).

---

## Phase 1 : Analyse & Classification des Documents

### 1.1 Extraction des métadonnées depuis les noms de fichiers
- Scanner les 245 documents dans `sources_documentaires/`
- Patterns à détecter :
  - **Dates** : `YYYYMMDD`, `YYYY-MM-DD`, `DD/MM/YYYY`
  - **Numéros de référence** : `Avenant n°X`, `Circulaire N°YYYY-X`
  - **Types** : Circulaire, Avenant, Accord, Guide, Décret, etc.
  - **Catégories** : CSN2019-2025, Convention Collective, Fil-Infos, etc.

### 1.2 Système de classification (vocabulaire notarial)

| Label | Description | Exemples |
|-------|-------------|----------|
| `circulaire_csn` | Instructions officielles du Conseil Supérieur du Notariat | CIRCULAIRE 01-25, Circulaire N°2020-1 |
| `avenant_ccn` | Modifications de la Convention Collective Nationale | Avenant n°48, Avenant n°60 |
| `accord_branche` | Négociations collectives et accords professionnels | Accord de salaires, Accord harcèlement |
| `fil_info` | Bulletins d'actualité et veille juridique | fil-info-224 à fil-info-2909 |
| `guide_pratique` | Documentation métier et bonnes pratiques | Guide informatique, Fiche bonnes pratiques |
| `decret_ordonnance` | Textes réglementaires officiels | Décret 2024-906, Ordonnance PLR |
| `remuneration` | Salaires, primes, intéressement | Accord de salaires, Partage de la valeur |
| `prevoyance_assurance` | Protection sociale et assurances | Contrat cyber, Complémentaire santé |
| `formation_pro` | Développement professionnel et alternance | Formation, OPCO, reconversion |
| `immobilier` | Transactions et obligations immobilières | Guide négociation immobilière, Observatoire |
| `conformite` | LCB-FT, RGPD, cyber-sécurité | Analyse risques LCB-FT, Cyber-attaque |
| `procedure_rh` | Licenciement, période d'essai, congés | Modification art. 12.2, Congés payés |

---

## Phase 2 : Génération des Métadonnées KM (JSON)

### 2.1 Structure JSON par document

```json
{
  "document_id": "identifiant_unique",
  "fichier": "nom_fichier.pdf",
  "metadata": {
    "titre": "Titre complet du document",
    "titre_court": "Titre abrégé",
    "date_publication": "YYYY-MM-DD",
    "date_effet": "YYYY-MM-DD",
    "version": "X.Y",
    "langue": "fr",
    "auteur": "CSN | Organisme",
    "statut": "en_vigueur | remplace | archive"
  },
  "classification": {
    "type_document": "circulaire_csn | avenant_ccn | ...",
    "domaines_juridiques": ["droit social", "assurance", "immobilier"],
    "public_cible": ["notaires", "clercs", "comptables offices"],
    "annee_reference": 2025
  },
  "vocabulaire_specifique": [
    {
      "terme": "Terme technique notarial",
      "synonymes": ["syn1", "syn2", "abréviation"],
      "definition": "Définition claire et concise",
      "contexte_utilisation": "Dans quel cadre ce terme apparaît"
    }
  ],
  "questions_typiques": [
    "Question que poserait un notaire sur ce document ?",
    "Autre question fréquente ?",
    "Comment appliquer telle disposition ?"
  ],
  "relations_documentaires": {
    "remplace": ["ancien_document.pdf"],
    "modifie": ["document_modifie.pdf"],
    "reference": ["Code civil", "Convention Collective"],
    "complete": ["document_complementaire.pdf"]
  },
  "resume": "Résumé en 2-3 phrases du contenu et de l'objectif du document",
  "mots_cles": ["mot1", "mot2", "mot3"]
}
```

### 2.2 Vocabulaire notarial prioritaire à enrichir

| Terme | Synonymes | Domaine |
|-------|-----------|---------|
| Convention Collective Nationale | CCN, IDCC 2205, accord de branche | Droit social |
| Conseil Supérieur du Notariat | CSN, instance nationale | Institution |
| Avenant | modification, amendement, révision | Juridique |
| Circulaire | instruction, note, directive | Administratif |
| LCB-FT | Lutte anti-blanchiment, LAB, compliance | Conformité |
| OPCO | Opérateur de compétences, financement formation | Formation |
| Société multi-offices | SMO, holding notariale, structure multi-offices | Organisation |
| Clerc de notaire | collaborateur, employé d'office | RH |
| Acte authentique | acte notarié, instrumentum | Acte juridique |
| Minute | original de l'acte, archive notariale | Conservation |

### 2.3 Questions typiques par type de document

**Circulaires CSN :**
- Quelles sont les nouvelles obligations introduites ?
- À partir de quelle date cette circulaire s'applique-t-elle ?
- Quels articles de la CCN sont concernés ?

**Avenants CCN :**
- Quels articles de la convention sont modifiés ?
- Quel impact sur les salaires/conditions de travail ?
- Cette modification est-elle rétroactive ?

**Accords de branche :**
- Quelles sont les nouvelles dispositions négociées ?
- Qui sont les signataires ?
- Quelle est la durée de validité ?

**Fil-Infos :**
- Quelles actualités juridiques sont traitées ?
- Y a-t-il des alertes ou points de vigilance ?
- Quelles sont les dates limites mentionnées ?

---

## Phase 3 : Génération du README.md (Index GitHub)

### 3.1 Structure du README

```markdown
# Bible Notariale - Index Documentaire

## Présentation
Base documentaire complète pour les professionnels du notariat français.
245 documents | 2019-2025 | Mise à jour : [DATE]

## Statistiques
- [X] Circulaires CSN
- [X] Avenants Convention Collective
- [X] Accords de branche
- [X] Fil-Infos
- etc.

## Navigation par catégorie

### Circulaires CSN
| Date | Référence | Titre | Type |
|------|-----------|-------|------|
| 2025-XX-XX | CIRCULAIRE 01-25 | [Titre](lien) | Information |

### Convention Collective - Avenants
[...]

### Fil-Infos (Actualités)
[...]

## Index chronologique
[...]

## Recherche
Utilisez Ctrl+F pour rechercher par mot-clé.
```

### 3.2 Liens cliquables
- Format : `[Titre du document](sources_documentaires/categorie/fichier.pdf)`
- Les PDFs sont directement consultables sur GitHub

---

## Phase 4 : Export et Livraisons

### 4.1 Fichiers générés

```
bible_notariale/
├── README.md                           # Index principal navigable
├── _INSTRUCTIONS/
│   └── PLAN_ACTION_INDEX.md           # Ce document
├── _metadata/
│   ├── index_complet.json             # Base de données complète
│   ├── documents/
│   │   ├── doc_001.metadata.json      # Métadonnées par document
│   │   ├── doc_002.metadata.json
│   │   └── ...
│   └── vocabulaire_notarial.json      # Lexique enrichi
└── sources_documentaires/
    └── [documents existants]
```

### 4.2 Utilisation pour KM Tool

1. **Ingestion** : Charger `_metadata/documents/*.metadata.json`
2. **Enrichissement texte** : Ajouter synonymes et contexte aux embeddings
3. **Graph** : Construire relations via `relations_documentaires`
4. **Recherche** : Utiliser `questions_typiques` pour matching sémantique

---

## Implémentation

### Script Python principal

```python
# index_bible_notariale.py

def main():
    # 1. Scanner les fichiers
    documents = scan_sources_documentaires()

    # 2. Extraire métadonnées depuis noms
    for doc in documents:
        doc.metadata = extract_metadata_from_filename(doc.path)
        doc.classification = classify_document(doc)

    # 3. Générer JSON KM pour chaque document
    for doc in documents:
        km_metadata = generate_km_metadata(doc)
        save_json(km_metadata, f"_metadata/documents/{doc.id}.metadata.json")

    # 4. Générer index global
    global_index = compile_global_index(documents)
    save_json(global_index, "_metadata/index_complet.json")

    # 5. Générer README.md
    readme = generate_readme(documents, global_index)
    save_markdown(readme, "README.md")

    # 6. Exporter vocabulaire notarial
    vocab = extract_vocabulary(documents)
    save_json(vocab, "_metadata/vocabulaire_notarial.json")
```

### Priorités d'enrichissement KM

**Niveau 1 - Automatique (noms de fichiers)** :
- Type de document
- Date de publication
- Numéro de référence
- Catégorie (CSN2025, Convention Collective, etc.)

**Niveau 2 - Semi-automatique (patterns)** :
- Mots-clés généraux
- Relations entre documents (même numéro d'avenant)
- Domaines juridiques principaux

**Niveau 3 - Manuel (enrichissement futur)** :
- Résumés détaillés (après extraction PDF)
- Vocabulaire spécifique avec synonymes
- Questions typiques contextualisées
- Liens vers textes de loi

---

## Prochaines étapes

1. **Immédiat** : Exécuter Phase 1-3 avec métadonnées automatiques
2. **Court terme** : Enrichir manuellement les 20-30 documents clés
3. **Moyen terme** : Extraction de texte PDF pour enrichissement automatique
4. **Long terme** : Intégration complète dans pipeline RAG/GraphRAG

---

## Notes techniques

- **Encodage** : UTF-8 pour caractères français (accents, cédilles)
- **Dates** : Format ISO 8601 (YYYY-MM-DD) dans JSON
- **IDs documents** : snake_case, sans accents, unique
- **Chemins** : Relatifs depuis racine du repo pour portabilité

---

*Plan créé le : 2025-11-15*
*Version : 1.0*
