"""
Module 1 — Analyse démographique et profil client.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any

from springlane.config import AGE_BRACKETS


def _age_bracket(age: int) -> str:
    if age < 25:
        return "18-24"
    elif age < 35:
        return "25-34"
    elif age < 45:
        return "35-44"
    return "45+"


def analyze_demographics(
    customers: pd.DataFrame,
    transactions: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Calcule les métriques démographiques.
    """
    results = {}

    # --- Core metrics ---
    results["total_customers"] = len(customers)

    # Clients actifs (au moins 1 transaction)
    active_ids = transactions["customer_id"].unique()
    results["active_customers"] = len(active_ids)
    results["inactive_customers"] = results["total_customers"] - results["active_customers"]

    # Nouveaux vs récurrents (>1 transaction)
    tx_counts = transactions.groupby("customer_id").size()
    results["new_customers"] = int((tx_counts == 1).sum())
    results["returning_customers"] = int((tx_counts > 1).sum())

    # Brackets d'âge
    customers = customers.copy()
    customers["age_bracket"] = customers["age"].apply(_age_bracket)
    age_dist = customers["age_bracket"].value_counts(normalize=True).reindex(
        AGE_BRACKETS, fill_value=0
    )
    results["age_distribution"] = age_dist.to_dict()
    results["age_distribution_pct"] = (age_dist * 100).round(1).to_dict()

    # Genre
    gender_dist = customers["gender"].value_counts(normalize=True)
    results["gender_distribution"] = gender_dist.to_dict()
    results["gender_distribution_pct"] = (gender_dist * 100).round(1).to_dict()

    # Heatmap code postal
    postcode_counts = customers["postcode"].value_counts()
    results["postcode_heatmap"] = postcode_counts.head(10).to_dict()

    # Tourist vs local
    results["local_pct"] = round(
        (~customers["is_tourist"]).mean() * 100, 1
    )
    results["tourist_pct"] = round(
        customers["is_tourist"].mean() * 100, 1
    )

    # --- High-value insights ---
    # Top purchasing age group par catégorie
    active_customers = customers[customers["customer_id"].isin(active_ids)].copy()
    merged = transactions.merge(active_customers[["customer_id", "age_bracket"]])
    if not merged.empty:
        # On a besoin des items pour la catégorie — on utilise le total comme proxy
        results["avg_spend_by_age"] = (
            merged.groupby("age_bracket")["total_amount"]
            .mean().round(2).to_dict()
        )

    # Concentration locale
    local_customers = customers[~customers["is_tourist"]]
    if len(local_customers) > 0:
        results["top_local_postcodes"] = (
            local_customers["postcode"].value_counts().head(5).to_dict()
        )

    return results
