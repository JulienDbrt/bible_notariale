# FICHIERS EXCEL DE VALIDATION - PRÊTS À L'EMPLOI

**Générés le** : 18 novembre 2025
**Statut** : ✅ Prêts pour utilisation

---

## 📊 FICHIERS DISPONIBLES

### 1. validation_metadonnees_20docs.xlsx (8.9 KB)

**Phase** : Phase 1 - Validation des métadonnées
**Durée session** : 2h
**Participants** : 1 expert métier + 1 chef de projet

**Contenu** :
- 20 documents pré-sélectionnés avec leurs métadonnées
- Type de document, catégories métier, priorité, mots-clés
- Colonnes de validation avec listes déroulantes (OK / A corriger)

**Sélection** :
- 3 documents priorité 10 (RPN, Circulaire 01-25, etc.)
- 5 types de documents différents
- 5 documents avec peu de mots-clés (potentiellement problématiques)
- 7 documents complémentaires

**Utilisation** :
1. Ouvrir le fichier Excel
2. Pour chaque document :
   - Consulter le PDF source
   - Valider Type, Catégories, Priorité
   - Cocher OK ou À corriger
   - Si À corriger : indiquer la correction
3. Sauvegarder sous `validation_metadonnees_20docs_VALIDEE.xlsx`

---

### 2. validation_dataset_20questions.xlsx (12 KB)

**Phase** : Phase 2 - Validation du dataset de questions
**Durée session** : 1h30
**Participants** : 1-2 experts métier + 1 chef de projet

**Contenu** :
- 20 questions pré-sélectionnées selon répartition méthodologique
- Question, catégorie, difficulté, documents sources, éléments clés, réponse attendue
- 4 types de validation avec listes déroulantes

**Répartition** :
- 8 questions Déontologie (3 facile, 3 moyen, 2 pointu)
- 5 questions Juridique CCN/RH (2 facile, 2 moyen, 1 pointu)
- 4 questions Multi-documents (1 facile, 2 moyen, 1 pointu)
- 3 questions Edge cases (1 facile, 1 moyen, 1 pointu)

**Utilisation** :
1. Ouvrir le fichier Excel
2. Pour chaque question :
   - Lire la question
   - Valider si réaliste (Oui / Non / À reformuler)
   - Valider les documents sources (Oui / Non / Incomplet)
   - Valider les éléments clés (Oui / Incomplet / Incorrect)
   - Valider la réponse attendue (Oui / Non / À préciser) ⚠️ CRITIQUE
3. Sauvegarder sous `validation_dataset_20questions_VALIDEE.xlsx`

---

### 3. liste_questions_a_tester.xlsx (6.6 KB)

**Phase** : Phase 3 - Tests du chatbot (VERSION SIMPLE)
**Durée session** : 1h30
**Participants** : 2-3 experts métier + 1 chef de projet (observateur)

**Contenu** :
- Liste simple des 20 questions à tester
- Numéro, Question, Catégorie, Case "Testée", Notes rapides

**Utilisation** :
1. Imprimer ou partager le fichier avec les experts
2. Chaque expert :
   - Choisit une question non testée
   - La pose au chatbot via l'interface web
   - Donne son feedback via le système "tribunal"
   - Coche "Testée" dans l'Excel
   - Ajoute des notes rapides si nécessaire
3. Répéter jusqu'à ce que les 20 questions soient testées

---

### 4. suivi_tests_chatbot.xlsx ⭐ NOUVEAU

**Phase** : Phase 3 - Tests du chatbot (VERSION ENRICHIE)
**Durée session** : 1h30
**Participants** : 2-3 experts métier + 1 chef de projet

**Contenu** :
- 20 questions pré-remplies avec catégories et réponses de référence
- Colonnes pour noter les 3 critères : Exactitude /3, Sources /3, Formulation /3
- Calcul automatique du score total /9 et du status (✅/❌)
- Onglet "Synthese" avec métriques automatiques et décision finale

**Structure** :
- **Onglet QA_Tests** : Suivi détaillé de chaque question
  - ID Test, Catégorie, Question
  - Document Source
  - Date Test
  - Réponse Obtenue (à copier-coller depuis le chatbot)
  - Exactitude /3, Sources /3, Formulation /3
  - TOTAL /9 (formule automatique)
  - Status (✅ si ≥6/9, ❌ si <6/9)
  - Notes/Commentaires
  - Réponse de Référence (issue du dataset validé)

- **Onglet Synthese** : Métriques automatiques
  - Total tests, Tests exécutés
  - Réussis, Échecs
  - Score moyen global
  - % de réussite
  - Scores moyens par critère
  - **Décision finale calculée automatiquement**

**Utilisation** :
1. Ouvrir le fichier Excel
2. Pour chaque question (lignes 5 à 24) :
   - Lire la question (colonne C)
   - Poser la question au chatbot
   - Copier-coller la réponse obtenue dans la colonne F
   - Comparer avec la réponse de référence (colonne M)
   - Noter sur les 3 critères (colonnes G, H, I)
   - Ajouter des commentaires si nécessaire (colonne L)
3. Le score total et le status se calculent automatiquement
4. Consulter l'onglet "Synthese" pour voir les métriques globales
5. La décision finale (GO/ITÉRATION/STOP) s'affiche automatiquement

**Avantages vs version simple** :
- ✅ Réponses de référence disponibles directement
- ✅ Notation structurée sur 3 critères (pas besoin du système "tribunal")
- ✅ Métriques calculées en temps réel
- ✅ Décision finale automatique
- ✅ Historique complet des tests dans un seul fichier

---

## 🔄 RÉGÉNÉRATION

Si vous devez régénérer ces fichiers (par exemple, pour sélectionner d'autres documents/questions) :

```bash
# Régénérer le fichier Phase 1
python scripts/validation/generate_validation_metadonnees.py

# Régénérer le fichier Phase 2
python scripts/validation/generate_validation_dataset.py

# Régénérer le fichier Phase 3 (version simple)
python scripts/validation/generate_liste_questions_test.py

# Régénérer le fichier Phase 3 (version enrichie) ⭐ RECOMMANDÉ
python scripts/validation/generate_suivi_tests_enrichi.py
```

---

## 📋 WORKFLOW COMPLET

### Phase 1 (Semaine 1, Lundi)

1. **Préparation** (Chef de projet - 1h)
   - Le fichier `validation_metadonnees_20docs.xlsx` est déjà prêt
   - Préparer les PDFs des 20 documents

2. **Session de validation** (Expert + Chef projet - 2h)
   - Ouvrir le fichier Excel
   - Valider les 20 documents (5-6 min par doc)
   - Sauvegarder sous `validation_metadonnees_20docs_VALIDEE.xlsx`

3. **Intégration** (Chef de projet - 2h)
   - Exécuter le script d'intégration (à venir)
   - Mettre à jour les fichiers `.metadata.json`

---

### Phase 2 (Semaine 1, Mercredi)

1. **Préparation** (Chef de projet - 1h)
   - Le fichier `validation_dataset_20questions.xlsx` est déjà prêt
   - Préparer les liens vers les documents sources

2. **Session de validation** (Experts + Chef projet - 1h30)
   - Ouvrir le fichier Excel
   - Valider les 20 questions (3-4 min par question)
   - Sauvegarder sous `validation_dataset_20questions_VALIDEE.xlsx`

3. **Intégration** (Chef de projet - 2h)
   - Exécuter le script d'intégration (à venir)
   - Générer le dataset final JSON

---

### Phase 3 (Semaine 2, Mercredi)

**Option A : Version simple (avec système "tribunal")**

1. **Préparation** (Chef de projet - 30 min)
   - Le fichier `liste_questions_a_tester.xlsx` est déjà prêt
   - Vérifier que le chatbot est accessible
   - Vérifier que le système "tribunal" fonctionne

2. **Session de tests** (2-3 Experts + Chef projet - 1h30)
   - Utiliser le fichier Excel comme guide
   - Tester chaque question dans le chatbot
   - Donner les feedbacks via le système "tribunal"
   - Cocher "Testée" dans l'Excel

3. **Extraction et analyse** (Chef de projet - 3h)
   - Extraire les feedbacks du système "tribunal"
   - Générer le rapport d'évaluation

**Option B : Version enrichie (recommandée) ⭐**

1. **Préparation** (Chef de projet - 30 min)
   - Le fichier `suivi_tests_chatbot.xlsx` est déjà prêt
   - Vérifier que le chatbot est accessible
   - Imprimer les critères d'évaluation pour les experts

2. **Session de tests** (2-3 Experts + Chef projet - 1h30)
   - Ouvrir le fichier `suivi_tests_chatbot.xlsx`
   - Pour chaque question :
     * Poser la question au chatbot
     * Copier-coller la réponse dans le fichier
     * Noter sur les 3 critères (/3 chacun)
     * Comparer avec la réponse de référence
   - Les métriques se calculent automatiquement

3. **Analyse** (Chef de projet - 30 min)
   - Consulter l'onglet "Synthese"
   - Lire la décision finale automatique
   - Préparer les recommandations si nécessaire

---

## ✅ AVANTAGES

**Gain de temps** :
- Plus besoin d'attendre le développement des scripts
- Fichiers prêts à ouvrir et à utiliser
- Sélection automatique selon les critères méthodologiques

**Qualité** :
- Sélection intelligente des 20 documents/questions
- Respect strict de la répartition méthodologique
- Données pré-remplies pour faciliter la validation

**Flexibilité** :
- Régénération facile si besoin
- Scripts Python disponibles pour personnalisation

---

## 📞 SUPPORT

**Questions** :
- Consulter `docs/guides/GUIDE_CHEF_DE_PROJET.md`
- Consulter `docs/guides/GUIDE_EXPERT_METIER.md`

**Problèmes techniques** :
- Vérifier l'installation : `python scripts/validation/verify_setup.py`
- Consulter `docs/COMMANDES_UTILES.md`

---

**Ces fichiers sont prêts à l'emploi. Bon courage pour les sessions de validation ! 🚀**
