"""
SpringLane Purchase Intelligence — Point d'entrée principal.

Usage:
    python main.py
    python main.py --customers 500 --months 6 --store "Paris Marais"
"""
import argparse
import os
import sys
import json
from datetime import datetime

from springlane.config import SimulationConfig
from springlane.data.simulator import run_simulation
from springlane.analytics.demographics import analyze_demographics
from springlane.analytics.purchase_behavior import analyze_purchase_behavior
from springlane.analytics.product_performance import analyze_product_performance
from springlane.analytics.basket_analysis import analyze_baskets
from springlane.analytics.time_trends import analyze_time_trends
from springlane.analytics.demand_forecast import analyze_demand_forecast
from springlane.reports.pdf_report import generate_report


def run_analytics(data: dict) -> dict:
    """
    Exécute tous les modules analytiques.
    """
    print("\n📊 Analyse en cours...")

    results = {}

    # Module 1 — Démographie
    print("  [1/6] Analyse démographique...")
    results["demographics"] = analyze_demographics(
        data["customers"], data["transactions"]
    )

    # Module 2 — Comportement d'achat
    print("  [2/6] Comportement d'achat...")
    results["behavior"] = analyze_purchase_behavior(
        data["transactions"], data["scans"], data["customers"]
    )

    # Module 3 — Performance produit
    print("  [3/6] Performance produit...")
    results["products"] = analyze_product_performance(
        data["items"], data["transactions"], data["customers"], data["stock"]
    )

    # Module 4 — Analyse de panier
    print("  [4/6] Analyse de panier...")
    results["baskets"] = analyze_baskets(
        data["items"], data["transactions"], data["customers"]
    )

    # Module 5 — Tendances temporelles
    print("  [5/6] Tendances temporelles...")
    results["trends"] = analyze_time_trends(
        data["transactions"], data["items"]
    )

    # Module 6 — Prévisions de demande
    print("  [6/6] Prévisions de demande...")
    results["forecast"] = analyze_demand_forecast(
        data["items"], data["transactions"], data["stock"]
    )

    print("✅ Analyse complète !")
    return results


def main():
    parser = argparse.ArgumentParser(
        description="SpringLane Purchase Intelligence Report Generator"
    )
    parser.add_argument("--customers", type=int, default=300,
                        help="Nombre de clients simulés (défaut: 300)")
    parser.add_argument("--months", type=int, default=6,
                        help="Nombre de mois de données (défaut: 6)")
    parser.add_argument("--store", type=str, default="Paris Marais",
                        help="Nom du magasin (défaut: Paris Marais)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Seed pour la reproductibilité (défaut: 42)")
    parser.add_argument("--output-dir", type=str, default="output",
                        help="Dossier de sortie (défaut: output/)")
    parser.add_argument("--export-csv", action="store_true",
                        help="Exporter les données simulées en CSV")
    args = parser.parse_args()

    # Configuration
    config = SimulationConfig(
        n_customers=args.customers,
        n_months=args.months,
        store_name=args.store,
        seed=args.seed,
    )

    print("=" * 60)
    print("  🚀 SpringLane Purchase Intelligence Engine v0.1.0")
    print("=" * 60)
    print(f"  Magasin     : {config.store_name}")
    print(f"  Clients     : {config.n_customers}")
    print(f"  Période     : {config.n_months} mois")
    print(f"  Seed        : {config.seed}")
    print("=" * 60)

    # --- Étape 1 : Simulation des données ---
    data = run_simulation(config)

    # Export CSV optionnel
    if args.export_csv:
        csv_dir = os.path.join(args.output_dir, "csv")
        os.makedirs(csv_dir, exist_ok=True)
        for name, df in data.items():
            path = os.path.join(csv_dir, f"{name}.csv")
            df.to_csv(path, index=False)
            print(f"  💾 CSV exporté : {path}")

    # --- Étape 2 : Analyse ---
    results = run_analytics(data)

    # --- Étape 3 : Génération du rapport PDF ---
    print("\n📄 Génération du rapport PDF...")
    os.makedirs(args.output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = os.path.join(
        args.output_dir,
        f"SpringLane_Intelligence_Report_{timestamp}.pdf"
    )

    config_info = (
        f"{config.start_date.strftime('%d/%m/%Y')} — "
        f"{config.n_months} mois | {config.n_customers} clients simulés"
    )

    generate_report(
        all_results=results,
        output_path=pdf_path,
        store_name=config.store_name,
        config_info=config_info,
    )

    # --- Étape 4 : Export JSON des métriques ---
    json_path = os.path.join(args.output_dir, f"metrics_{timestamp}.json")
    # Convertir les résultats en sérialisable JSON
    def _serialize(obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        if isinstance(obj, (set, frozenset)):
            return list(obj)
        return str(obj)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=_serialize)
    print(f"📋 Métriques JSON exportées : {json_path}")

    print("\n" + "=" * 60)
    print("  ✅ Pipeline terminé avec succès !")
    print(f"  📄 Rapport : {pdf_path}")
    print(f"  📋 JSON    : {json_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
