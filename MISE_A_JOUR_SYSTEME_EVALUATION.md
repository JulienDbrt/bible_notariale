# MISE À JOUR SYSTÈME D'ÉVALUATION

**Date** : 18 novembre 2025
**Version** : 1.1

---

## CHANGEMENTS APPLIQUÉS

### 1. Nouveau système d'évaluation (3 critères)

L'ancien système de notation global (sur 5 étoiles) a été remplacé par un système à 3 critères notés sur 3 points chacun :

#### EXACTITUDE /3
- Évalue la pertinence et la complétude de la réponse
- 0/3 : Incorrecte, hors sujet ou très incomplète
- 1/3 : Partiellement correcte avec erreurs importantes
- 2/3 : Correcte mais il manque des éléments
- 3/3 : Complète, pertinente et exacte

#### SOURCES /3
- Évalue la pertinence et la complétude des sources citées
- 0/3 : Aucune source ou non pertinentes
- 1/3 : Sources partiellement pertinentes ou incomplètes
- 2/3 : Pertinentes mais il en manque
- 3/3 : Parfaites (pertinentes et complètes)

#### FORMULATION /3
- Évalue la clarté, le style notarial et la longueur
- 0/3 : Incompréhensible, trop longue ou inadaptée
- 1/3 : Peu claire ou style/longueur inadaptés
- 2/3 : Claire mais peut être améliorée
- 3/3 : Excellente (claire, professionnelle, adaptée)

**Score total** : /9 (somme des 3 critères)

---

## FICHIERS MODIFIÉS

### Documentation mise à jour

1. **docs/guides/GUIDE_EXPERT_METIER.md**
   - Section "Comment tester une question" mise à jour
   - Exemple de feedback avec le nouveau système de notation
   - Explication détaillée des 3 critères

2. **docs/guides/GUIDE_CHEF_DE_PROJET.md**
   - Instructions pour les experts mises à jour
   - Colonnes CSV mises à jour :
     * `exactitude_score` (0-3)
     * `sources_score` (0-3)
     * `formulation_score` (0-3)
     * `score_total` (0-9)
   - Grille de décision finale mise à jour (score ≥ 6/9)

3. **docs/VALIDATION_CHATBOT_README.md**
   - Objectifs quantitatifs mis à jour
   - Phase 3 - Résultats attendus : score moyen ≥ 6/9

4. **DEMARRAGE_RAPIDE_VALIDATION.md**
   - Métriques de succès mises à jour
   - Information sur les fichiers pré-générés ajoutée
   - Scripts de génération marqués comme complétés

---

## NOUVEAUX OBJECTIFS QUANTITATIFS

| Métrique | Ancien objectif | Nouvel objectif |
|----------|----------------|-----------------|
| Documents métadonnées validés | ≥ 15/20 (75%) | ≥ 15/20 (75%) ✓ |
| Questions dataset validées | ≥ 16/20 (80%) | ≥ 16/20 (80%) ✓ |
| Tests chatbot réussis | ≥ 16/20 (80%) | ≥ 16/20 (80%) ✓ |
| Score moyen chatbot | ≥ 3.5/5 | **≥ 6/9 (67%)** ⭐ |
| Hallucinations | ≤ 15% | *Critère supprimé* |

**Note** : Le critère "hallucinations" a été supprimé car il est maintenant intégré dans le critère "Exactitude".

---

## STRUCTURE CSV MISE À JOUR

### Ancien format
```
question_id, timestamp, score_global, reponse_utile, sources_correctes,
hallucinations, commentaire, testeur_id
```

### Nouveau format
```
question_id, timestamp, exactitude_score, sources_score,
formulation_score, score_total, commentaire, testeur_id
```

---

## FICHIERS EXCEL PRÉ-REMPLIS

Les 3 fichiers Excel sont **déjà générés** et disponibles dans `output/` :

1. **validation_metadonnees_20docs.xlsx** (8.9 KB)
   - 20 documents pré-sélectionnés
   - Prêt pour Phase 1

2. **validation_dataset_20questions.xlsx** (12 KB)
   - 20 questions pré-sélectionnées (répartition méthodologique)
   - Prêt pour Phase 2

3. **liste_questions_a_tester.xlsx** (6.6 KB)
   - Liste simple des 20 questions
   - Prêt pour Phase 3

---

## SCRIPTS DE GÉNÉRATION DISPONIBLES

Les scripts suivants permettent de régénérer les fichiers si nécessaire :

```bash
# Phase 1
python scripts/validation/generate_validation_metadonnees.py

# Phase 2
python scripts/validation/generate_validation_dataset.py

# Phase 3
python scripts/validation/generate_liste_questions_test.py
```

---

## IMPACT SUR LES SESSIONS DE VALIDATION

### Phase 1 : Validation métadonnées (2h)
- **Aucun changement** (pas concernée par le nouveau système d'évaluation)

### Phase 2 : Validation dataset (1h30)
- **Aucun changement** (pas concernée par le nouveau système d'évaluation)

### Phase 3 : Tests chatbot (1h30)
- **Changement majeur** : Les experts utilisent maintenant 3 critères au lieu d'un score global
- **Temps estimé par question** : Reste 4-5 minutes (pas d'impact)
- **Interface tribunal** : À mettre à jour pour refléter les 3 critères

---

## ACTIONS REQUISES

### ✅ Terminé
- [x] Mise à jour GUIDE_EXPERT_METIER.md
- [x] Mise à jour GUIDE_CHEF_DE_PROJET.md
- [x] Mise à jour VALIDATION_CHATBOT_README.md
- [x] Mise à jour DEMARRAGE_RAPIDE_VALIDATION.md
- [x] Génération des 3 fichiers Excel pré-remplis

### ⏳ À faire (si développement Phase 3 requis)
- [ ] Mettre à jour l'interface "tribunal" pour capturer les 3 scores
- [ ] Mettre à jour le script `extract_tribunal_feedbacks.py` pour le nouveau format CSV
- [ ] Mettre à jour le script `generate_evaluation_report.py` pour calculer les métriques sur 9 points

---

## COMPATIBILITÉ

### Rétrocompatibilité
- Les templates Excel générés **avant** cette mise à jour restent utilisables
- Les fichiers validés avec l'ancien système peuvent coexister avec le nouveau système
- Aucune migration de données nécessaire

### Migration
Si des données existent déjà avec l'ancien format :
```python
# Conversion score global → score total
# Ancien : score_global sur 5
# Nouveau : score_total sur 9
score_total = (score_global / 5) * 9
```

---

## RÉSUMÉ DES AVANTAGES

### Ancien système (5 étoiles)
- ✓ Simple et rapide
- ✗ Manque de granularité
- ✗ Pas de détail sur les aspects à améliorer

### Nouveau système (3 critères × 3 points)
- ✓ **Précision accrue** : Identifie exactement ce qui pose problème
- ✓ **Feedback actionnable** : Les développeurs savent quoi améliorer
- ✓ **Équilibré** : Pondération égale entre exactitude, sources, et formulation
- ✓ **Reste simple** : Seulement 3 critères à évaluer

---

## EXEMPLE COMPARATIF

### Ancien système
```
Score global : 4/5 ⭐⭐⭐⭐
Commentaire : "Bien mais peut être amélioré"
```
→ Pas clair ce qui doit être amélioré

### Nouveau système
```
Exactitude : 3/3 ✓
Sources : 2/3 (manque 1 document pertinent)
Formulation : 3/3 ✓
Score total : 8/9

Commentaire : "Réponse exacte et bien formulée, mais devrait citer aussi
le RPN article 4.2.1 qui est pertinent sur ce sujet"
```
→ Feedback clair et actionnable

---

## PROCHAINES ÉTAPES

1. **Court terme** : Utiliser les fichiers Excel générés pour les 3 sessions
2. **Moyen terme** : Développer les scripts d'intégration et de rapports
3. **Long terme** : Adapter l'interface "tribunal" si nécessaire

---

**Questions ou problèmes ?**
- Consulter les guides mis à jour dans `docs/guides/`
- Vérifier la cohérence avec `python scripts/validation/verify_setup.py`
