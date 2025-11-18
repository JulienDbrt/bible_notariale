#!/usr/bin/env python3
"""
Script de vérification du système de validation.
Vérifie que tous les fichiers nécessaires sont présents et fonctionnels.
"""

import sys
from pathlib import Path
from typing import List, Tuple


def check_file_exists(filepath: Path, description: str) -> Tuple[bool, str]:
    """Vérifie qu'un fichier existe."""
    if filepath.exists():
        return True, f"✅ {description}"
    else:
        return False, f"❌ {description} - MANQUANT: {filepath}"


def check_directory_exists(dirpath: Path, description: str) -> Tuple[bool, str]:
    """Vérifie qu'un répertoire existe."""
    if dirpath.exists() and dirpath.is_dir():
        return True, f"✅ {description}"
    else:
        return False, f"❌ {description} - MANQUANT: {dirpath}"


def main():
    """Vérifie la configuration du système de validation."""

    print("=" * 70)
    print("VÉRIFICATION DU SYSTÈME DE VALIDATION - CHATBOT BIBLE NOTARIALE")
    print("=" * 70)
    print()

    # Trouver la racine du projet
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    print(f"📁 Répertoire du projet : {project_root}")
    print()

    results: List[Tuple[bool, str]] = []

    # Vérification de la structure des dossiers
    print("📂 STRUCTURE DES DOSSIERS")
    print("-" * 70)

    results.append(check_directory_exists(
        project_root / "docs" / "guides",
        "Dossier documentation guides"
    ))

    results.append(check_directory_exists(
        project_root / "scripts" / "validation",
        "Dossier scripts validation"
    ))

    results.append(check_directory_exists(
        project_root / "templates",
        "Dossier templates Excel"
    ))

    results.append(check_directory_exists(
        project_root / "_metadata" / "documents",
        "Dossier métadonnées documents"
    ))

    results.append(check_directory_exists(
        project_root / "tests" / "datasets",
        "Dossier datasets de test"
    ))

    for success, message in results[-5:]:
        print(message)

    print()

    # Vérification de la documentation
    print("📚 DOCUMENTATION")
    print("-" * 70)

    results.append(check_file_exists(
        project_root / "docs" / "guides" / "GUIDE_CHEF_DE_PROJET.md",
        "Guide Chef de Projet"
    ))

    results.append(check_file_exists(
        project_root / "docs" / "guides" / "GUIDE_EXPERT_METIER.md",
        "Guide Expert Métier"
    ))

    results.append(check_file_exists(
        project_root / "docs" / "VALIDATION_CHATBOT_README.md",
        "README principal"
    ))

    results.append(check_file_exists(
        project_root / "_INSTRUCTIONS" / "METHODOLOGIE_TEST_ASSURANCE_QUALITE.md",
        "Méthodologie complète"
    ))

    for success, message in results[-4:]:
        print(message)

    print()

    # Vérification des templates Excel
    print("📊 TEMPLATES EXCEL")
    print("-" * 70)

    results.append(check_file_exists(
        project_root / "templates" / "validation_metadonnees_20docs_TEMPLATE.xlsx",
        "Template validation métadonnées"
    ))

    results.append(check_file_exists(
        project_root / "templates" / "validation_dataset_20questions_TEMPLATE.xlsx",
        "Template validation dataset"
    ))

    results.append(check_file_exists(
        project_root / "templates" / "liste_questions_a_tester_TEMPLATE.xlsx",
        "Template liste questions test"
    ))

    for success, message in results[-3:]:
        print(message)

    print()

    # Vérification des scripts Python
    print("🐍 SCRIPTS PYTHON")
    print("-" * 70)

    results.append(check_file_exists(
        project_root / "scripts" / "validation" / "create_template_validation_metadonnees.py",
        "Script création template métadonnées"
    ))

    results.append(check_file_exists(
        project_root / "scripts" / "validation" / "create_template_validation_dataset.py",
        "Script création template dataset"
    ))

    results.append(check_file_exists(
        project_root / "scripts" / "validation" / "create_template_liste_questions_test.py",
        "Script création template liste questions"
    ))

    for success, message in results[-3:]:
        print(message)

    print()

    # Vérification des dépendances
    print("📦 DÉPENDANCES PYTHON")
    print("-" * 70)

    try:
        import openpyxl
        results.append((True, f"✅ openpyxl installé (version {openpyxl.__version__})"))
    except ImportError:
        results.append((False, "❌ openpyxl non installé - Exécutez: pip install openpyxl"))

    try:
        import pandas
        results.append((True, f"✅ pandas installé (version {pandas.__version__})"))
    except ImportError:
        results.append((False, "⚠️  pandas non installé (optionnel pour l'instant)"))

    try:
        import yaml
        results.append((True, "✅ pyyaml installé"))
    except ImportError:
        results.append((False, "⚠️  pyyaml non installé (optionnel pour l'instant)"))

    for success, message in results[-3:]:
        print(message)

    print()

    # Vérification des données sources
    print("📄 DONNÉES SOURCES")
    print("-" * 70)

    metadata_dir = project_root / "_metadata" / "documents"
    if metadata_dir.exists():
        metadata_files = list(metadata_dir.glob("*.metadata.json"))
        results.append((True, f"✅ {len(metadata_files)} fichiers de métadonnées trouvés"))
    else:
        results.append((False, "❌ Aucun fichier de métadonnées trouvé"))

    dataset_file = project_root / "tests" / "datasets" / "chatbot_test_dataset.json"
    if dataset_file.exists():
        results.append((True, "✅ Dataset de test trouvé"))
    else:
        results.append((False, "❌ Dataset de test non trouvé"))

    for success, message in results[-2:]:
        print(message)

    print()

    # Résumé final
    print("=" * 70)
    print("RÉSUMÉ")
    print("=" * 70)

    total = len(results)
    success_count = sum(1 for success, _ in results if success)
    warning_count = sum(1 for _, msg in results if "⚠️" in msg)
    error_count = total - success_count - warning_count

    print(f"✅ Réussite : {success_count}/{total}")
    if warning_count > 0:
        print(f"⚠️  Avertissements : {warning_count}")
    if error_count > 0:
        print(f"❌ Erreurs : {error_count}")

    print()

    if error_count == 0:
        print("🎉 Tous les fichiers critiques sont en place !")
        print()
        print("PROCHAINES ÉTAPES :")
        print("1. Lire docs/guides/GUIDE_CHEF_DE_PROJET.md")
        print("2. Installer les dépendances optionnelles : pip install -r requirements_validation.txt")
        print("3. Planifier les 3 sessions de validation avec les experts")
        print("4. Développer les scripts de génération et d'intégration")
        return 0
    else:
        print("⚠️  Certains fichiers sont manquants. Vérifiez les messages ci-dessus.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
