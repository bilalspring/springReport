"""
Module 6 — Prévision de demande & optimisation des stocks.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
from scipy import stats


def analyze_demand_forecast(
    items: pd.DataFrame,
    transactions: pd.DataFrame,
    stock: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Calcule les prévisions de demande et recommandations de stock.
    Utilise une approche de lissage exponentiel simple pour le POC.
    """
    results = {}

    tx = transactions.copy()
    tx["datetime"] = pd.to_datetime(tx["datetime"])
    tx["week"] = tx["datetime"].dt.isocalendar().week.astype(int)
    tx["date"] = pd.to_datetime(tx["date"])

    items_tx = items.merge(tx[["transaction_id", "datetime", "date"]], on="transaction_id")
    items_tx["week"] = items_tx["datetime"].dt.isocalendar().week.astype(int)

    # --- Calcul de la demande hebdomadaire par produit ---
    weekly_demand = items_tx.groupby(
        ["product_id", "product_name", "week"]
    )["quantity"].sum().reset_index()

    # Demande moyenne par produit
    avg_demand = weekly_demand.groupby(["product_id", "product_name"]).agg(
        avg_weekly_demand=("quantity", "mean"),
        std_weekly_demand=("quantity", "std"),
        max_weekly_demand=("quantity", "max"),
        n_weeks_active=("week", "nunique"),
    ).reset_index()
    avg_demand["std_weekly_demand"] = avg_demand["std_weekly_demand"].fillna(0)

    # --- Merge avec stock ---
    forecast = avg_demand.merge(stock, on="product_id", how="left", suffixes=("", "_stock"))

    # --- Forecast simple : prochaines 4 semaines ---
    # Utilise la moyenne + marge de sécurité (1.5 * écart-type)
    forecast["forecast_4w_demand"] = (
        forecast["avg_weekly_demand"] * 4
    ).round(0).astype(int)

    forecast["safety_stock"] = (
        1.5 * forecast["std_weekly_demand"] * np.sqrt(forecast["lead_time_days"] / 7)
    ).round(0).astype(int)

    # --- Date estimée de rupture de stock ---
    forecast["days_until_stockout"] = np.where(
        forecast["avg_weekly_demand"] > 0,
        (forecast["current_stock"] / (forecast["avg_weekly_demand"] / 7)).round(0),
        999
    ).astype(int)

    # --- Score de risque de surstock ---
    # Si le stock actuel > 3 mois de demande → surstock
    forecast["months_of_stock"] = np.where(
        forecast["avg_weekly_demand"] > 0,
        forecast["current_stock"] / (forecast["avg_weekly_demand"] * 4.33),
        99
    ).round(1)

    forecast["overstock_risk"] = pd.cut(
        forecast["months_of_stock"],
        bins=[0, 1, 2, 3, 100],
        labels=["Bas", "Modéré", "Élevé", "Critique"],
    )

    # --- Quantité optimale de réapprovisionnement ---
    # EOQ simplifié: Q = demande prévue + stock de sécurité - stock actuel
    forecast["reorder_qty"] = (
        forecast["forecast_4w_demand"]
        + forecast["safety_stock"]
        - forecast["current_stock"]
    ).clip(lower=0).astype(int)

    # --- Résultats structurés ---
    results["product_forecasts"] = forecast[[
        "product_id", "product_name_stock", "category",
        "current_stock", "avg_weekly_demand", "forecast_4w_demand",
        "safety_stock", "days_until_stockout", "overstock_risk",
        "reorder_qty", "lead_time_days",
    ]].rename(columns={"product_name_stock": "product_name"}).to_dict("records")

    # --- Alertes prédictives ---
    alerts = []

    # Risque de rupture (< 14 jours)
    stockout_risk = forecast[forecast["days_until_stockout"] < 14]
    for _, row in stockout_risk.iterrows():
        alerts.append({
            "type": "stockout",
            "severity": "🔴 CRITIQUE" if row["days_until_stockout"] < 7 else "🟡 ATTENTION",
            "message": f"Risque de rupture: {row['product_name']} "
                       f"({row['days_until_stockout']}j restants)",
            "product_id": row["product_id"],
            "action": f"Commander {row['reorder_qty']} unités",
        })

    # Produits en surstock
    overstock = forecast[forecast["overstock_risk"].isin(["Élevé", "Critique"])]
    for _, row in overstock.iterrows():
        alerts.append({
            "type": "overstock",
            "severity": "🟠 SURSTOCK",
            "message": f"Rotation lente: {row['product_name']} "
                       f"({row['months_of_stock']} mois de stock)",
            "product_id": row["product_id"],
            "action": "Envisager promotion ou réduction de commande",
        })

    # Pics de demande inattendus
    demand_spikes = forecast[
        forecast["max_weekly_demand"] > forecast["avg_weekly_demand"] * 2.5
    ]
    for _, row in demand_spikes.iterrows():
        alerts.append({
            "type": "demand_spike",
            "severity": "📈 SPIKE",
            "message": f"Pic de demande détecté: {row['product_name']}",
            "product_id": row["product_id"],
            "action": "Vérifier approvisionnement",
        })

    results["alerts"] = sorted(alerts, key=lambda x: x["severity"])
    results["n_stockout_alerts"] = len(stockout_risk)
    results["n_overstock_alerts"] = len(overstock)

    # --- Résumé reorder ---
    reorder_needed = forecast[forecast["reorder_qty"] > 0][[
        "product_id", "product_name", "reorder_qty", "days_until_stockout"
    ]].sort_values("days_until_stockout")
    results["reorder_recommendations"] = reorder_needed.head(10).to_dict("records")

    return results
