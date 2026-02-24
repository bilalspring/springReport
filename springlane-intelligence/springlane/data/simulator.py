"""
Simulateur de données SpringLane.
Génère des profils clients, transactions et scans produits réalistes.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, Dict
from faker import Faker

from springlane.config import (
    SimulationConfig, PRODUCT_CATALOG, LOCAL_POSTCODES,
    TOURIST_POSTCODES, PRODUCT_AFFINITIES,
)

fake = Faker("fr_FR")


def generate_customers(config: SimulationConfig) -> pd.DataFrame:
    """Génère des profils clients réalistes."""
    np.random.seed(config.seed)
    Faker.seed(config.seed)

    n = config.n_customers

    # Distribution d'âge réaliste (pondérée vers 25-34)
    age_weights = [0.20, 0.35, 0.25, 0.20]  # 18-24, 25-34, 35-44, 45-60
    age_ranges = [(18, 24), (25, 34), (35, 44), (45, 60)]
    ages = []
    for _ in range(n):
        bracket = np.random.choice(len(age_ranges), p=age_weights)
        low, high = age_ranges[bracket]
        ages.append(np.random.randint(low, high + 1))

    # Genre : 55% F, 43% M, 2% Autre
    genders = np.random.choice(
        ["F", "M", "Autre"], size=n, p=[0.55, 0.43, 0.02]
    )

    # Codes postaux : 75% locaux, 25% touristes
    postcodes = []
    is_tourist = []
    for _ in range(n):
        if np.random.random() < 0.75:
            postcodes.append(np.random.choice(LOCAL_POSTCODES))
            is_tourist.append(False)
        else:
            postcodes.append(np.random.choice(TOURIST_POSTCODES))
            is_tourist.append(True)

    # Date d'inscription (répartie sur la période)
    end_date = config.start_date + timedelta(days=config.n_months * 30)
    signup_dates = [
        config.start_date + timedelta(
            days=int(np.random.exponential(scale=30))
        )
        for _ in range(n)
    ]
    signup_dates = [min(d, end_date - timedelta(days=1)) for d in signup_dates]

    customers = pd.DataFrame({
        "customer_id": [f"C{i:04d}" for i in range(1, n + 1)],
        "full_name": [fake.name() for _ in range(n)],
        "gender": genders,
        "age": ages,
        "date_of_birth": [
            datetime(2026, 1, 1) - timedelta(days=int(a * 365.25))
            for a in ages
        ],
        "postcode": postcodes,
        "is_tourist": is_tourist,
        "email": [fake.email() for _ in range(n)],
        "signup_date": signup_dates,
        "country": ["FR" if not t else np.random.choice(["DE", "GB", "ES", "IT"])
                     for t in is_tourist],
    })

    # Assigner un profil de comportement (affecte la fréquence d'achat)
    behavior_prob = np.random.dirichlet([2, 3, 1.5], size=1)[0]
    customers["behavior_type"] = np.random.choice(
        ["one_time", "occasional", "loyal"], size=n, p=behavior_prob
    )

    return customers


def _build_product_df() -> pd.DataFrame:
    """Convertit le catalogue produit en DataFrame."""
    return pd.DataFrame(PRODUCT_CATALOG)


def _pick_basket_items(
    products_df: pd.DataFrame,
    customer_age: int,
    customer_gender: str,
    rng: np.random.Generator,
) -> list:
    """Génère un panier réaliste en tenant compte des affinités produit."""
    # Nombre d'articles par panier (distribution réaliste)
    n_items = max(1, int(rng.normal(loc=2.8, scale=1.5)))
    n_items = min(n_items, 8)

    # Pondérer les catégories selon âge/genre
    category_weights = _get_category_weights(customer_age, customer_gender)

    # Choisir le premier produit
    weighted_probs = products_df["category"].map(category_weights).values
    weighted_probs = weighted_probs / weighted_probs.sum()
    first_idx = rng.choice(len(products_df), p=weighted_probs)
    first_product = products_df.iloc[first_idx]["id"]

    basket = [first_product]

    # Ajouter des produits avec affinité
    for _ in range(n_items - 1):
        last_product = basket[-1]
        affinities = PRODUCT_AFFINITIES.get(last_product, [])

        if affinities and rng.random() < 0.6:
            # 60% de chance de suivre une affinité
            available = [p for p in affinities if p not in basket
                         and p in products_df["id"].values]
            if available:
                basket.append(rng.choice(available))
                continue

        # Sinon, produit aléatoire pondéré
        remaining = products_df[~products_df["id"].isin(basket)]
        if len(remaining) == 0:
            break
        w = remaining["category"].map(category_weights).values
        w = w / w.sum()
        idx = rng.choice(len(remaining), p=w)
        basket.append(remaining.iloc[idx]["id"])

    return basket


def _get_category_weights(age: int, gender: str) -> dict:
    """Retourne les pondérations de catégorie selon le profil client."""
    base = {"Mode": 1.0, "Accessoires": 0.8, "Chaussures": 0.7,
            "Beauté": 0.6, "Maison": 0.5}

    if gender == "F":
        base["Beauté"] = 1.2
        base["Accessoires"] = 1.0
    elif gender == "M":
        base["Chaussures"] = 0.9
        base["Beauté"] = 0.3

    if age < 25:
        base["Mode"] = 1.3
        base["Accessoires"] = 1.1
    elif age > 44:
        base["Maison"] = 1.0
        base["Beauté"] = 0.8

    return base


def generate_transactions(
    customers: pd.DataFrame,
    config: SimulationConfig,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Génère les transactions et les lignes de détail (items).
    Retourne (transactions_df, transaction_items_df).
    """
    rng = np.random.default_rng(config.seed)
    products_df = _build_product_df()
    end_date = config.start_date + timedelta(days=config.n_months * 30)

    transactions = []
    items = []
    tx_id = 0

    for _, cust in customers.iterrows():
        # Nombre de visites selon le profil comportemental
        behavior = cust["behavior_type"]
        if behavior == "one_time":
            n_visits = 1
        elif behavior == "occasional":
            n_visits = rng.integers(2, 5)
        else:  # loyal
            n_visits = rng.integers(5, int(config.n_months * 3) + 1)

        signup = cust["signup_date"]
        days_available = (end_date - signup).days
        if days_available <= 0:
            continue

        for _ in range(n_visits):
            tx_id += 1
            # Date aléatoire après inscription
            tx_date = signup + timedelta(days=int(rng.integers(0, max(1, days_available))))

            # Heure réaliste (pic à 12h et 17h)
            hour_weights = np.zeros(24)
            hour_weights[9:21] = 1.0
            hour_weights[11:14] = 2.5   # Pause déjeuner
            hour_weights[16:19] = 2.0   # Après-midi / after-work
            hour_weights /= hour_weights.sum()
            hour = rng.choice(24, p=hour_weights)
            minute = rng.integers(0, 60)

            tx_datetime = tx_date.replace(hour=int(hour), minute=int(minute))

            # Générer le panier
            basket = _pick_basket_items(
                products_df, cust["age"], cust["gender"], rng
            )

            total = 0.0
            for product_id in basket:
                prod = products_df[products_df["id"] == product_id].iloc[0]
                qty = int(rng.choice([1, 1, 1, 2], p=[0.7, 0.1, 0.1, 0.1]))
                line_total = prod["price"] * qty
                total += line_total

                items.append({
                    "transaction_id": f"TX{tx_id:06d}",
                    "product_id": product_id,
                    "product_name": prod["name"],
                    "category": prod["category"],
                    "subcategory": prod["subcategory"],
                    "unit_price": prod["price"],
                    "quantity": qty,
                    "line_total": round(line_total, 2),
                })

            transactions.append({
                "transaction_id": f"TX{tx_id:06d}",
                "customer_id": cust["customer_id"],
                "datetime": tx_datetime,
                "date": tx_datetime.date(),
                "hour": int(hour),
                "day_of_week": tx_datetime.strftime("%A"),
                "n_items": len(basket),
                "total_amount": round(total, 2),
                "is_purchase": True,
            })

    transactions_df = pd.DataFrame(transactions)
    items_df = pd.DataFrame(items)

    return transactions_df, items_df


def generate_scan_events(
    customers: pd.DataFrame,
    config: SimulationConfig,
) -> pd.DataFrame:
    """Génère des événements de scan sans achat (browsing)."""
    rng = np.random.default_rng(config.seed + 1)
    products_df = _build_product_df()
    end_date = config.start_date + timedelta(days=config.n_months * 30)

    scans = []
    scan_id = 0

    for _, cust in customers.iterrows():
        # Plus de scans que d'achats (ratio ~2:1)
        n_scans = rng.integers(1, 8)
        signup = cust["signup_date"]
        days_available = (end_date - signup).days
        if days_available <= 0:
            continue

        for _ in range(n_scans):
            scan_id += 1
            scan_date = signup + timedelta(days=int(rng.integers(0, max(1, days_available))))
            product = products_df.iloc[rng.integers(0, len(products_df))]

            scans.append({
                "scan_id": f"SC{scan_id:06d}",
                "customer_id": cust["customer_id"],
                "product_id": product["id"],
                "product_name": product["name"],
                "category": product["category"],
                "datetime": scan_date,
                "resulted_in_purchase": bool(rng.random() < 0.35),
            })

    return pd.DataFrame(scans)


def generate_stock_levels(config: SimulationConfig) -> pd.DataFrame:
    """Génère des niveaux de stock simulés pour le forecasting."""
    rng = np.random.default_rng(config.seed + 2)
    products_df = _build_product_df()

    stock = []
    for _, prod in products_df.iterrows():
        initial = rng.integers(50, 300)
        stock.append({
            "product_id": prod["id"],
            "product_name": prod["name"],
            "category": prod["category"],
            "initial_stock": int(initial),
            "current_stock": int(max(0, initial - rng.integers(20, initial))),
            "cost_per_unit": prod["cost"],
            "price_per_unit": prod["price"],
            "lead_time_days": int(rng.choice([3, 5, 7, 10, 14])),
        })

    return pd.DataFrame(stock)


def run_simulation(config: SimulationConfig = None) -> Dict[str, pd.DataFrame]:
    """
    Exécute la simulation complète.
    Retourne un dictionnaire de DataFrames.
    """
    if config is None:
        config = SimulationConfig()

    print(f"🔄 Simulation en cours ({config.n_customers} clients, "
          f"{config.n_months} mois)...")

    customers = generate_customers(config)
    transactions, items = generate_transactions(customers, config)
    scans = generate_scan_events(customers, config)
    stock = generate_stock_levels(config)

    data = {
        "customers": customers,
        "transactions": transactions,
        "items": items,
        "scans": scans,
        "stock": stock,
    }

    print(f"✅ Simulation terminée:")
    print(f"   • {len(customers)} clients")
    print(f"   • {len(transactions)} transactions")
    print(f"   • {len(items)} lignes articles")
    print(f"   • {len(scans)} scans produits")

    return data
