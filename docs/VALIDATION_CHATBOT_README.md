# SYSTÈME DE VALIDATION DU CHATBOT BIBLE NOTARIALE

**Version** : 1.0
**Date** : 18 novembre 2025
**Projet** : Chatbot RAG Bible Notariale - Chambre des Notaires de Caen

---

## DOCUMENTATION DISPONIBLE

### Pour commencer

| Document | Public cible | Contenu |
|----------|-------------|---------|
| **[GUIDE_CHEF_DE_PROJET.md](guides/GUIDE_CHEF_DE_PROJET.md)** | Chef de projet technique | Guide complet pour préparer, animer et intégrer les 3 phases de validation |
| **[GUIDE_EXPERT_METIER.md](guides/GUIDE_EXPERT_METIER.md)** | Expert métier (notaire) | Guide pratique pour participer aux 3 sessions de validation |
| **[METHODOLOGIE_TEST_ASSURANCE_QUALITE.md](../_INSTRUCTIONS/METHODOLOGIE_TEST_ASSURANCE_QUALITE.md)** | Tous | Méthodologie complète et détaillée du processus de validation |

---

## VUE D'ENSEMBLE

### Objectif

Valider la qualité du système RAG du chatbot avant déploiement via une approche pragmatique et itérative impliquant les experts métier.

### Principes

- **Simplicité** : Outils familiers (Excel), pas de JSON pour les experts
- **Efficacité** : 5h d'expert métier maximum, réparties sur 2 semaines
- **Pragmatisme** : 20 documents critiques + 20 questions représentatives
- **Itératif** : Si validation OK → on continue, sinon → on corrige et re-teste

---

## LES 3 PHASES DE VALIDATION

### Phase 1 : Validation des métadonnées (2h)

**Objectif** : Vérifier que les 234 documents sont bien classés (type, catégories, priorité)

**Participants** : 1 expert métier + 1 chef de projet

**Matériel** :
- Template Excel : `templates/validation_metadonnees_20docs_TEMPLATE.xlsx`
- 20 documents PDF à consulter
- 2h en présentiel

**Résultat attendu** :
- Fichier Excel validé avec corrections
- Taux de validation ≥ 75% (15/20 documents OK)

**Documentation** :
- Guide Chef de Projet : Section "Phase 1"
- Guide Expert Métier : Section "Session 1"

---

### Phase 2 : Validation du dataset (1h30)

**Objectif** : Vérifier que les 20 questions de test sont réalistes et juridiquement exactes

**Participants** : 1-2 experts métier + 1 chef de projet

**Matériel** :
- Template Excel : `templates/validation_dataset_20questions_TEMPLATE.xlsx`
- Accès aux documents sources
- 1h30 en présentiel

**Résultat attendu** :
- Fichier Excel validé avec corrections
- Taux de validation ≥ 80% (16/20 questions OK)
- 100% des réponses juridiquement exactes

**Documentation** :
- Guide Chef de Projet : Section "Phase 2"
- Guide Expert Métier : Section "Session 2"

---

### Phase 3 : Tests du chatbot (1h30)

**Objectif** : Tester le chatbot en conditions réelles avec les 20 questions validées

**Participants** : 2-3 experts métier + 1 chef de projet (observateur)

**Matériel** :
- Interface chatbot accessible (URL)
- Template Excel : `templates/liste_questions_a_tester_TEMPLATE.xlsx`
- Système de feedback "tribunal" actif
- 1h30 en présentiel

**Résultat attendu** :
- 20 questions testées avec feedbacks
- Taux de réussite ≥ 80% (16/20)
- Score moyen ≥ 6/9 (notation sur 3 critères × 3 points)

**Documentation** :
- Guide Chef de Projet : Section "Phase 3"
- Guide Expert Métier : Section "Session 3"

---

## TEMPLATES EXCEL DISPONIBLES

Tous les templates sont disponibles dans le dossier `templates/` et peuvent être générés à l'aide des scripts Python.

### 1. Template validation métadonnées

**Fichier** : `validation_metadonnees_20docs_TEMPLATE.xlsx`

**Génération** :
```bash
python scripts/validation/create_template_validation_metadonnees.py
```

**Contenu** :
- Onglet "Instructions" : Guide pour l'expert
- Onglet "Validation_Metadonnees" : 20 lignes avec listes déroulantes

**Colonnes principales** :
- ID, Nom_Fichier, Type_Propose, Categories_Proposees, Priorite_Proposee
- Validation_Type, Correction_Type
- Validation_Categories, Correction_Categories
- Validation_Priorite, Correction_Priorite
- Commentaires

---

### 2. Template validation dataset

**Fichier** : `validation_dataset_20questions_TEMPLATE.xlsx`

**Génération** :
```bash
python scripts/validation/create_template_validation_dataset.py
```

**Contenu** :
- Onglet "Instructions" : Guide pour l'expert
- Onglet "Validation_Questions" : 20 lignes avec listes déroulantes

**Colonnes principales** :
- ID, Question, Categorie, Difficulte
- Documents_Sources_Proposes, Elements_Cles_Reponse, Reponse_Attendue_Resumee
- Validation_Question, Correction_Question
- Validation_Sources, Correction_Sources
- Validation_Elements_Cles, Correction_Elements_Cles
- Validation_Reponse_Attendue, Correction_Reponse_Attendue (CRITIQUE)
- Commentaires

---

### 3. Template liste questions test

**Fichier** : `liste_questions_a_tester_TEMPLATE.xlsx`

**Génération** :
```bash
python scripts/validation/create_template_liste_questions_test.py
```

**Contenu** :
- Liste simple des 20 questions à tester
- Colonnes : Numero, Question, Categorie, Testee, Notes_Rapides
- Compteur automatique de questions testées

---

## PLANNING TYPE (2 SEMAINES)

### Semaine 1 : Validation métadonnées + dataset

| Jour | Activité | Durée | Participants |
|------|----------|-------|--------------|
| **Lundi matin** | Préparation fichier Excel métadonnées | 1h | Chef de projet |
| **Lundi PM** | Session validation métadonnées | 2h | Expert + Chef projet |
| **Mardi** | Intégration corrections métadonnées | 4h | Chef de projet |
| **Mercredi matin** | Préparation fichier Excel dataset | 1h | Chef de projet |
| **Mercredi PM** | Session validation dataset | 1h30 | Experts + Chef projet |
| **Jeudi** | Intégration corrections dataset | 4h | Chef de projet |
| **Vendredi** | Implémentation améliorations urgentes | 4h | Chef de projet |

### Semaine 2 : Tests chatbot + décision

| Jour | Activité | Durée | Participants |
|------|----------|-------|--------------|
| **Lundi-Mardi** | Finalisation améliorations techniques | 2j | Chef de projet |
| **Mercredi PM** | Session tests chatbot | 1h30 | 2-3 Experts + Chef projet |
| **Jeudi** | Extraction feedbacks + rapport | 4h | Chef de projet |
| **Vendredi matin** | Réunion Go/No-Go Phase 2 | 2h | Tous + Client |

**Total temps expert** : 5h sur 2 semaines
**Total temps chef de projet** : 3-4 jours sur 2 semaines

---

## CRITÈRES DE SUCCÈS

### Objectifs quantitatifs

| Métrique | Objectif |
|----------|----------|
| Documents métadonnées validés | ≥ 15/20 (75%) |
| Questions dataset validées | ≥ 16/20 (80%) |
| Tests chatbot réussis | ≥ 16/20 (80%) |
| Score moyen chatbot | ≥ 6/9 (67%) |

### Décision finale

| Résultat | Décision |
|----------|----------|
| Tous les objectifs atteints | ✅ **GO PHASE 2** : Déploiement élargi |
| 1-2 critères non atteints | ⚠️ **ITÉRATION** : Corrections ciblées + re-tests |
| Problèmes structurels | ❌ **STOP** : Revoir l'architecture |

---

## STRUCTURE DES DOSSIERS

```
bible_notariale/
├── docs/
│   ├── guides/
│   │   ├── GUIDE_CHEF_DE_PROJET.md
│   │   └── GUIDE_EXPERT_METIER.md
│   └── VALIDATION_CHATBOT_README.md (ce fichier)
│
├── _INSTRUCTIONS/
│   └── METHODOLOGIE_TEST_ASSURANCE_QUALITE.md
│
├── scripts/
│   └── validation/
│       ├── create_template_validation_metadonnees.py
│       ├── create_template_validation_dataset.py
│       ├── create_template_liste_questions_test.py
│       ├── generate_validation_metadonnees.py (à créer)
│       ├── integrate_validated_metadonnees.py (à créer)
│       ├── generate_validation_dataset.py (à créer)
│       ├── integrate_validated_dataset.py (à créer)
│       ├── extract_tribunal_feedbacks.py (à créer)
│       └── generate_evaluation_report.py (à créer)
│
├── templates/
│   ├── validation_metadonnees_20docs_TEMPLATE.xlsx
│   ├── validation_dataset_20questions_TEMPLATE.xlsx
│   └── liste_questions_a_tester_TEMPLATE.xlsx
│
├── output/ (créé lors de l'exécution)
│   ├── validation_metadonnees_20docs.xlsx
│   ├── validation_metadonnees_20docs_VALIDEE.xlsx
│   ├── validation_dataset_20questions.xlsx
│   ├── validation_dataset_20questions_VALIDEE.xlsx
│   ├── liste_questions_a_tester.xlsx
│   ├── feedbacks_tribunal.csv
│   └── rapport_evaluation_chatbot.txt
│
├── _metadata/
│   └── documents/
│       └── *.metadata.json
│
└── tests/
    └── datasets/
        ├── chatbot_test_dataset.json
        └── dataset_test_final_20questions.json
```

---

## DÉMARRAGE RAPIDE

### Pour le Chef de Projet

1. **Lire la documentation** :
   - `docs/guides/GUIDE_CHEF_DE_PROJET.md` (guide complet)
   - `_INSTRUCTIONS/METHODOLOGIE_TEST_ASSURANCE_QUALITE.md` (méthodologie)

2. **Générer les templates Excel** :
   ```bash
   python scripts/validation/create_template_validation_metadonnees.py
   python scripts/validation/create_template_validation_dataset.py
   python scripts/validation/create_template_liste_questions_test.py
   ```

3. **Planifier les 3 sessions** avec les experts métier

4. **Suivre le planning** de la semaine 1 puis semaine 2

### Pour l'Expert Métier

1. **Lire le guide** :
   - `docs/guides/GUIDE_EXPERT_METIER.md`

2. **Bloquer dans votre agenda** :
   - Session 1 (S1) : 2h pour validation métadonnées
   - Session 2 (S1) : 1h30 pour validation dataset
   - Session 3 (S2) : 1h30 pour tests chatbot
   - Réunion finale (S2) : 2h (optionnel mais recommandé)

3. **Le jour J** : Venir avec votre expertise juridique, le reste est préparé !

---

## PROCHAINES ÉTAPES (À IMPLÉMENTER)

Les scripts suivants restent à développer :

### Scripts de génération des fichiers de validation

- [ ] `generate_validation_metadonnees.py` : Lit les métadonnées et génère l'Excel avec 20 docs
- [ ] `generate_validation_dataset.py` : Lit le dataset JSON et génère l'Excel avec 20 questions

### Scripts d'intégration des corrections

- [ ] `integrate_validated_metadonnees.py` : Parse l'Excel validé et met à jour les .metadata.json
- [ ] `integrate_validated_dataset.py` : Parse l'Excel validé et génère le dataset final JSON

### Scripts d'extraction et rapports

- [ ] `extract_tribunal_feedbacks.py` : Se connecte à la DB et extrait les feedbacks en CSV
- [ ] `generate_evaluation_report.py` : Calcule les métriques et génère le rapport TXT

### Outils utilitaires

- [ ] `scripts/utils/excel_helpers.py` : Fonctions réutilisables pour manipulation Excel
- [ ] `scripts/utils/metadata_reader.py` : Fonctions pour lire et parser les .metadata.json
- [ ] `scripts/utils/metrics_calculator.py` : Calcul des métriques d'évaluation

### Configuration

- [ ] `config/validation_config.yaml` : Configuration centralisée (chemins, seuils, etc.)

---

## SUPPORT

### Questions fréquentes

**Q : Où trouver les templates Excel ?**
R : Dossier `templates/` ou générez-les avec les scripts Python

**Q : Comment générer un fichier de validation pour ma session ?**
R : Utilisez les scripts `generate_validation_*.py` (à venir)

**Q : Que faire si un expert annule une session ?**
R : Reporter toute la semaine, la préparation doit être refaite

**Q : Les templates Excel fonctionnent-ils sur LibreOffice ?**
R : Oui, mais les listes déroulantes peuvent avoir un affichage légèrement différent

### Contact

- **Chef de projet** : [À compléter]
- **Développeur technique** : [À compléter]
- **Responsable méthodologie** : [À compléter]

---

## LICENCE ET CONFIDENTIALITÉ

**Document de travail - Propriété La Fabriq AI**
**Confidentialité : Usage interne projet Chambre des Notaires de Caen**

---

**Bon courage dans la mise en œuvre de ce processus de validation !**
