# SpringLane — Retail Purchase Intelligence Engine (POC)

> Algorithme d'analyse comportementale des achats retail, générant des rapports d'intelligence automatisés à partir des données collectées via l'application SpringLane.

## 🎯 Objectif

Ce POC simule le pipeline complet de l'intelligence d'achat SpringLane :

1. **Simulation de données** — Profils clients, transactions, scans produits
2. **Moteur analytique** — Calcul des métriques (démographie, comportement, performance produits, paniers, tendances temporelles, prévisions)
3. **Génération de rapports** — PDF professionnel auto-généré avec graphiques

## 📁 Structure du projet

```
springlane-intelligence/
├── springlane/
│   ├── __init__.py
│   ├── config.py              # Configuration et constantes
│   ├── data/
│   │   ├── __init__.py
│   │   └── simulator.py       # Génération de données simulées
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── demographics.py    # Analyse démographique clients
│   │   ├── purchase_behavior.py  # Comportement d'achat
│   │   ├── product_performance.py # Performance produits
│   │   ├── basket_analysis.py # Analyse de panier
│   │   ├── time_trends.py     # Tendances temporelles
│   │   └── demand_forecast.py # Prévisions de demande
│   └── reports/
│       ├── __init__.py
│       └── pdf_report.py      # Générateur de rapport PDF
├── main.py                    # Point d'entrée
├── requirements.txt
├── .gitignore
└── README.md
```

## 🚀 Installation

```bash
# Cloner le repo
git clone https://github.com/<your-org>/springlane-intelligence.git
cd springlane-intelligence

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## ▶️ Utilisation

```bash
# Lancer le POC complet (simulation + analyse + rapport PDF)
python main.py

# Options
python main.py --customers 500 --months 6 --store "Paris Marais"
```

Le rapport PDF sera généré dans le dossier `output/`.

## 📊 Métriques couvertes

| Module | Métriques |
|--------|-----------|
| Démographie | Répartition âge/genre, heatmap géo, clients nouveaux vs récurrents |
| Comportement | Fréquence d'achat, panier moyen, segmentation (one-time/occasionnel/fidèle) |
| Produits | Classement produits, sell-through rate, performance par âge/lieu/heure |
| Paniers | Combinaisons fréquentes, cross-sell affinity, bundles manqués |
| Tendances | Ventes par heure/jour/mois, pics, saisonnalité |
| Prévisions | Forecast de demande, alertes stock-out, score surstock |

## 🔗 Intégration avec l'App

Ce moteur analytique est conçu pour être intégré comme module backend de l'application SpringLane. L'interface entre ce module et l'app se fait via :

- **Input** : DataFrames pandas (remplacer le simulateur par les vraies données de l'app)
- **Output** : Rapport PDF + dictionnaire JSON des métriques

## 📝 Licence

Propriétaire — SpringLane © 2026
