"""
Module 2 — Analyse du comportement d'achat.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any


def analyze_purchase_behavior(
    transactions: pd.DataFrame,
    scans: pd.DataFrame,
    customers: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Calcule les métriques de comportement d'achat.
    """
    results = {}

    # --- Core metrics ---
    results["total_transactions"] = len(transactions)
    results["total_scans"] = len(scans)
    results["scans_without_purchase"] = int(
        (~scans["resulted_in_purchase"]).sum()
    )
    results["scan_to_purchase_rate"] = round(
        scans["resulted_in_purchase"].mean() * 100, 1
    )

    # Panier moyen
    results["avg_basket_value"] = round(transactions["total_amount"].mean(), 2)
    results["median_basket_value"] = round(transactions["total_amount"].median(), 2)
    results["avg_items_per_basket"] = round(transactions["n_items"].mean(), 1)

    # Fréquence d'achat par client
    tx_per_customer = transactions.groupby("customer_id").size()
    results["avg_purchases_per_customer"] = round(tx_per_customer.mean(), 1)
    results["max_purchases_per_customer"] = int(tx_per_customer.max())

    # Fréquence mensuelle / hebdomadaire
    if "date" in transactions.columns:
        transactions = transactions.copy()
        transactions["date"] = pd.to_datetime(transactions["date"])
        date_range_days = (transactions["date"].max() - transactions["date"].min()).days
        if date_range_days > 0:
            months = max(1, date_range_days / 30)
            weeks = max(1, date_range_days / 7)
            results["avg_monthly_frequency"] = round(
                len(transactions) / months / len(tx_per_customer), 2
            )
            results["avg_weekly_frequency"] = round(
                len(transactions) / weeks / len(tx_per_customer), 2
            )

    # Temps entre les achats (cycle de réachat)
    repurchase_gaps = []
    for cid, group in transactions.sort_values("datetime").groupby("customer_id"):
        if len(group) > 1:
            dates = pd.to_datetime(group["datetime"])
            gaps = dates.diff().dropna().dt.days
            repurchase_gaps.extend(gaps.tolist())

    if repurchase_gaps:
        results["avg_repurchase_cycle_days"] = round(np.mean(repurchase_gaps), 1)
        results["median_repurchase_cycle_days"] = round(np.median(repurchase_gaps), 1)
    else:
        results["avg_repurchase_cycle_days"] = None
        results["median_repurchase_cycle_days"] = None

    # --- Segmentation comportementale ---
    one_time = int((tx_per_customer == 1).sum())
    occasional = int(((tx_per_customer >= 2) & (tx_per_customer <= 4)).sum())
    loyal = int((tx_per_customer >= 5).sum())
    total_active = one_time + occasional + loyal

    results["segments"] = {
        "one_time": {
            "count": one_time,
            "pct": round(one_time / max(1, total_active) * 100, 1),
        },
        "occasional": {
            "count": occasional,
            "pct": round(occasional / max(1, total_active) * 100, 1),
        },
        "loyal": {
            "count": loyal,
            "pct": round(loyal / max(1, total_active) * 100, 1),
        },
    }

    # Distribution des valeurs de panier
    results["basket_value_distribution"] = {
        "0-20": int((transactions["total_amount"] < 20).sum()),
        "20-50": int(((transactions["total_amount"] >= 20) & (transactions["total_amount"] < 50)).sum()),
        "50-100": int(((transactions["total_amount"] >= 50) & (transactions["total_amount"] < 100)).sum()),
        "100-200": int(((transactions["total_amount"] >= 100) & (transactions["total_amount"] < 200)).sum()),
        "200+": int((transactions["total_amount"] >= 200).sum()),
    }

    return results
