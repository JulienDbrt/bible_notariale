#!/usr/bin/env python3
"""
RAPPORT DE QUALITÉ - ANALYSE DES ÉVALUATIONS
Analyse la corrélation entre le nombre de sources utilisées et la satisfaction utilisateur.

Usage:
    python scripts/benchmark_quality_report.py
    python scripts/benchmark_quality_report.py --start-date 2025-09-07 --end-date 2025-10-21
    python scripts/benchmark_quality_report.py --format json
    python scripts/benchmark_quality_report.py --export report.csv
"""

import os
import sys
import argparse
import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
from dotenv import load_dotenv

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import get_supabase

# Configuration des couleurs pour le terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class QualityReportGenerator:
    """Générateur de rapports de qualité basés sur les évaluations."""

    def __init__(self):
        load_dotenv()
        self.supabase = get_supabase()

    def fetch_evaluations(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Récupère les évaluations depuis Supabase pour une période donnée.

        Args:
            start_date: Date de début (format: YYYY-MM-DD)
            end_date: Date de fin (format: YYYY-MM-DD)

        Returns:
            Liste des évaluations
        """
        try:
            query = self.supabase.table("evaluations").select(
                "id, feedback, sources, created_at, question, response, comment"
            )

            # Filtres de date si fournis
            if start_date:
                query = query.gte("created_at", f"{start_date}T00:00:00")
            if end_date:
                query = query.lte("created_at", f"{end_date}T23:59:59")

            result = query.order("created_at", desc=False).execute()

            if not result.data:
                print(f"{Colors.WARNING}⚠️  Aucune évaluation trouvée pour la période spécifiée.{Colors.ENDC}")
                return []

            print(f"{Colors.OKGREEN}✅ {len(result.data)} évaluations récupérées.{Colors.ENDC}")
            return result.data

        except Exception as e:
            print(f"{Colors.FAIL}❌ Erreur lors de la récupération des évaluations: {e}{Colors.ENDC}")
            return []

    def categorize_sources(self, sources: Any) -> str:
        """
        Catégorise le nombre de sources.

        Args:
            sources: Liste des sources (JSONB array ou None)

        Returns:
            Catégorie sous forme de string
        """
        if sources is None or not isinstance(sources, list):
            return "0 source"

        nb_sources = len(sources)

        if nb_sources == 0:
            return "0 source"
        elif nb_sources == 1:
            return "1 source"
        elif 2 <= nb_sources <= 3:
            return "2-3 sources"
        elif 4 <= nb_sources <= 5:
            return "4-5 sources"
        else:
            return "6+ sources"

    def analyze_data(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyse les données d'évaluation et génère les statistiques.

        Args:
            evaluations: Liste des évaluations

        Returns:
            Dictionnaire avec les statistiques par catégorie
        """
        # Initialisation des catégories
        categories = ["0 source", "1 source", "2-3 sources", "4-5 sources", "6+ sources"]
        stats = {cat: {"total": 0, "positive": 0, "negative": 0} for cat in categories}

        # Comptage par catégorie
        for eval_data in evaluations:
            category = self.categorize_sources(eval_data.get("sources"))
            feedback = eval_data.get("feedback", "").lower()

            stats[category]["total"] += 1
            if feedback == "positive":
                stats[category]["positive"] += 1
            elif feedback == "negative":
                stats[category]["negative"] += 1

        # Calcul des pourcentages et qualité
        total_evaluations = len(evaluations)
        results = []

        for category in categories:
            data = stats[category]
            if data["total"] == 0:
                continue

            pct_du_total = round((data["total"] / total_evaluations) * 100, 1)
            taux_satisfaction = round((data["positive"] / data["total"]) * 100, 1) if data["total"] > 0 else 0

            # Indicateur qualité
            if taux_satisfaction >= 80:
                qualite = "✅ Excellent"
            elif taux_satisfaction >= 60:
                qualite = "⚠️  Moyen"
            else:
                qualite = "❌ Faible"

            results.append({
                "nb_sources_categorie": category,
                "nb_reponses": data["total"],
                "pct_du_total": pct_du_total,
                "positives": data["positive"],
                "negatives": data["negative"],
                "taux_satisfaction_pct": taux_satisfaction,
                "qualite": qualite
            })

        return {
            "period": {
                "total_evaluations": total_evaluations,
                "positive_total": sum(r["positives"] for r in results),
                "negative_total": sum(r["negatives"] for r in results),
            },
            "by_category": results
        }

    def print_report(self, analysis: Dict[str, Any], start_date: str, end_date: str):
        """
        Affiche le rapport dans le terminal de manière formatée.

        Args:
            analysis: Résultats de l'analyse
            start_date: Date de début
            end_date: Date de fin
        """
        print("\n" + "="*100)
        print(f"{Colors.HEADER}{Colors.BOLD}📊 RAPPORT DE QUALITÉ - ANALYSE DES SOURCES{Colors.ENDC}")
        print("="*100)
        print(f"{Colors.OKCYAN}📅 Période analysée: {start_date} → {end_date}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}📈 Total évaluations: {analysis['period']['total_evaluations']}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}   ✓ Positives: {analysis['period']['positive_total']}{Colors.ENDC}")
        print(f"{Colors.FAIL}   ✗ Négatives: {analysis['period']['negative_total']}{Colors.ENDC}")
        print("="*100 + "\n")

        # En-têtes du tableau
        headers = [
            "Nb Sources",
            "Réponses",
            "% Total",
            "Positives",
            "Négatives",
            "Satisfaction %",
            "Qualité"
        ]

        # Calcul des largeurs de colonnes
        col_widths = [15, 10, 10, 10, 10, 15, 15]

        # Affichage de l'en-tête
        header_line = "│ " + " │ ".join(
            h.ljust(w) for h, w in zip(headers, col_widths)
        ) + " │"
        separator = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
        top_border = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
        bottom_border = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

        print(top_border)
        print(header_line)
        print(separator)

        # Affichage des données
        for row in analysis["by_category"]:
            values = [
                row["nb_sources_categorie"],
                str(row["nb_reponses"]),
                f"{row['pct_du_total']}%",
                str(row["positives"]),
                str(row["negatives"]),
                f"{row['taux_satisfaction_pct']}%",
                row["qualite"]
            ]

            # Colorisation basée sur la qualité
            if "Excellent" in row["qualite"]:
                color = Colors.OKGREEN
            elif "Moyen" in row["qualite"]:
                color = Colors.WARNING
            else:
                color = Colors.FAIL

            data_line = "│ " + " │ ".join(
                v.ljust(w) for v, w in zip(values, col_widths)
            ) + " │"
            print(f"{color}{data_line}{Colors.ENDC}")

        print(bottom_border)
        print()

        # Insights supplémentaires
        self._print_insights(analysis)

    def _print_insights(self, analysis: Dict[str, Any]):
        """Affiche des insights supplémentaires basés sur l'analyse."""
        print(f"{Colors.HEADER}{Colors.BOLD}💡 INSIGHTS CLÉS{Colors.ENDC}")
        print("─" * 100)

        by_cat = analysis["by_category"]
        if not by_cat:
            print("Aucune donnée à analyser.")
            return

        # Meilleure catégorie
        best = max(by_cat, key=lambda x: x["taux_satisfaction_pct"])
        print(f"{Colors.OKGREEN}✓ Meilleure performance: {best['nb_sources_categorie']} "
              f"({best['taux_satisfaction_pct']}% de satisfaction){Colors.ENDC}")

        # Pire catégorie
        worst = min(by_cat, key=lambda x: x["taux_satisfaction_pct"])
        print(f"{Colors.FAIL}✗ Performance à améliorer: {worst['nb_sources_categorie']} "
              f"({worst['taux_satisfaction_pct']}% de satisfaction){Colors.ENDC}")

        # Catégorie la plus fréquente
        most_frequent = max(by_cat, key=lambda x: x["nb_reponses"])
        print(f"{Colors.OKBLUE}📊 Configuration la plus fréquente: {most_frequent['nb_sources_categorie']} "
              f"({most_frequent['nb_reponses']} réponses, {most_frequent['pct_du_total']}%){Colors.ENDC}")

        # Taux de satisfaction global
        total_positive = sum(r["positives"] for r in by_cat)
        total_responses = sum(r["nb_reponses"] for r in by_cat)
        global_satisfaction = round((total_positive / total_responses) * 100, 1) if total_responses > 0 else 0

        print(f"\n{Colors.BOLD}📈 Taux de satisfaction global: {global_satisfaction}%{Colors.ENDC}")
        print("─" * 100 + "\n")

    def export_to_csv(self, analysis: Dict[str, Any], filename: str):
        """
        Exporte les résultats au format CSV.

        Args:
            analysis: Résultats de l'analyse
            filename: Nom du fichier de sortie
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "nb_sources_categorie",
                    "nb_reponses",
                    "pct_du_total",
                    "positives",
                    "negatives",
                    "taux_satisfaction_pct",
                    "qualite"
                ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for row in analysis["by_category"]:
                    writer.writerow(row)

            print(f"{Colors.OKGREEN}✅ Rapport exporté vers: {filename}{Colors.ENDC}")

        except Exception as e:
            print(f"{Colors.FAIL}❌ Erreur lors de l'export CSV: {e}{Colors.ENDC}")

    def export_to_json(self, analysis: Dict[str, Any], filename: str):
        """
        Exporte les résultats au format JSON.

        Args:
            analysis: Résultats de l'analyse
            filename: Nom du fichier de sortie
        """
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(analysis, jsonfile, indent=2, ensure_ascii=False)

            print(f"{Colors.OKGREEN}✅ Rapport exporté vers: {filename}{Colors.ENDC}")

        except Exception as e:
            print(f"{Colors.FAIL}❌ Erreur lors de l'export JSON: {e}{Colors.ENDC}")


def main():
    """Point d'entrée principal du script."""
    parser = argparse.ArgumentParser(
        description="Génère un rapport de qualité basé sur les évaluations collectées.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python scripts/benchmark_quality_report.py
  python scripts/benchmark_quality_report.py --start-date 2025-09-07 --end-date 2025-10-21
  python scripts/benchmark_quality_report.py --format json --export report.json
  python scripts/benchmark_quality_report.py --last-days 30
        """
    )

    parser.add_argument(
        '--start-date',
        type=str,
        help='Date de début (format: YYYY-MM-DD)'
    )

    parser.add_argument(
        '--end-date',
        type=str,
        help='Date de fin (format: YYYY-MM-DD)'
    )

    parser.add_argument(
        '--last-days',
        type=int,
        help='Analyser les N derniers jours (ex: --last-days 30)'
    )

    parser.add_argument(
        '--format',
        type=str,
        choices=['table', 'json', 'both'],
        default='table',
        help='Format de sortie (défaut: table)'
    )

    parser.add_argument(
        '--export',
        type=str,
        help='Exporter vers un fichier (CSV ou JSON selon l\'extension)'
    )

    args = parser.parse_args()

    # Détermination des dates
    if args.last_days:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=args.last_days)).strftime('%Y-%m-%d')
    else:
        start_date = args.start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = args.end_date or datetime.now().strftime('%Y-%m-%d')

    # Génération du rapport
    print(f"\n{Colors.BOLD}🔍 Génération du rapport de qualité...{Colors.ENDC}\n")

    generator = QualityReportGenerator()
    evaluations = generator.fetch_evaluations(start_date, end_date)

    if not evaluations:
        print(f"{Colors.WARNING}⚠️  Aucune donnée à analyser. Vérifiez la période ou la base de données.{Colors.ENDC}")
        return

    analysis = generator.analyze_data(evaluations)

    # Affichage selon le format demandé
    if args.format in ['table', 'both']:
        generator.print_report(analysis, start_date, end_date)

    if args.format in ['json', 'both']:
        print(json.dumps(analysis, indent=2, ensure_ascii=False))

    # Export si demandé
    if args.export:
        if args.export.endswith('.csv'):
            generator.export_to_csv(analysis, args.export)
        elif args.export.endswith('.json'):
            generator.export_to_json(analysis, args.export)
        else:
            print(f"{Colors.WARNING}⚠️  Extension non reconnue. Utilisez .csv ou .json{Colors.ENDC}")


if __name__ == "__main__":
    main()
