# COMMANDES UTILES - SYSTÈME DE VALIDATION

**Référence rapide des commandes pour le système de validation du chatbot**

---

## 🔍 VÉRIFICATION DU SYSTÈME

### Vérifier que tout est en place

```bash
python scripts/validation/verify_setup.py
```

**Ce que ça fait** : Vérifie que tous les fichiers, dossiers et dépendances sont présents.

**Résultat attendu** : `🎉 Tous les fichiers critiques sont en place !`

---

## 📊 GÉNÉRATION DES TEMPLATES EXCEL

### Générer tous les templates

```bash
python scripts/validation/create_template_validation_metadonnees.py
python scripts/validation/create_template_validation_dataset.py
python scripts/validation/create_template_liste_questions_test.py
```

### Générer un template vers un emplacement spécifique

```bash
python scripts/validation/create_template_validation_metadonnees.py output/custom_name.xlsx
```

---

## 📦 INSTALLATION DES DÉPENDANCES

### Installer les dépendances Python

```bash
pip install -r requirements_validation.txt
```

### Vérifier les dépendances installées

```bash
pip list | grep -E "openpyxl|pandas|pyyaml"
```

---

## 📄 CONSULTATION DES DOCUMENTS

### Ouvrir un template Excel

**Sur Mac** :
```bash
open templates/validation_metadonnees_20docs_TEMPLATE.xlsx
```

**Sur Windows** :
```bash
start templates\validation_metadonnees_20docs_TEMPLATE.xlsx
```

**Sur Linux** :
```bash
xdg-open templates/validation_metadonnees_20docs_TEMPLATE.xlsx
```

### Lire un guide en Markdown (depuis le terminal)

```bash
# Avec cat
cat docs/guides/GUIDE_CHEF_DE_PROJET.md

# Avec less (défilement)
less docs/guides/GUIDE_CHEF_DE_PROJET.md

# Avec bat (si installé, avec coloration syntaxique)
bat docs/guides/GUIDE_CHEF_DE_PROJET.md
```

---

## 🔧 COMMANDES DE DÉVELOPPEMENT (Phase 2)

### Structure attendue des commandes pour les scripts à venir

**Génération des fichiers de validation** :

```bash
# Phase 1 - Métadonnées
python scripts/validation/generate_validation_metadonnees.py

# Phase 2 - Dataset
python scripts/validation/generate_validation_dataset.py \
  --input tests/datasets/chatbot_test_dataset.json \
  --output output/validation_dataset_20questions.xlsx
```

**Intégration des corrections** :

```bash
# Phase 1 - Métadonnées
python scripts/validation/integrate_validated_metadonnees.py \
  --input output/validation_metadonnees_20docs_VALIDEE.xlsx \
  --output-dir _metadata/documents/

# Phase 2 - Dataset
python scripts/validation/integrate_validated_dataset.py \
  --input output/validation_dataset_20questions_VALIDEE.xlsx \
  --output tests/datasets/dataset_test_final_20questions.json
```

**Extraction et rapports** :

```bash
# Extraction des feedbacks tribunal
python scripts/validation/extract_tribunal_feedbacks.py \
  --output output/feedbacks_tribunal.csv

# Génération du rapport d'évaluation
python scripts/validation/generate_evaluation_report.py \
  --feedbacks output/feedbacks_tribunal.csv \
  --dataset tests/datasets/dataset_test_final_20questions.json \
  --output output/rapport_evaluation_chatbot.txt
```

---

## 📂 NAVIGATION DANS LES FICHIERS

### Afficher la structure du projet

```bash
tree -L 3 -I '__pycache__|*.pyc|.git' .
```

### Lister les templates Excel

```bash
ls -lh templates/
```

### Lister les scripts de validation

```bash
ls -lh scripts/validation/
```

### Compter les fichiers de métadonnées

```bash
ls -1 _metadata/documents/*.metadata.json | wc -l
```

---

## 🔍 RECHERCHE DANS LES FICHIERS

### Rechercher dans la documentation

```bash
# Rechercher un terme dans tous les guides
grep -r "validation" docs/guides/

# Rechercher dans un guide spécifique
grep -i "excel" docs/guides/GUIDE_CHEF_DE_PROJET.md
```

### Vérifier le contenu d'un fichier JSON

```bash
# Afficher un fichier metadata
cat _metadata/documents/rpn_pj_rpn_commentaire.metadata.json | head -30

# Vérifier la syntaxe JSON
python -m json.tool _metadata/documents/rpn_pj_rpn_commentaire.metadata.json > /dev/null
```

---

## 🧪 TESTS ET VALIDATION

### Exécuter les tests unitaires (quand ils seront créés)

```bash
pytest tests/test_validation_scripts.py -v
```

### Valider la syntaxe Python

```bash
python -m py_compile scripts/validation/*.py
```

### Linter le code (si flake8 installé)

```bash
flake8 scripts/validation/ --max-line-length=120
```

---

## 📊 STATISTIQUES

### Compter les lignes de code

```bash
# Documentation
wc -l docs/**/*.md

# Scripts Python
wc -l scripts/validation/*.py
```

### Taille des fichiers

```bash
# Taille des templates Excel
du -h templates/

# Taille totale du projet
du -sh .
```

---

## 🗄️ GESTION DES FICHIERS

### Créer une sauvegarde

```bash
# Sauvegarder les templates
cp -r templates/ templates_backup_$(date +%Y%m%d)/

# Sauvegarder les métadonnées
cp -r _metadata/ _metadata_backup_$(date +%Y%m%d)/
```

### Nettoyer les fichiers temporaires

```bash
# Supprimer les fichiers Python compilés
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete

# Supprimer les fichiers Excel temporaires
rm -f templates/~$*.xlsx
```

---

## 🔄 WORKFLOW COMPLET (Phase 1 - Métadonnées)

### Séquence complète pour Phase 1

```bash
# 1. Vérifier le système
python scripts/validation/verify_setup.py

# 2. Générer le fichier Excel de validation (à venir)
python scripts/validation/generate_validation_metadonnees.py

# 3. Le chef de projet et l'expert remplissent le fichier Excel
# (manuel)

# 4. Intégrer les corrections (à venir)
python scripts/validation/integrate_validated_metadonnees.py \
  --input output/validation_metadonnees_20docs_VALIDEE.xlsx

# 5. Vérifier les mises à jour
git diff _metadata/documents/
```

---

## 🔄 WORKFLOW COMPLET (Phase 2 - Dataset)

### Séquence complète pour Phase 2

```bash
# 1. Générer le fichier Excel de validation (à venir)
python scripts/validation/generate_validation_dataset.py

# 2. Le chef de projet et l'expert remplissent le fichier Excel
# (manuel)

# 3. Intégrer les corrections (à venir)
python scripts/validation/integrate_validated_dataset.py \
  --input output/validation_dataset_20questions_VALIDEE.xlsx

# 4. Vérifier le dataset final
cat tests/datasets/dataset_test_final_20questions.json | python -m json.tool
```

---

## 🔄 WORKFLOW COMPLET (Phase 3 - Tests)

### Séquence complète pour Phase 3

```bash
# 1. Générer la liste des questions (à venir)
python scripts/validation/generate_liste_questions_test.py

# 2. Les experts testent le chatbot
# (manuel - utilisation de l'interface web + système tribunal)

# 3. Extraire les feedbacks (à venir)
python scripts/validation/extract_tribunal_feedbacks.py

# 4. Générer le rapport (à venir)
python scripts/validation/generate_evaluation_report.py

# 5. Consulter le rapport
cat output/rapport_evaluation_chatbot.txt
```

---

## 📝 RACCOURCIS UTILES

### Alias à ajouter dans votre .bashrc ou .zshrc

```bash
# Alias pour vérifier le système
alias check-validation='python scripts/validation/verify_setup.py'

# Alias pour régénérer tous les templates
alias regen-templates='python scripts/validation/create_template_validation_metadonnees.py && python scripts/validation/create_template_validation_dataset.py && python scripts/validation/create_template_liste_questions_test.py'

# Alias pour ouvrir les guides
alias guide-chef='open docs/guides/GUIDE_CHEF_DE_PROJET.md'
alias guide-expert='open docs/guides/GUIDE_EXPERT_METIER.md'
```

---

## 🆘 COMMANDES DE DÉPANNAGE

### Le script Python ne s'exécute pas

```bash
# Vérifier la version de Python
python --version

# Vérifier les permissions
chmod +x scripts/validation/*.py

# Exécuter avec python3 explicitement
python3 scripts/validation/verify_setup.py
```

### Problème avec openpyxl

```bash
# Réinstaller openpyxl
pip uninstall openpyxl
pip install openpyxl>=3.1.2
```

### Les templates Excel ne s'ouvrent pas

```bash
# Vérifier que le fichier existe
ls -lh templates/validation_metadonnees_20docs_TEMPLATE.xlsx

# Régénérer le template
python scripts/validation/create_template_validation_metadonnees.py
```

---

## 📚 RESSOURCES RAPIDES

### Afficher les guides disponibles

```bash
ls -lh docs/guides/
```

### Afficher le README principal

```bash
cat DEMARRAGE_RAPIDE_VALIDATION.md
```

### Afficher la méthodologie

```bash
less _INSTRUCTIONS/METHODOLOGIE_TEST_ASSURANCE_QUALITE.md
```

---

**Ajoutez cette page à vos favoris pour un accès rapide !**
