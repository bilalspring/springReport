"""
Module 5 — Tendances temporelles d'achat.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any


DAYS_FR = {
    "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi",
    "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi",
    "Sunday": "Dimanche",
}
DAY_ORDER = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


def analyze_time_trends(
    transactions: pd.DataFrame,
    items: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Analyse les tendances temporelles de vente.
    """
    results = {}
    tx = transactions.copy()
    tx["datetime"] = pd.to_datetime(tx["datetime"])
    tx["date"] = pd.to_datetime(tx["date"])
    tx["month"] = tx["datetime"].dt.to_period("M").astype(str)
    tx["day_fr"] = tx["day_of_week"].map(DAYS_FR)

    # --- Ventes par heure ---
    hourly = tx.groupby("hour").agg(
        transactions=("transaction_id", "count"),
        revenue=("total_amount", "sum"),
    ).reindex(range(24), fill_value=0)
    hourly["revenue"] = hourly["revenue"].round(2)
    results["sales_by_hour"] = hourly.to_dict()

    peak_hour = hourly["transactions"].idxmax()
    results["peak_hour"] = int(peak_hour)
    results["peak_hour_label"] = f"{peak_hour}h00 - {peak_hour+1}h00"

    # --- Ventes par jour de la semaine ---
    daily = tx.groupby("day_fr").agg(
        transactions=("transaction_id", "count"),
        revenue=("total_amount", "sum"),
    )
    daily = daily.reindex(DAY_ORDER, fill_value=0)
    daily["revenue"] = daily["revenue"].round(2)
    results["sales_by_day"] = daily.to_dict()

    peak_day = daily["revenue"].idxmax()
    results["peak_day"] = peak_day

    # --- Ventes par mois ---
    monthly = tx.groupby("month").agg(
        transactions=("transaction_id", "count"),
        revenue=("total_amount", "sum"),
        avg_basket=("total_amount", "mean"),
        unique_customers=("customer_id", "nunique"),
    ).round(2)
    results["sales_by_month"] = monthly.to_dict()
    results["monthly_summary"] = monthly.reset_index().to_dict("records")

    # --- Vélocité des ventes par produit ---
    items_tx = items.merge(
        tx[["transaction_id", "datetime"]], on="transaction_id"
    )
    product_velocity = items_tx.groupby("product_name").agg(
        first_sale=("datetime", "min"),
        last_sale=("datetime", "max"),
        total_units=("quantity", "sum"),
    )
    product_velocity["days_span"] = (
        product_velocity["last_sale"] - product_velocity["first_sale"]
    ).dt.days.clip(lower=1)
    product_velocity["units_per_day"] = (
        product_velocity["total_units"] / product_velocity["days_span"]
    ).round(2)
    product_velocity = product_velocity.sort_values("units_per_day", ascending=False)
    results["product_velocity"] = (
        product_velocity[["total_units", "days_span", "units_per_day"]]
        .head(10).reset_index().to_dict("records")
    )

    # --- Indicateurs de tendance (accélération / décélération) ---
    if len(monthly) >= 2:
        months_sorted = monthly.sort_index()
        revenue_series = months_sorted["revenue"]
        # Variation mois sur mois
        mom_change = revenue_series.pct_change().dropna()
        results["month_over_month_growth"] = (mom_change * 100).round(1).to_dict()

        last_mom = mom_change.iloc[-1] if len(mom_change) > 0 else 0
        if last_mom > 0.1:
            results["trend_signal"] = "📈 Accélération des ventes"
        elif last_mom < -0.1:
            results["trend_signal"] = "📉 Décélération des ventes"
        else:
            results["trend_signal"] = "➡️ Ventes stables"
    else:
        results["trend_signal"] = "Données insuffisantes"

    return results
