# GUIDE CHEF DE PROJET
## Système de Validation du Chatbot Bible Notariale

**Version** : 1.0
**Date** : 18 novembre 2025
**Durée totale** : 2-3 jours répartis sur 2 semaines

---

## 🎉 BONNE NOUVELLE !

**Les 3 fichiers Excel sont déjà générés et prêts à l'emploi** dans le dossier `output/` :
- ✅ `validation_metadonnees_20docs.xlsx` - 20 documents pré-sélectionnés
- ✅ `validation_dataset_20questions.xlsx` - 20 questions selon répartition
- ✅ `liste_questions_a_tester.xlsx` - Liste simple pour les tests

**Vous pouvez démarrer les sessions de validation immédiatement !**

---

## VOTRE RÔLE

Vous êtes responsable de :
1. ~~Préparer les fichiers Excel de validation~~ ✅ **Déjà fait !** Les 3 fichiers Excel sont prêts dans `output/`
2. Organiser et animer les sessions de validation avec les experts métier
3. Intégrer les corrections dans le système (scripts à venir)
4. Générer les rapports de synthèse (scripts à venir)

**Temps requis** : 2-3 jours répartis sur 2 semaines (réduit grâce aux fichiers pré-générés)

---

## PHASE 1 : VALIDATION DES MÉTADONNÉES (20 DOCUMENTS)

### Objectif
Valider que l'annotation automatique des 234 documents est correcte en testant 20 documents critiques.

### ÉTAPE 1.1 : Préparation (30 min - Lundi matin)

**Bonne nouvelle** : Le fichier Excel est **déjà généré** et prêt à l'emploi !

**Localisation** : `output/validation_metadonnees_20docs.xlsx`

**Vérifications à faire** :
- [ ] Ouvrir le fichier : `open output/validation_metadonnees_20docs.xlsx`
- [ ] Vérifier que les 20 documents sont listés
- [ ] Vérifier que les colonnes de validation ont des listes déroulantes fonctionnelles
- [ ] Le fichier s'ouvre correctement dans Excel

**Préparation** :
- [ ] Identifier les PDFs des 20 documents listés dans l'Excel
- [ ] Préparer l'accès rapide aux PDFs (dossier `sources_documentaires/`)
- [ ] Préparer 2 écrans (1 pour Excel, 1 pour PDFs)

**Si besoin de régénérer le fichier** :
```bash
python scripts/validation/generate_validation_metadonnees.py
```

---

### ÉTAPE 1.2 : Session de validation (2h - Lundi après-midi)

**Préparation 30 min avant** :
1. Imprimer l'onglet "Instructions" du fichier Excel
2. Préparer 2 écrans :
   - Écran 1 : Fichier Excel ouvert
   - Écran 2 : Dossier des PDFs (`sources_documentaires/`)
3. Ouvrir les 2 premiers documents pour la démo
4. Avoir un chronomètre (5-6 min max par document)

**Matériel** :
- Fichier `validation_metadonnees_20docs.xlsx` ouvert en modification
- Accès aux PDFs sources
- 1 expert métier disponible 2h

**Déroulement** :

| Timing | Activité | Votre action |
|--------|----------|--------------|
| **0:00 - 0:10** | Introduction | Expliquer la méthodologie (voir onglet Instructions) |
| **0:10 - 0:15** | Démonstration | Valider ensemble les documents 1 et 2 |
| **0:15 - 1:30** | Validation | Parcourir les 20 documents avec l'expert |
| **1:30 - 1:50** | Enrichissement | Focus sur les docs prioritaires : améliorer les mots-clés |
| **1:50 - 2:00** | Synthèse | Noter les patterns d'erreur observés |

**Pour chaque document (5-6 min)** :
1. Ouvrir le PDF sur l'écran 2
2. Lire à voix haute : Type, Catégories, Priorité proposés
3. L'expert dit "OK" ou "À corriger"
4. Vous sélectionnez dans la liste déroulante
5. Si "À corriger" : l'expert dicte la correction, vous saisissez
6. Passer au suivant

**Conseils pratiques** :
- Ne pas passer plus de 6 min par document
- Si doute, marquer "À corriger" et mettre en commentaire "À revoir ensemble"
- Sauvegarder le fichier toutes les 5 lignes

**À la fin** :
- Sauvegarder le fichier sous `validation_metadonnees_20docs_VALIDEE.xlsx`
- Noter dans vos notes les patterns d'erreur récurrents

---

### ÉTAPE 1.3 : Intégration des corrections (2h - Mardi)

**Action** : Appliquer les corrections aux fichiers metadata.json

```bash
python scripts/validation/integrate_validated_metadonnees.py \
  --input output/validation_metadonnees_20docs_VALIDEE.xlsx \
  --output-dir _metadata/documents/
```

**Résultat attendu** :
- Les 20 fichiers `.metadata.json` sont mis à jour
- Un rapport CSV est généré : `output/rapport_integration_metadonnees.csv`

**Vérifications** :
- [ ] Nombre de corrections appliquées correspond au nombre de "À corriger" dans l'Excel
- [ ] Les fichiers JSON sont valides (pas d'erreur de syntaxe)
- [ ] Backup des fichiers originaux créé dans `_metadata/backup_YYYYMMDD/`

**Analyse des patterns** :
1. Ouvrir `output/rapport_integration_metadonnees.csv`
2. Si > 5 documents ont le même type d'erreur → Note pour améliorer le script d'annotation
3. Documenter dans `docs/patterns_erreur_metadonnees.txt`

**Décision Go/No-Go** :

| Résultat | Action |
|----------|--------|
| ≥ 15/20 documents validés OK | ✅ Passer à Phase 2 |
| 10-14/20 validés | ⚠️ Corriger le script d'annotation + re-valider 20 nouveaux docs |
| < 10/20 validés | ❌ Revoir complètement la stratégie d'annotation |

---

## PHASE 2 : VALIDATION DU DATASET (20 QUESTIONS)

### Objectif
Valider que les 20 questions de test sont réalistes et que les réponses attendues sont juridiquement exactes.

### ÉTAPE 2.1 : Préparation (30 min - Mercredi matin)

**Bonne nouvelle** : Le fichier Excel est **déjà généré** et prêt à l'emploi !

**Localisation** : `output/validation_dataset_20questions.xlsx`

**Vérifications** :
- [ ] Ouvrir le fichier : `open output/validation_dataset_20questions.xlsx`
- [ ] Vérifier la répartition : 8 déonto, 5 juridique, 4 multi, 3 edge
- [ ] Vérifier que les éléments clés de réponse sont bien formatés (numérotés)
- [ ] Vérifier que les listes déroulantes fonctionnent

**Préparation** :
- [ ] Préparer l'accès rapide aux documents sources mentionnés
- [ ] Imprimer l'onglet "Instructions" si besoin

**Si besoin de régénérer le fichier** :
```bash
python scripts/validation/generate_validation_dataset.py
```

---

### ÉTAPE 2.2 : Session de validation (1h30 - Mercredi après-midi)

**Préparation 30 min avant** :
1. Imprimer l'onglet "Instructions"
2. Préparer accès aux documents sources (PDFs)
3. Prévoir 3-4 min par question max

**Matériel** :
- Fichier `validation_dataset_20questions.xlsx` ouvert
- 1-2 experts métier disponibles 1h30

**Déroulement** :

| Timing | Activité | Votre action |
|--------|----------|--------------|
| **0:00 - 0:10** | Introduction | Expliquer la méthodologie |
| **0:10 - 1:10** | Validation | Parcourir les 20 questions (3 min/question) |
| **1:10 - 1:25** | Enrichissement | Focus questions pointues : affiner réponses attendues |
| **1:25 - 1:30** | Synthèse | Noter les ajustements nécessaires |

**Pour chaque question (3 min)** :
1. Lire la question à voix haute
2. Expert valide : Réaliste ? Sources correctes ? Éléments clés complets ? Réponse exacte ?
3. Vous cochez dans les listes déroulantes
4. Si correction nécessaire : l'expert dicte, vous saisissez

**À la fin** :
- Sauvegarder sous `validation_dataset_20questions_VALIDEE.xlsx`

---

### ÉTAPE 2.3 : Intégration des corrections (2h - Jeudi)

**Action** : Créer le dataset final validé

```bash
python scripts/validation/integrate_validated_dataset.py \
  --input output/validation_dataset_20questions_VALIDEE.xlsx \
  --output tests/datasets/dataset_test_final_20questions.json
```

**Résultat attendu** :
- Fichier JSON avec les 20 questions validées et corrigées
- Rapport CSV : `output/rapport_integration_dataset.csv`

**Vérifications** :
- [ ] Le JSON est valide
- [ ] Les 20 questions sont présentes
- [ ] Les corrections ont bien été appliquées

**Décision Go/No-Go** :

| Résultat | Action |
|----------|--------|
| ≥ 16/20 questions validées OK | ✅ Passer à Phase 3 (Tests chatbot) |
| 12-15/20 validées | ⚠️ Reformuler + re-valider |
| < 12/20 validées | ❌ Revoir la méthodologie de génération des questions |

---

## PHASE 3 : TESTS DU CHATBOT (20 QUESTIONS)

### Objectif
Tester le chatbot avec les 20 questions validées et collecter les feedbacks via le système "tribunal".

### ÉTAPE 3.1 : Préparation (30 min - Mercredi matin S2)

**Bonne nouvelle** : Le fichier Excel est **déjà généré** et prêt à l'emploi !

**Localisation** : `output/liste_questions_a_tester.xlsx`

**Vérifications pré-session** :
- [ ] Ouvrir le fichier : `open output/liste_questions_a_tester.xlsx`
- [ ] Vérifier que les 20 questions sont listées
- [ ] Le chatbot est accessible (tester avec 1 question simple)
- [ ] Le système tribunal enregistre les feedbacks
- [ ] Imprimer ou partager le fichier Excel avec les experts

**Si besoin de régénérer le fichier** :
```bash
python scripts/validation/generate_liste_questions_test.py
```

---

### ÉTAPE 3.2 : Session de tests (1h30 - Mercredi après-midi S2)

**Matériel** :
- Interface chatbot accessible (URL)
- Fichier `liste_questions_a_tester.xlsx` imprimé ou partagé
- 2-3 experts métier disponibles 1h30

**Déroulement** :

| Timing | Activité | Votre rôle |
|--------|----------|------------|
| **0:00 - 0:10** | Présentation | Montrer l'interface chatbot et le système de feedback |
| **0:10 - 0:15** | Démonstration | Tester 1 question ensemble en direct |
| **0:15 - 1:15** | Tests individuels | Observer en silence (chaque expert teste ~7 questions) |
| **1:15 - 1:30** | Débrief | Collecter les observations sur les patterns d'erreur |

**Instructions pour les experts** (à imprimer ou projeter) :

```
COMMENT TESTER UNE QUESTION
---------------------------
1. Choisir une question dans la liste Excel
2. La poser au chatbot via l'interface
3. Lire la réponse complète
4. Utiliser le système de feedback "tribunal" pour noter sur 3 critères :

   EXACTITUDE /3 (pertinence + complétude de la réponse)
   ├─ 0/3 : Incorrecte, hors sujet ou très incomplète
   ├─ 1/3 : Partiellement correcte avec erreurs importantes
   ├─ 2/3 : Correcte mais il manque des éléments
   └─ 3/3 : Complète, pertinente et exacte

   SOURCES /3 (pertinence + complétude des sources citées)
   ├─ 0/3 : Aucune source ou non pertinentes
   ├─ 1/3 : Sources partiellement pertinentes ou incomplètes
   ├─ 2/3 : Pertinentes mais il en manque
   └─ 3/3 : Parfaites (pertinentes et complètes)

   FORMULATION /3 (clarté + style notarial + longueur)
   ├─ 0/3 : Incompréhensible, trop longue ou inadaptée
   ├─ 1/3 : Peu claire ou style/longueur inadaptés
   ├─ 2/3 : Claire mais peut être améliorée
   └─ 3/3 : Excellente (claire, professionnelle, adaptée)

   + Commentaire libre avec observations précises

5. Cocher "Testée" dans l'Excel
6. Passer à la suivante

SCORE TOTAL : /9 (Objectif : ≥ 7/9 pour validation)
```

**Votre rôle pendant les tests** :
- Observer en SILENCE (ne pas influencer les experts)
- Noter les bugs ou comportements inattendus
- Noter les questions qui semblent poser problème
- Ne PAS intervenir sauf si blocage technique

**Pendant le débrief (15 min)** :
- Demander : "Quelles questions ont le mieux fonctionné ?"
- Demander : "Quels patterns d'erreur avez-vous observés ?"
- Noter les retours dans `docs/observations_tests_chatbot.txt`

---

### ÉTAPE 3.3 : Extraction et analyse (3h - Jeudi S2)

**Action 1** : Extraire les feedbacks du système tribunal

```bash
python scripts/validation/extract_tribunal_feedbacks.py \
  --output output/feedbacks_tribunal.csv
```

**Résultat attendu** : Fichier CSV avec colonnes :
- `question_id`, `timestamp`, `exactitude_score` (0-3), `sources_score` (0-3),
  `formulation_score` (0-3), `score_total` (0-9), `commentaire`, `testeur_id`

**Action 2** : Générer le rapport d'évaluation (simplifié)

```bash
python scripts/validation/generate_evaluation_report.py \
  --feedbacks output/feedbacks_tribunal.csv \
  --dataset tests/datasets/dataset_test_final_20questions.json \
  --output output/rapport_evaluation_chatbot.txt
```

**Résultat attendu** : Rapport texte lisible avec :
- Synthèse des résultats (score moyen, taux de réussite)
- Répartition par difficulté et par catégorie
- Liste des questions ayant échoué
- Patterns d'erreur identifiés
- Recommandations

**Analyse manuelle** :
1. Lire le rapport
2. Identifier les 3-5 améliorations prioritaires
3. Documenter dans `docs/recommandations_ameliorations.txt`

---

## DÉCISION FINALE (Vendredi matin S2)

**Réunion Go/No-Go Phase 2** (2h)

**Participants** : Experts, Équipe technique, Client

**Documents à présenter** :
1. `output/rapport_integration_metadonnees.csv`
2. `output/rapport_integration_dataset.csv`
3. `output/rapport_evaluation_chatbot.txt`
4. `docs/recommandations_ameliorations.txt`

**Grille de décision** :

| Critère | Résultat | Objectif | Statut |
|---------|----------|----------|--------|
| Métadonnées validées | __/20 | ≥ 15 | |
| Questions validées | __/20 | ≥ 16 | |
| Tests chatbot réussis | __/20 | ≥ 16 | |
| Score moyen chatbot | __/9 | ≥ 6 | |

**Décision** :
- ✅ **GO PHASE 2** : Tous les objectifs atteints → Déploiement élargi
- ⚠️ **ITÉRATION** : 1-2 critères non atteints → Corrections ciblées + re-tests
- ❌ **STOP** : Problèmes structurels → Revoir l'architecture

---

## SCRIPTS DISPONIBLES

### ✅ Fichiers Excel (déjà générés)

Les 3 fichiers Excel sont **déjà prêts** dans `output/` :
- `output/validation_metadonnees_20docs.xlsx` ✅
- `output/validation_dataset_20questions.xlsx` ✅
- `output/liste_questions_a_tester.xlsx` ✅

**Pour les ouvrir** :
```bash
open output/validation_metadonnees_20docs.xlsx
open output/validation_dataset_20questions.xlsx
open output/liste_questions_a_tester.xlsx
```

### Régénération des fichiers Excel (si nécessaire)

| Script | Commande | Résultat |
|--------|----------|----------|
| **Métadonnées** | `python scripts/validation/generate_validation_metadonnees.py` | Régénère `output/validation_metadonnees_20docs.xlsx` |
| **Dataset** | `python scripts/validation/generate_validation_dataset.py` | Régénère `output/validation_dataset_20questions.xlsx` |
| **Liste questions** | `python scripts/validation/generate_liste_questions_test.py` | Régénère `output/liste_questions_a_tester.xlsx` |

### Intégration des corrections

| Script | Commande | Résultat |
|--------|----------|----------|
| **Métadonnées** | `python scripts/validation/integrate_validated_metadonnees.py --input output/validation_metadonnees_20docs_VALIDEE.xlsx` | Mise à jour des `.metadata.json` |
| **Dataset** | `python scripts/validation/integrate_validated_dataset.py --input output/validation_dataset_20questions_VALIDEE.xlsx` | `dataset_test_final_20questions.json` |

### Extraction et rapports

| Script | Commande | Résultat |
|--------|----------|----------|
| **Feedbacks tribunal** | `python scripts/validation/extract_tribunal_feedbacks.py` | `output/feedbacks_tribunal.csv` |
| **Rapport évaluation** | `python scripts/validation/generate_evaluation_report.py` | `output/rapport_evaluation_chatbot.txt` |

---

## GESTION DES PROBLÈMES

### Problème : Le script de génération échoue

**Solution** :
1. Vérifier les logs dans `logs/`
2. Vérifier que les fichiers d'entrée existent
3. Vérifier les permissions d'écriture sur `output/`
4. Consulter `docs/FAQ_TECHNIQUE.md`

### Problème : L'expert n'est pas disponible

**Solution** :
- Planifier les sessions 2 semaines à l'avance
- Prévoir 30 min de marge sur chaque session
- Si annulation : reporter toute la semaine

### Problème : Fatigue de validation (> 2h)

**Solution** :
- Faire une pause de 10 min après 1h
- Ne jamais dépasser 2h sans pause
- Si besoin, découper en 2 sessions de 1h

### Problème : Désaccord sur une validation

**Solution** :
- Marquer "À corriger" + commentaire "À revoir en réunion"
- Ne pas perdre de temps en débat pendant la session
- Trancher en réunion finale

### Problème : Résultats insuffisants (< objectifs)

**Solution** :
- Analyser les patterns d'erreur dans les rapports CSV
- Identifier si c'est un problème systémique ou ponctuel
- Planifier une itération de correction (prévoir +3 à 5 jours)

---

## CHECKLIST COMPLÈTE

### Avant de commencer
- [ ] Installer les dépendances Python (`pip install -r requirements_validation.txt`)
- [ ] Vérifier que les dossiers `_metadata/documents/` et `tests/datasets/` existent
- [ ] ✅ Les 3 fichiers Excel sont déjà générés dans `output/` !
- [ ] Planifier les 3 sessions de validation avec les experts

### Phase 1 - Métadonnées
- [x] ~~Générer le fichier Excel~~ ✅ Déjà fait : `output/validation_metadonnees_20docs.xlsx`
- [ ] Ouvrir et vérifier le fichier (10 min)
- [ ] Préparer les PDFs des 20 documents (20 min)
- [ ] Session de validation avec expert (2h)
- [ ] Intégrer les corrections (2h) - script à venir
- [ ] Analyser les patterns d'erreur
- [ ] Décision Go/No-Go Phase 1

### Phase 2 - Dataset
- [x] ~~Générer le fichier Excel~~ ✅ Déjà fait : `output/validation_dataset_20questions.xlsx`
- [ ] Ouvrir et vérifier le fichier (10 min)
- [ ] Préparer l'accès aux documents sources (20 min)
- [ ] Session de validation avec experts (1h30)
- [ ] Intégrer les corrections (2h) - script à venir
- [ ] Décision Go/No-Go Phase 2

### Phase 3 - Tests chatbot
- [x] ~~Générer la liste de questions~~ ✅ Déjà fait : `output/liste_questions_a_tester.xlsx`
- [ ] Vérifier le système tribunal (30 min)
- [ ] Imprimer/partager la liste de questions (10 min)
- [ ] Session de tests avec experts (1h30)
- [ ] Extraire les feedbacks (1h) - script à venir
- [ ] Générer le rapport d'évaluation (2h) - script à venir
- [ ] Préparer la réunion de décision

### Après validation
- [ ] Sauvegarder tous les fichiers validés dans `output/archives/YYYYMMDD/`
- [ ] Documenter les leçons apprises
- [ ] Planifier les améliorations identifiées

---

## CONTACTS UTILES

| Rôle | Contact | Disponibilité |
|------|---------|---------------|
| **Expert métier principal** | [À compléter] | 5h sur 2 semaines |
| **Développeur backend** | [À compléter] | En cas de bug technique |
| **Responsable projet** | [À compléter] | Validation finale |

---

## RESSOURCES

- Méthodologie complète : `_INSTRUCTIONS/METHODOLOGIE_TEST_ASSURANCE_QUALITE.md`
- Templates Excel : `templates/`
- Scripts Python : `scripts/validation/`
- Documentation technique : `docs/`

---

## ANNEXE : GÉNÉRATION MANUELLE DES FICHIERS EXCEL

**Note** : Cette section n'est utile que si vous devez **régénérer** les fichiers Excel (par exemple, pour sélectionner d'autres documents/questions ou après une mise à jour des données).

**Les fichiers sont déjà générés et prêts dans `output/` - vous n'avez normalement pas besoin de cette annexe.**

---

### Pourquoi régénérer les fichiers ?

Vous pourriez avoir besoin de régénérer les fichiers Excel si :
- Vous voulez sélectionner d'autres documents (critères de sélection différents)
- Vous voulez sélectionner d'autres questions (répartition différente)
- Les métadonnées ont été mises à jour et vous voulez travailler avec les dernières versions
- Les fichiers Excel ont été corrompus ou perdus

---

### GÉNÉRATION PHASE 1 : Validation des métadonnées

**Commande** :
```bash
cd /chemin/vers/bible_notariale
python scripts/validation/generate_validation_metadonnees.py
```

**Résultat** : Fichier créé dans `output/validation_metadonnees_20docs.xlsx`

**Critères de sélection automatique** :
- 3 documents avec priorité maximale (RPN, Circulaires CSN, etc.)
- 5 types de documents différents (1 par type)
- 5 documents avec peu de mots-clés (potentiellement problématiques)
- 7 documents complémentaires

**Personnalisation** :
Si vous voulez modifier les critères de sélection, éditez le fichier :
`scripts/validation/generate_validation_metadonnees.py`

Fonction à modifier : `select_20_documents()`

---

### GÉNÉRATION PHASE 2 : Validation du dataset

**Commande** :
```bash
python scripts/validation/generate_validation_dataset.py
```

**Résultat** : Fichier créé dans `output/validation_dataset_20questions.xlsx`

**Répartition automatique** :
- 8 questions Déontologie (3 facile, 3 moyen, 2 pointu)
- 5 questions Juridique CCN/RH (2 facile, 2 moyen, 1 pointu)
- 4 questions Multi-documents (1 facile, 2 moyen, 1 pointu)
- 3 questions Edge cases (1 facile, 1 moyen, 1 pointu)

**Personnalisation** :
Si vous voulez modifier la répartition, éditez le fichier :
`scripts/validation/generate_validation_dataset.py`

Fonction à modifier : `select_20_questions()`

Variable à modifier : `selection_plan`

---

### GÉNÉRATION PHASE 3 : Liste des questions à tester

**Commande** :
```bash
python scripts/validation/generate_liste_questions_test.py
```

**Résultat** : Fichier créé dans `output/liste_questions_a_tester.xlsx`

**Source des données** :
Le script utilise par défaut :
1. Le dataset validé Phase 2 : `tests/datasets/dataset_test_final_20questions.json` (si existe)
2. Sinon, le dataset original : `tests/datasets/chatbot_test_dataset.json` (20 premières questions)

**Note** : Ce fichier est une simple liste pour la session de tests. Il reprend les questions validées en Phase 2.

---

### Logs et débogage

**Logs de génération** :
- Les scripts affichent des messages détaillés dans la console
- Vérifiez que le nombre de documents/questions sélectionnés est correct
- En cas d'erreur, les messages d'erreur indiquent le problème

**Erreurs courantes** :

| Erreur | Cause | Solution |
|--------|-------|----------|
| `Template non trouvé` | Le template Excel n'existe pas | Exécuter `python scripts/validation/create_template_*.py` |
| `Aucun fichier dataset trouvé` | Le dataset JSON n'existe pas | Vérifier le chemin `tests/datasets/` |
| `Seulement X documents trouvés` | Moins de 20 documents disponibles | Normal si < 20 docs dans la base, le script complète |

**Vérification après génération** :
```bash
# Ouvrir le fichier généré
open output/validation_metadonnees_20docs.xlsx

# Vérifier le nombre de lignes
# → Doit avoir exactement 20 lignes de données (+ 1 en-tête)

# Vérifier les listes déroulantes
# → Colonnes de validation doivent avoir des menus déroulants fonctionnels
```

---

### Génération de tous les fichiers d'un coup

**Script rapide** :
```bash
# Générer les 3 fichiers Excel
python scripts/validation/generate_validation_metadonnees.py && \
python scripts/validation/generate_validation_dataset.py && \
python scripts/validation/generate_liste_questions_test.py

# Vérifier qu'ils existent tous
ls -lh output/*.xlsx
```

**Résultat attendu** :
```
validation_metadonnees_20docs.xlsx      (8-10 KB)
validation_dataset_20questions.xlsx     (10-15 KB)
liste_questions_a_tester.xlsx           (6-8 KB)
```

---

### Sauvegarde avant régénération

**Important** : Si vous régénérez les fichiers, sauvegardez d'abord les versions existantes :

```bash
# Créer un dossier d'archive avec la date
mkdir -p output/archives/$(date +%Y%m%d)

# Copier les fichiers existants
cp output/validation_*.xlsx output/archives/$(date +%Y%m%d)/
cp output/liste_*.xlsx output/archives/$(date +%Y%m%d)/

# Puis régénérer
python scripts/validation/generate_validation_metadonnees.py
```

---

### Questions fréquentes

**Q : Dois-je régénérer les fichiers avant chaque session ?**
R : Non ! Les fichiers sont déjà générés et prêts. Régénérez uniquement si vous voulez changer la sélection.

**Q : Puis-je modifier manuellement les fichiers Excel générés ?**
R : Oui, mais attention : si vous régénérez, vos modifications seront perdues. Mieux vaut modifier le script de génération.

**Q : Combien de temps prend la génération ?**
R : Quelques secondes pour chaque fichier (< 10 secondes au total).

**Q : Puis-je sélectionner manuellement les 20 documents ?**
R : Oui, mais c'est fastidieux. Mieux vaut modifier le script `generate_validation_metadonnees.py` pour implémenter votre logique de sélection.

**Q : Les fichiers générés sont-ils toujours les mêmes ?**
R : Oui, sauf si vous modifiez les critères de sélection dans les scripts ou si les données source changent.

---

**Bon courage ! Ce processus est conçu pour être pragmatique et efficace.**
**En cas de doute, privilégiez la simplicité et la clarté.**
