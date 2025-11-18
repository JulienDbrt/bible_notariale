# NOUVEAU FICHIER DE SUIVI DES TESTS ⭐

**Date** : 18 novembre 2025
**Version** : 1.1

---

## RÉSUMÉ

Un nouveau fichier Excel enrichi a été créé pour la Phase 3 (tests du chatbot), inspiré du fichier de référence `BM_QA_Marianne_test20250611_BM.xlsx` mais adapté à notre système d'évaluation /9.

**Fichier** : `output/suivi_tests_chatbot.xlsx`

---

## COMPARAISON DES OPTIONS

### Option A : Version Simple
**Fichier** : `liste_questions_a_tester.xlsx`

**Avantages** :
- ✅ Simple et rapide
- ✅ Utilise le système "tribunal" existant

**Inconvénients** :
- ❌ Pas de réponse de référence disponible
- ❌ Feedbacks stockés dans la base de données (extraction nécessaire)
- ❌ Pas de métriques en temps réel
- ❌ Nécessite un script d'extraction post-session

### Option B : Version Enrichie ⭐ RECOMMANDÉE
**Fichier** : `suivi_tests_chatbot.xlsx`

**Avantages** :
- ✅ Réponses de référence disponibles directement
- ✅ Notation structurée sur 3 critères dans l'Excel
- ✅ Métriques calculées en temps réel
- ✅ Décision finale automatique (GO/ITÉRATION/STOP)
- ✅ Historique complet dans un seul fichier
- ✅ Pas besoin du système "tribunal"
- ✅ Pas besoin de script d'extraction
- ✅ Inspiré d'un fichier éprouvé (BM_QA_Marianne)

**Inconvénients** :
- ⚠️ Plus de colonnes à remplir (mais tout dans l'Excel)

---

## STRUCTURE DU FICHIER ENRICHI

### Onglet 1 : "QA_Tests"

**Colonnes** :

| Col | Nom | Description | À remplir ? |
|-----|-----|-------------|-------------|
| A | ID Test | TEST_001, TEST_002, etc. | ✅ Pré-rempli |
| B | Catégorie | Déontologie, Juridique/RH, etc. | ✅ Pré-rempli |
| C | Question | Question complète | ✅ Pré-rempli |
| D | Document Source | Documents pertinents | ✅ Pré-rempli |
| E | Date Test | Date du test | ⏳ À remplir |
| F | Réponse Obtenue | Réponse du chatbot | ⏳ À copier-coller |
| G | Exactitude /3 | Pertinence + Complétude | ⏳ À noter |
| H | Sources /3 | Pertinence + Complétude | ⏳ À noter |
| I | Formulation /3 | Clarté + Style + Longueur | ⏳ À noter |
| J | TOTAL /9 | Somme des 3 scores | ⚙️ Automatique |
| K | Status | ✅ Réussi ou ❌ Échec | ⚙️ Automatique |
| L | Notes | Commentaires libres | ⏳ Optionnel |
| M | Réponse de Référence | Réponse attendue | ✅ Pré-rempli |

**Calculs automatiques** :
- Colonne J : `=SUM(G:I)` → Score total /9
- Colonne K : `=IF(J>=6,"✅ Réussi","❌ Échec")` → Status

**Mise en forme** :
- Colonnes G, H, I : Fond jaune (à remplir)
- En-têtes : Bleu foncé avec explications
- Lignes : Hauteur ajustée pour texte long
- Volets figés sur les en-têtes

### Onglet 2 : "Synthese"

**Métriques calculées automatiquement** :

| Métrique | Formule | Objectif |
|----------|---------|----------|
| Total Tests | Compte le nombre de tests | 20 |
| Tests Exécutés | Compte les tests avec status | 20 |
| Réussis (≥6/9) | Compte les ✅ | ≥16 (80%) |
| Échecs (<6/9) | Compte les ❌ | ≤4 (20%) |
| Score Moyen | Moyenne des scores totaux | ≥6/9 |
| % Réussite | (Réussis / Total) × 100 | ≥80% |
| Score Moyen Exactitude | Moyenne colonne G | /3 |
| Score Moyen Sources | Moyenne colonne H | /3 |
| Score Moyen Formulation | Moyenne colonne I | /3 |

**Décision finale automatique** :
```
SI % Réussite ≥ 80% → "✅ GO PHASE 2 : Déploiement élargi"
SI % Réussite ≥ 60% → "⚠️ ITÉRATION : Corrections ciblées + re-tests"
SI % Réussite < 60% → "❌ STOP : Revoir l'architecture"
```

---

## WORKFLOW D'UTILISATION

### Préparation (Chef de projet - 30 min)

1. Vérifier que le fichier `output/suivi_tests_chatbot.xlsx` existe
2. Vérifier que le chatbot est accessible (URL de test)
3. Imprimer ou projeter les critères d'évaluation :
   ```
   EXACTITUDE /3 : Pertinence + Complétude de la réponse
   SOURCES /3 : Pertinence + Complétude des sources citées
   FORMULATION /3 : Clarté + Style notarial + Longueur adaptée
   ```

### Session de tests (2-3 Experts + Chef projet - 1h30)

**Pour chaque question (5-6 minutes par question)** :

1. **Lire** la question (colonne C)
2. **Poser** la question au chatbot via l'interface web
3. **Copier-coller** la réponse obtenue dans la colonne F
4. **Lire** la réponse de référence (colonne M)
5. **Comparer** les deux réponses
6. **Noter** sur les 3 critères :
   - Colonne G : Exactitude /3
   - Colonne H : Sources /3
   - Colonne I : Formulation /3
7. **Ajouter** des commentaires si nécessaire (colonne L)
8. **Observer** le score total et le status (colonnes J et K)

**Répartition du travail** :
- Expert 1 : Questions 1-7
- Expert 2 : Questions 8-14
- Expert 3 : Questions 15-20
- Chef de projet : Observe et prend des notes générales

### Analyse (Chef de projet - 30 min)

1. **Ouvrir** l'onglet "Synthese"
2. **Lire** les métriques :
   - Score moyen : X/9
   - % de réussite : X%
   - Scores moyens par critère
3. **Lire** la décision finale automatique
4. **Préparer** les recommandations :
   - Si ÉCHEC : Quels sont les critères problématiques ?
   - Exactitude faible → Améliorer le prompt ou le retrieval
   - Sources faibles → Améliorer le retrieval ou le ranking
   - Formulation faible → Améliorer le prompt de génération

---

## SCRIPTS DISPONIBLES

### Génération du template
```bash
python scripts/validation/create_template_suivi_tests_enrichi.py
```

Crée le template vide dans `templates/suivi_tests_chatbot_TEMPLATE.xlsx`

### Génération du fichier pré-rempli
```bash
python scripts/validation/generate_suivi_tests_enrichi.py
```

Génère le fichier pré-rempli dans `output/suivi_tests_chatbot.xlsx` avec :
- 20 questions du dataset
- Catégories et sources pré-remplies
- Réponses de référence

---

## COMPATIBILITÉ AVEC L'EXISTANT

### Système "tribunal"
- **Peut coexister** : Le fichier enrichi n'empêche pas d'utiliser le système "tribunal"
- **Peut remplacer** : Si le fichier enrichi est utilisé, le système "tribunal" devient optionnel

### Fichier simple `liste_questions_a_tester.xlsx`
- **Complémentaire** : Peut être imprimé comme aide-mémoire
- **Remplacé** : Le fichier enrichi fait tout ce que fait le fichier simple + plus

### Scripts d'extraction
- **Non nécessaires** : Si le fichier enrichi est utilisé, pas besoin de `extract_tribunal_feedbacks.py`
- **Non nécessaires** : Si le fichier enrichi est utilisé, pas besoin de `generate_evaluation_report.py`

---

## AVANTAGES PAR RAPPORT AU FICHIER DE RÉFÉRENCE

Le fichier `BM_QA_Marianne_test20250611_BM.xlsx` utilisait un système /25 (5 sous-critères × 5 points).

Notre fichier utilise un système **simplifié /9** (3 critères × 3 points) :

| Aspect | BM_QA_Marianne | Notre système |
|--------|----------------|---------------|
| Exactitude | /5 | **/3** ✅ Plus simple |
| Sources | /5 Pertinence + /5 Complétude = /10 | **/3 global** ✅ Plus rapide |
| Formulation | /5 Clarté+Style + /5 Longueur = /10 | **/3 global** ✅ Plus rapide |
| **TOTAL** | /25 | **/9** ✅ Plus facile à interpréter |
| **Seuil réussite** | ≥20/25 (80%) | **≥6/9 (67%)** ✅ Plus accessible |

**Avantages de notre système** :
- ✅ **Plus rapide** : 3 notes au lieu de 5
- ✅ **Plus simple** : Échelle /3 au lieu de /5
- ✅ **Même précision** : Permet d'identifier les problèmes
- ✅ **Cohérent** : Suit notre méthodologie initiale

---

## RECOMMANDATIONS

### Pour la Phase 3

**Utiliser le fichier enrichi** `suivi_tests_chatbot.xlsx` car :
1. **Gain de temps** : Pas besoin d'extraction post-session
2. **Feedback immédiat** : Les métriques se calculent en temps réel
3. **Décision claire** : GO/ITÉRATION/STOP affiché automatiquement
4. **Historique complet** : Tout dans un seul fichier Excel
5. **Flexibilité** : Peut être fait sans système "tribunal"

### Pour les futures itérations

Si des tests supplémentaires sont nécessaires après la Phase 3 :
1. Dupliquer le fichier : `suivi_tests_chatbot_iteration2.xlsx`
2. Modifier les questions si besoin
3. Re-tester
4. Comparer les résultats entre itérations

---

## FICHIERS CRÉÉS

### Templates
- `templates/suivi_tests_chatbot_TEMPLATE.xlsx` (template vide)

### Scripts
- `scripts/validation/create_template_suivi_tests_enrichi.py` (création template)
- `scripts/validation/generate_suivi_tests_enrichi.py` (génération pré-rempli)

### Output
- `output/suivi_tests_chatbot.xlsx` ⭐ **FICHIER PRINCIPAL**

### Documentation
- `output/README.md` (mis à jour avec section sur le nouveau fichier)
- `NOUVEAU_FICHIER_SUIVI_TESTS.md` (ce document)

---

## PROCHAINES ÉTAPES

1. ✅ **Fichier créé et prêt**
2. ⏳ **Tester avec un petit échantillon** (2-3 questions)
3. ⏳ **Ajuster si nécessaire** (largeurs colonnes, formules, etc.)
4. ⏳ **Documenter dans les guides** (GUIDE_CHEF_DE_PROJET.md, GUIDE_EXPERT_METIER.md)
5. ⏳ **Planifier la session de tests** (Semaine 2, Mercredi)

---

**Le système est prêt ! Le fichier enrichi offre une solution complète et autonome pour la Phase 3. 🚀**
