"""
Module 4 — Analyse de panier & cross-sell.
"""
import pandas as pd
import numpy as np
from itertools import combinations
from typing import Dict, Any


def analyze_baskets(
    items: pd.DataFrame,
    transactions: pd.DataFrame,
    customers: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Analyse les compositions de panier et identifie les affinités cross-sell.
    """
    results = {}

    # --- Composition moyenne du panier ---
    basket_composition = items.groupby("transaction_id").agg(
        n_items=("quantity", "sum"),
        n_unique_products=("product_id", "nunique"),
        n_categories=("category", "nunique"),
        total=("line_total", "sum"),
    )
    results["avg_basket"] = {
        "items": round(basket_composition["n_items"].mean(), 1),
        "unique_products": round(basket_composition["n_unique_products"].mean(), 1),
        "categories": round(basket_composition["n_categories"].mean(), 1),
        "value": round(basket_composition["total"].mean(), 2),
    }

    # --- Combinaisons de produits les plus fréquentes ---
    # Construire la matrice de co-occurrence
    baskets = items.groupby("transaction_id")["product_name"].apply(list)
    pair_counts = {}

    for basket_items in baskets:
        unique_items = list(set(basket_items))
        if len(unique_items) < 2:
            continue
        for pair in combinations(sorted(unique_items), 2):
            pair_counts[pair] = pair_counts.get(pair, 0) + 1

    # Top 10 combinaisons
    top_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    results["top_product_pairs"] = [
        {"product_a": p[0], "product_b": p[1], "frequency": count}
        for p, count in top_pairs
    ]

    # --- Cross-sell affinity score ---
    # P(B|A) = P(A∩B) / P(A)
    n_baskets = len(baskets)
    product_frequency = items.groupby("product_name")["transaction_id"].nunique()

    affinity_scores = []
    for (prod_a, prod_b), co_count in pair_counts.items():
        freq_a = product_frequency.get(prod_a, 0)
        freq_b = product_frequency.get(prod_b, 0)
        if freq_a > 0 and freq_b > 0:
            # Lift = P(A∩B) / (P(A) * P(B))
            p_ab = co_count / n_baskets
            p_a = freq_a / n_baskets
            p_b = freq_b / n_baskets
            lift = p_ab / (p_a * p_b) if (p_a * p_b) > 0 else 0

            affinity_scores.append({
                "product_a": prod_a,
                "product_b": prod_b,
                "co_occurrences": co_count,
                "confidence_a_to_b": round(co_count / freq_a * 100, 1),
                "confidence_b_to_a": round(co_count / freq_b * 100, 1),
                "lift": round(lift, 2),
            })

    affinity_df = pd.DataFrame(affinity_scores)
    if not affinity_df.empty:
        affinity_df = affinity_df.sort_values("lift", ascending=False)
        results["cross_sell_affinity"] = affinity_df.head(10).to_dict("records")

        # "Si produit A acheté → X% chance produit B"
        top_rules = []
        for _, row in affinity_df.head(5).iterrows():
            top_rules.append(
                f"Si {row['product_a']} → {row['confidence_a_to_b']}% chance "
                f"que {row['product_b']} soit acheté"
            )
        results["association_rules"] = top_rules

    # --- Combinaisons de catégories ---
    cat_baskets = items.groupby("transaction_id")["category"].apply(
        lambda x: tuple(sorted(set(x)))
    )
    cat_combos = cat_baskets.value_counts().head(5)
    results["top_category_combos"] = {
        " + ".join(combo): int(count)
        for combo, count in cat_combos.items()
    }

    # --- Opportunités de bundle manquées ---
    # Produits souvent scannés ensemble mais rarement achetés ensemble
    results["bundle_opportunities"] = []
    if not affinity_df.empty:
        high_lift_low_freq = affinity_df[
            (affinity_df["lift"] > 1.5) & (affinity_df["co_occurrences"] < 10)
        ].head(3)
        for _, row in high_lift_low_freq.iterrows():
            results["bundle_opportunities"].append({
                "products": f"{row['product_a']} + {row['product_b']}",
                "lift": row["lift"],
                "current_co_purchases": row["co_occurrences"],
            })

    return results
