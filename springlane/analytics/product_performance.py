"""
Module 3 — Intelligence de performance produit.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any


def analyze_product_performance(
    items: pd.DataFrame,
    transactions: pd.DataFrame,
    customers: pd.DataFrame,
    stock: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Calcule les métriques de performance produit.
    """
    results = {}

    # --- Core metrics : volume & revenu par produit ---
    product_stats = items.groupby(["product_id", "product_name", "category"]).agg(
        total_qty=("quantity", "sum"),
        total_revenue=("line_total", "sum"),
        n_transactions=("transaction_id", "nunique"),
    ).reset_index()

    product_stats = product_stats.sort_values("total_revenue", ascending=False)
    product_stats["rank"] = range(1, len(product_stats) + 1)
    product_stats["total_revenue"] = product_stats["total_revenue"].round(2)

    # Tier (Top / Middle / Bottom)
    n = len(product_stats)
    product_stats["tier"] = pd.cut(
        product_stats["rank"],
        bins=[0, max(1, n // 3), max(2, 2 * n // 3), n + 1],
        labels=["Top", "Middle", "Bottom"],
    )

    results["product_ranking"] = product_stats.to_dict("records")
    results["top_10_products"] = product_stats.head(10)[
        ["rank", "product_name", "category", "total_qty", "total_revenue"]
    ].to_dict("records")

    results["bottom_5_products"] = product_stats.tail(5)[
        ["rank", "product_name", "category", "total_qty", "total_revenue"]
    ].to_dict("records")

    # Revenu par catégorie
    cat_revenue = items.groupby("category")["line_total"].sum().round(2)
    results["revenue_by_category"] = cat_revenue.sort_values(ascending=False).to_dict()

    # Units by category
    cat_qty = items.groupby("category")["quantity"].sum()
    results["units_by_category"] = cat_qty.sort_values(ascending=False).to_dict()

    # --- Sell-through rate ---
    if stock is not None and len(stock) > 0:
        sell_through = product_stats[["product_id", "total_qty"]].merge(
            stock[["product_id", "initial_stock"]], on="product_id", how="left"
        )
        sell_through["sell_through_rate"] = (
            sell_through["total_qty"] / sell_through["initial_stock"].clip(lower=1) * 100
        ).round(1)
        results["sell_through"] = sell_through[
            ["product_id", "total_qty", "initial_stock", "sell_through_rate"]
        ].to_dict("records")

    # --- Performance par groupe d'âge ---
    tx_with_age = transactions[["transaction_id", "customer_id"]].merge(
        customers[["customer_id", "age"]], on="customer_id"
    )
    tx_with_age["age_bracket"] = tx_with_age["age"].apply(
        lambda a: "18-24" if a < 25 else ("25-34" if a < 35 else ("35-44" if a < 45 else "45+"))
    )
    items_with_age = items.merge(
        tx_with_age[["transaction_id", "age_bracket"]], on="transaction_id"
    )
    if not items_with_age.empty:
        age_cat = items_with_age.groupby(
            ["age_bracket", "category"]
        )["line_total"].sum().round(2)
        results["revenue_by_age_category"] = {
            str(k): v for k, v in age_cat.to_dict().items()
        }

        # Top catégorie par groupe d'âge
        top_cat_by_age = age_cat.groupby(level=0).idxmax()
        results["top_category_by_age"] = {
            age: cat for age, (_, cat) in top_cat_by_age.items()
        }

    # --- Bestsellers vs long-tail ---
    top_20_pct = product_stats.head(max(1, n // 5))
    results["bestseller_revenue_share"] = round(
        top_20_pct["total_revenue"].sum() / max(1, product_stats["total_revenue"].sum()) * 100, 1
    )
    results["long_tail_count"] = int((product_stats["total_qty"] <= 5).sum())

    return results
