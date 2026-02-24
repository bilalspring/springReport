"""
Configuration et constantes pour le moteur d'intelligence SpringLane.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict


@dataclass
class SimulationConfig:
    """Paramètres de simulation des données."""
    n_customers: int = 300
    n_products: int = 50
    n_months: int = 6
    store_name: str = "Paris Marais"
    store_postcode: str = "75004"
    start_date: datetime = field(default_factory=lambda: datetime(2025, 7, 1))
    seed: int = 42


# --- Catalogue produits simulé ---
PRODUCT_CATALOG: List[Dict] = [
    # Mode
    {"id": "P001", "name": "T-Shirt Basique Coton", "category": "Mode", "subcategory": "Hauts", "price": 19.99, "cost": 6.00},
    {"id": "P002", "name": "Jean Slim Fit", "category": "Mode", "subcategory": "Bas", "price": 49.99, "cost": 15.00},
    {"id": "P003", "name": "Veste Légère", "category": "Mode", "subcategory": "Vestes", "price": 79.99, "cost": 25.00},
    {"id": "P004", "name": "Robe Été Fleurie", "category": "Mode", "subcategory": "Robes", "price": 39.99, "cost": 12.00},
    {"id": "P005", "name": "Pull Col Roulé", "category": "Mode", "subcategory": "Hauts", "price": 44.99, "cost": 14.00},
    {"id": "P006", "name": "Short Chino", "category": "Mode", "subcategory": "Bas", "price": 29.99, "cost": 9.00},
    {"id": "P007", "name": "Chemise Lin", "category": "Mode", "subcategory": "Hauts", "price": 54.99, "cost": 17.00},
    {"id": "P008", "name": "Blazer Casual", "category": "Mode", "subcategory": "Vestes", "price": 89.99, "cost": 28.00},
    # Accessoires
    {"id": "P009", "name": "Sac Cabas Cuir", "category": "Accessoires", "subcategory": "Sacs", "price": 129.99, "cost": 40.00},
    {"id": "P010", "name": "Ceinture Cuir", "category": "Accessoires", "subcategory": "Ceintures", "price": 34.99, "cost": 10.00},
    {"id": "P011", "name": "Écharpe Soie", "category": "Accessoires", "subcategory": "Écharpes", "price": 59.99, "cost": 18.00},
    {"id": "P012", "name": "Lunettes Soleil", "category": "Accessoires", "subcategory": "Lunettes", "price": 24.99, "cost": 5.00},
    {"id": "P013", "name": "Montre Minimaliste", "category": "Accessoires", "subcategory": "Montres", "price": 149.99, "cost": 45.00},
    {"id": "P014", "name": "Casquette Coton", "category": "Accessoires", "subcategory": "Chapeaux", "price": 19.99, "cost": 4.00},
    # Chaussures
    {"id": "P015", "name": "Sneakers Blanches", "category": "Chaussures", "subcategory": "Baskets", "price": 89.99, "cost": 28.00},
    {"id": "P016", "name": "Mocassins Cuir", "category": "Chaussures", "subcategory": "Ville", "price": 109.99, "cost": 35.00},
    {"id": "P017", "name": "Sandales Été", "category": "Chaussures", "subcategory": "Sandales", "price": 39.99, "cost": 12.00},
    {"id": "P018", "name": "Boots Chelsea", "category": "Chaussures", "subcategory": "Boots", "price": 119.99, "cost": 38.00},
    # Beauté
    {"id": "P019", "name": "Crème Hydratante Bio", "category": "Beauté", "subcategory": "Soins", "price": 29.99, "cost": 8.00},
    {"id": "P020", "name": "Sérum Vitamine C", "category": "Beauté", "subcategory": "Soins", "price": 39.99, "cost": 10.00},
    {"id": "P021", "name": "Parfum Floral 50ml", "category": "Beauté", "subcategory": "Parfums", "price": 69.99, "cost": 15.00},
    {"id": "P022", "name": "Rouge à Lèvres Mat", "category": "Beauté", "subcategory": "Maquillage", "price": 22.99, "cost": 5.00},
    {"id": "P023", "name": "Palette Ombres", "category": "Beauté", "subcategory": "Maquillage", "price": 34.99, "cost": 8.00},
    {"id": "P024", "name": "Shampoing Naturel", "category": "Beauté", "subcategory": "Cheveux", "price": 14.99, "cost": 3.00},
    # Maison
    {"id": "P025", "name": "Bougie Parfumée", "category": "Maison", "subcategory": "Décoration", "price": 24.99, "cost": 6.00},
    {"id": "P026", "name": "Coussin Velours", "category": "Maison", "subcategory": "Décoration", "price": 29.99, "cost": 8.00},
    {"id": "P027", "name": "Mug Céramique Artisanal", "category": "Maison", "subcategory": "Vaisselle", "price": 16.99, "cost": 4.00},
    {"id": "P028", "name": "Plaid Coton", "category": "Maison", "subcategory": "Textile", "price": 49.99, "cost": 15.00},
    {"id": "P029", "name": "Vase Design", "category": "Maison", "subcategory": "Décoration", "price": 34.99, "cost": 10.00},
    {"id": "P030", "name": "Set Serviettes Bio", "category": "Maison", "subcategory": "Textile", "price": 19.99, "cost": 5.00},
]


# --- Codes postaux simulés autour du magasin ---
LOCAL_POSTCODES = [
    "75001", "75002", "75003", "75004", "75005", "75006",
    "75007", "75008", "75009", "75010", "75011", "75012",
]
TOURIST_POSTCODES = [
    "69001", "13001", "33000", "31000",  # Autres villes FR
    "10115", "W1A",  "08001", "20121",   # Berlin, London, Barcelona, Milan
]


# --- Constantes d'analyse ---
AGE_BRACKETS = ["18-24", "25-34", "35-44", "45+"]

BEHAVIOR_SEGMENTS = {
    "one_time": (1, 1),       # 1 achat
    "occasional": (2, 4),     # 2-4 achats
    "loyal": (5, None),       # 5+ achats
}


# --- Affinités produits (pour simulation de paniers réalistes) ---
PRODUCT_AFFINITIES = {
    "P001": ["P002", "P006", "P015"],     # T-shirt → jean, short, sneakers
    "P002": ["P001", "P010", "P015"],     # Jean → t-shirt, ceinture, sneakers
    "P004": ["P017", "P011", "P022"],     # Robe → sandales, écharpe, rouge à lèvres
    "P009": ["P011", "P022", "P021"],     # Sac → écharpe, rouge à lèvres, parfum
    "P019": ["P020", "P024"],             # Crème → sérum, shampoing
    "P025": ["P026", "P027", "P029"],     # Bougie → coussin, mug, vase
    "P015": ["P001", "P006", "P014"],     # Sneakers → t-shirt, short, casquette
}
