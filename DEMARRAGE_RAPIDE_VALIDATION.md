# DÉMARRAGE RAPIDE - SYSTÈME DE VALIDATION

**Projet** : Chatbot Bible Notariale
**Version** : 1.0
**Date** : 18 novembre 2025

---

## 🎯 VOUS ÊTES...

### Chef de projet ?
👉 **Commencez ici** : [docs/guides/GUIDE_CHEF_DE_PROJET.md](docs/guides/GUIDE_CHEF_DE_PROJET.md)

### Expert métier (notaire) ?
👉 **Commencez ici** : [docs/guides/GUIDE_EXPERT_METIER.md](docs/guides/GUIDE_EXPERT_METIER.md)

### Développeur technique ?
👉 **Lisez d'abord** : [docs/VALIDATION_CHATBOT_README.md](docs/VALIDATION_CHATBOT_README.md)

---

## ⚡ DÉMARRAGE EN 5 MINUTES

### 1. Vérifier que tout est en place

```bash
python scripts/validation/verify_setup.py
```

**Résultat attendu** : `🎉 Tous les fichiers critiques sont en place !`

---

### 2. Installer les dépendances (si nécessaire)

```bash
pip install -r requirements_validation.txt
```

---

### 3. Consulter la documentation

**Pour une vue d'ensemble complète** :
- Lire [docs/VALIDATION_CHATBOT_README.md](docs/VALIDATION_CHATBOT_README.md)

**Pour la méthodologie détaillée** :
- Lire [_INSTRUCTIONS/METHODOLOGIE_TEST_ASSURANCE_QUALITE.md](_INSTRUCTIONS/METHODOLOGIE_TEST_ASSURANCE_QUALITE.md)

---

### 4. Générer les templates Excel (déjà fait !)

Les templates sont déjà créés dans `templates/` :
- ✅ `validation_metadonnees_20docs_TEMPLATE.xlsx`
- ✅ `validation_dataset_20questions_TEMPLATE.xlsx`
- ✅ `liste_questions_a_tester_TEMPLATE.xlsx`

Pour les regénérer si nécessaire :

```bash
python scripts/validation/create_template_validation_metadonnees.py
python scripts/validation/create_template_validation_dataset.py
python scripts/validation/create_template_liste_questions_test.py
```

---

### 5. Planifier les sessions

**À organiser avec les experts métier** :

| Session | Semaine | Durée | Participants |
|---------|---------|-------|--------------|
| Validation métadonnées | S1 Lundi PM | 2h | 1 expert + chef projet |
| Validation dataset | S1 Mercredi PM | 1h30 | 1-2 experts + chef projet |
| Tests chatbot | S2 Mercredi PM | 1h30 | 2-3 experts + chef projet |
| Réunion Go/No-Go | S2 Vendredi AM | 2h | Tous + client |

**Total temps expert** : 5h sur 2 semaines

---

## 📋 CE QUI EST DÉJÀ FAIT

### ✅ Phase 1 : Documentation et Templates (COMPLÉTÉ)

- [x] Guide Chef de Projet (30 pages)
- [x] Guide Expert Métier (25 pages)
- [x] README principal avec vue d'ensemble
- [x] Template Excel validation métadonnées
- [x] Template Excel validation dataset
- [x] Template Excel liste questions test
- [x] Scripts Python de génération des templates
- [x] Script de vérification du système
- [x] Documentation des livrables

---

## ✅ FICHIERS EXCEL PRÉ-REMPLIS (DÉJÀ GÉNÉRÉS)

**Bonne nouvelle** : Les 3 fichiers Excel sont déjà générés et prêts à utiliser !

**Localisation** : `output/`
- ✅ `validation_metadonnees_20docs.xlsx` (20 documents pré-sélectionnés)
- ✅ `validation_dataset_20questions.xlsx` (20 questions pré-sélectionnées)
- ✅ `liste_questions_a_tester.xlsx` (liste simple pour tests)

**Scripts de génération disponibles** :
- ✅ `generate_validation_metadonnees.py` - Régénère l'Excel Phase 1
- ✅ `generate_validation_dataset.py` - Régénère l'Excel Phase 2
- ✅ `generate_liste_questions_test.py` - Régénère l'Excel Phase 3

**Pour régénérer si nécessaire** :
```bash
python scripts/validation/generate_validation_metadonnees.py
python scripts/validation/generate_validation_dataset.py
python scripts/validation/generate_liste_questions_test.py
```

---

## 🚧 CE QUI RESTE À FAIRE

**Scripts d'intégration** (post-validation) :
- [ ] `integrate_validated_metadonnees.py` - Applique les corrections aux .metadata.json
- [ ] `integrate_validated_dataset.py` - Génère le dataset final validé

**Scripts d'extraction et rapports** :
- [ ] `extract_tribunal_feedbacks.py` - Extrait les feedbacks de la DB
- [ ] `generate_evaluation_report.py` - Génère le rapport d'évaluation

**Utilitaires** :
- [ ] `scripts/utils/excel_helpers.py` - Fonctions pour Excel
- [ ] `scripts/utils/metadata_reader.py` - Fonctions pour métadonnées
- [ ] `scripts/utils/metrics_calculator.py` - Calcul des métriques

**Configuration** :
- [ ] `config/validation_config.yaml` - Configuration centralisée

---

## 📁 STRUCTURE DES FICHIERS

```
bible_notariale/
│
├── 📄 DEMARRAGE_RAPIDE_VALIDATION.md (ce fichier)
│
├── docs/
│   ├── guides/
│   │   ├── GUIDE_CHEF_DE_PROJET.md ⭐ Guide complet chef de projet
│   │   └── GUIDE_EXPERT_METIER.md ⭐ Guide complet expert métier
│   ├── VALIDATION_CHATBOT_README.md ⭐ Vue d'ensemble système
│   └── LIVRABLES_PHASE1.md (documentation livrables)
│
├── _INSTRUCTIONS/
│   └── METHODOLOGIE_TEST_ASSURANCE_QUALITE.md (méthodologie complète)
│
├── templates/
│   ├── validation_metadonnees_20docs_TEMPLATE.xlsx ⭐
│   ├── validation_dataset_20questions_TEMPLATE.xlsx ⭐
│   └── liste_questions_a_tester_TEMPLATE.xlsx ⭐
│
├── scripts/
│   └── validation/
│       ├── verify_setup.py ⭐ Script de vérification
│       ├── create_template_validation_metadonnees.py
│       ├── create_template_validation_dataset.py
│       └── create_template_liste_questions_test.py
│
├── _metadata/
│   └── documents/ (245 fichiers .metadata.json)
│
├── tests/
│   └── datasets/
│       └── chatbot_test_dataset.json (50 questions)
│
└── requirements_validation.txt (dépendances Python)
```

⭐ = Fichiers essentiels pour démarrer

---

## 🔍 VÉRIFICATION RAPIDE

### Tous les fichiers essentiels sont-ils présents ?

```bash
python scripts/validation/verify_setup.py
```

### Les templates Excel s'ouvrent-ils correctement ?

```bash
# Sur Mac
open templates/validation_metadonnees_20docs_TEMPLATE.xlsx

# Sur Windows
start templates/validation_metadonnees_20docs_TEMPLATE.xlsx

# Sur Linux
xdg-open templates/validation_metadonnees_20docs_TEMPLATE.xlsx
```

**Vérifier** :
- Les 2 onglets sont présents (Instructions + Validation)
- Les listes déroulantes fonctionnent
- La mise en forme est correcte

---

## 📞 SUPPORT

### Questions fréquentes

**Q : Par où commencer ?**
R : Lire le guide correspondant à votre rôle (Chef de projet ou Expert métier)

**Q : Les templates Excel sont-ils modifiables ?**
R : Oui, mais ils sont déjà configurés avec les bonnes colonnes et validations

**Q : Comment personnaliser les templates ?**
R : Modifier les scripts Python `create_template_*.py` et les regénérer

**Q : Où trouver la méthodologie complète ?**
R : `_INSTRUCTIONS/METHODOLOGIE_TEST_ASSURANCE_QUALITE.md`

---

## 🎯 PROCHAINES ACTIONS

### Pour le Chef de Projet

1. ✅ Lire [GUIDE_CHEF_DE_PROJET.md](docs/guides/GUIDE_CHEF_DE_PROJET.md)
2. ✅ Vérifier que les fichiers Excel pré-remplis sont disponibles dans `output/`
3. ⏳ Planifier les 3 sessions avec les experts métier
4. ⏳ Préparer la première session (Phase 1 - Métadonnées)

### Pour le Développeur

1. ✅ Comprendre la méthodologie
2. ✅ Explorer les templates Excel créés
3. ✅ Scripts de génération (COMPLÉTÉS)
4. ⏳ Développer les scripts d'intégration (priorité 1)
5. ⏳ Développer les scripts d'extraction et rapports (priorité 2)

### Pour l'Expert Métier

1. ✅ Lire [GUIDE_EXPERT_METIER.md](docs/guides/GUIDE_EXPERT_METIER.md)
2. ⏳ Bloquer 5h dans l'agenda sur 2 semaines
3. ⏳ Attendre la convocation du chef de projet
4. ⏳ Participer aux 3 sessions de validation

---

## ✅ CHECKLIST AVANT LA PREMIÈRE SESSION

### Chef de Projet

- [ ] J'ai lu le GUIDE_CHEF_DE_PROJET.md
- [ ] J'ai vérifié que tous les fichiers sont en place (script verify_setup.py)
- [ ] J'ai vérifié que les 3 fichiers Excel sont dans `output/`
- [ ] J'ai planifié les 3 sessions avec les experts
- [ ] J'ai préparé l'accès aux PDFs des documents

### Expert Métier

- [ ] J'ai lu le GUIDE_EXPERT_METIER.md
- [ ] J'ai bloqué les créneaux dans mon agenda
- [ ] Je comprends mon rôle dans chaque session
- [ ] Je sais que la session 1 dure 2h, session 2 dure 1h30, session 3 dure 1h30

---

## 📊 MÉTRIQUES DE SUCCÈS

### Objectifs à atteindre

| Critère | Objectif |
|---------|----------|
| Documents métadonnées validés | ≥ 15/20 (75%) |
| Questions dataset validées | ≥ 16/20 (80%) |
| Tests chatbot réussis | ≥ 16/20 (80%) |
| Score moyen chatbot | ≥ 6/9 (67%) |
| Temps expert total | ≤ 6h |

### Si les objectifs ne sont pas atteints

- **15-20 docs validés** : ✅ On continue
- **10-14 docs validés** : ⚠️ On corrige et on re-valide
- **< 10 docs validés** : ❌ On revoit la stratégie

---

## 🎉 CONCLUSION

**Vous avez tout ce qu'il faut pour démarrer !**

- ✅ Documentation complète et opérationnelle
- ✅ Templates Excel prêts à l'emploi
- ✅ Fichiers Excel pré-remplis (20 docs, 20 questions)
- ✅ Scripts de génération opérationnels
- ✅ Méthodologie claire et pragmatique
- ✅ Guides utilisateurs détaillés

**Il ne manque que** :
- Les scripts d'intégration et de rapports (post-validation)
- La planification des sessions avec les experts

**Bon courage ! 🚀**

---

**Questions ou problèmes ?**
- Consulter la FAQ dans les guides
- Vérifier la méthodologie complète
- Contacter le chef de projet technique
