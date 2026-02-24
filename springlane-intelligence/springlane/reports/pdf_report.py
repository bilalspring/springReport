"""
Générateur de rapport PDF — SpringLane Purchase Intelligence Report.
"""
import os
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, HRFlowable,
)
from reportlab.lib import colors


# --- Couleurs SpringLane ---
PRIMARY = HexColor("#1A1A2E")
ACCENT = HexColor("#E94560")
ACCENT2 = HexColor("#0F3460")
LIGHT_BG = HexColor("#F5F5F5")
SUCCESS = HexColor("#2ECC71")
WARNING = HexColor("#F39C12")
DANGER = HexColor("#E74C3C")
TEXT_GRAY = HexColor("#555555")

CHART_COLORS = ["#E94560", "#0F3460", "#1A1A2E", "#F39C12", "#2ECC71",
                "#9B59B6", "#3498DB", "#1ABC9C"]


def _create_styles():
    """Crée les styles de texte pour le rapport."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        "SLTitle", parent=styles["Title"],
        fontSize=24, textColor=PRIMARY, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "SLSubtitle", parent=styles["Normal"],
        fontSize=11, textColor=TEXT_GRAY, spaceAfter=20,
    ))
    styles.add(ParagraphStyle(
        "SLHeading", parent=styles["Heading1"],
        fontSize=16, textColor=ACCENT2, spaceBefore=16, spaceAfter=8,
        borderWidth=0, borderPadding=0,
    ))
    styles.add(ParagraphStyle(
        "SLHeading2", parent=styles["Heading2"],
        fontSize=13, textColor=PRIMARY, spaceBefore=10, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        "SLBody", parent=styles["Normal"],
        fontSize=9, textColor=PRIMARY, leading=13,
    ))
    styles.add(ParagraphStyle(
        "SLSmall", parent=styles["Normal"],
        fontSize=8, textColor=TEXT_GRAY, leading=11,
    ))
    styles.add(ParagraphStyle(
        "SLMetric", parent=styles["Normal"],
        fontSize=20, textColor=ACCENT, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "SLMetricLabel", parent=styles["Normal"],
        fontSize=8, textColor=TEXT_GRAY, alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "SLAlert", parent=styles["Normal"],
        fontSize=9, textColor=DANGER, leading=12,
    ))
    return styles


def _fig_to_image(fig, width=16 * cm, height=8 * cm):
    """Convertit une figure matplotlib en Image reportlab."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=width, height=height)


def _kpi_card(value, label, styles):
    """Crée une cellule KPI pour les tableaux de métriques."""
    return [
        Paragraph(str(value), styles["SLMetric"]),
        Paragraph(label, styles["SLMetricLabel"]),
    ]


def _make_kpi_row(kpis, styles):
    """Crée une rangée de KPI cards."""
    cells = [_kpi_card(v, l, styles) for v, l in kpis]
    # Flatten into a 2-row table
    row1 = [c[0] for c in cells]
    row2 = [c[1] for c in cells]
    col_w = 16 * cm / len(cells)
    t = Table([row1, row2], colWidths=[col_w] * len(cells))
    t.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
    ]))
    return t


def _simple_table(headers, rows, col_widths=None):
    """Crée un tableau formaté."""
    data = [headers] + rows
    if col_widths is None:
        col_widths = [16 * cm / len(headers)] * len(headers)
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT2),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#DDDDDD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


# ======================================================================
# SECTIONS DU RAPPORT
# ======================================================================

def _section_cover(story, styles, store_name, config_info):
    """Page de couverture."""
    story.append(Spacer(1, 4 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph("Retail Purchase Intelligence Report", styles["SLTitle"]))
    story.append(Paragraph(
        f"Magasin : {store_name}<br/>"
        f"Rapport généré le : {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>"
        f"Période : {config_info}",
        styles["SLSubtitle"],
    ))
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT))
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph(
        "Ce rapport est généré automatiquement par le moteur d'intelligence "
        "SpringLane à partir des données collectées via l'application mobile. "
        "Il fournit des insights actionnables pour optimiser la gestion des stocks, "
        "comprendre le comportement client et améliorer la performance commerciale.",
        styles["SLBody"],
    ))
    story.append(PageBreak())


def _section_demographics(story, styles, demo):
    """Section 1 — Démographie."""
    story.append(Paragraph("1. Profil Client & Démographie", styles["SLHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 0.5 * cm))

    # KPIs
    kpis = [
        (demo["total_customers"], "Clients inscrits"),
        (demo["active_customers"], "Clients actifs"),
        (demo["returning_customers"], "Clients récurrents"),
        (f"{demo['tourist_pct']}%", "Touristes"),
    ]
    story.append(_make_kpi_row(kpis, styles))
    story.append(Spacer(1, 0.5 * cm))

    # Graphique répartition âge + genre
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Âge
    age_data = demo["age_distribution_pct"]
    ax1.bar(age_data.keys(), age_data.values(), color=CHART_COLORS[:4])
    ax1.set_title("Répartition par âge", fontsize=11, fontweight="bold")
    ax1.set_ylabel("%")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))

    # Genre
    gender_data = demo["gender_distribution_pct"]
    colors_g = [CHART_COLORS[0], CHART_COLORS[1], CHART_COLORS[2]][:len(gender_data)]
    ax2.pie(gender_data.values(), labels=gender_data.keys(),
            colors=colors_g, autopct="%1.1f%%", startangle=90)
    ax2.set_title("Répartition par genre", fontsize=11, fontweight="bold")

    fig.tight_layout()
    story.append(_fig_to_image(fig))

    # Heatmap codes postaux
    story.append(Paragraph("Concentration géographique (Top 10 codes postaux)", styles["SLHeading2"]))
    pc_data = demo.get("postcode_heatmap", {})
    if pc_data:
        rows = [[pc, str(count)] for pc, count in list(pc_data.items())[:10]]
        story.append(_simple_table(["Code Postal", "Nb Clients"], rows,
                                    [8 * cm, 8 * cm]))
    story.append(PageBreak())


def _section_purchase_behavior(story, styles, behavior):
    """Section 2 — Comportement d'achat."""
    story.append(Paragraph("2. Comportement d'Achat", styles["SLHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 0.5 * cm))

    kpis = [
        (behavior["total_transactions"], "Transactions"),
        (f"{behavior['avg_basket_value']}€", "Panier moyen"),
        (behavior["avg_items_per_basket"], "Articles/panier"),
        (f"{behavior.get('avg_repurchase_cycle_days', 'N/A')}j", "Cycle réachat"),
    ]
    story.append(_make_kpi_row(kpis, styles))
    story.append(Spacer(1, 0.5 * cm))

    # Segmentation
    story.append(Paragraph("Segmentation comportementale", styles["SLHeading2"]))
    seg = behavior["segments"]
    fig, ax = plt.subplots(figsize=(8, 4))
    labels = ["Acheteurs uniques", "Occasionnels", "Fidèles"]
    values = [seg["one_time"]["pct"], seg["occasional"]["pct"], seg["loyal"]["pct"]]
    bar_colors = [CHART_COLORS[3], CHART_COLORS[1], CHART_COLORS[4]]
    bars = ax.barh(labels, values, color=bar_colors, height=0.5)
    ax.set_xlabel("%")
    ax.set_title("Segmentation des clients", fontsize=11, fontweight="bold")
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{val}%", va="center", fontsize=10)
    ax.set_xlim(0, max(values) * 1.2)
    fig.tight_layout()
    story.append(_fig_to_image(fig))

    # Distribution valeur panier
    story.append(Paragraph("Distribution de la valeur des paniers", styles["SLHeading2"]))
    bvd = behavior["basket_value_distribution"]
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.bar(bvd.keys(), bvd.values(), color=CHART_COLORS[0], alpha=0.85)
    ax.set_ylabel("Nombre de transactions")
    ax.set_xlabel("Valeur du panier (€)")
    ax.set_title("Distribution des paniers", fontsize=11, fontweight="bold")
    fig.tight_layout()
    story.append(_fig_to_image(fig))
    story.append(PageBreak())


def _section_product_performance(story, styles, products):
    """Section 3 — Performance produit."""
    story.append(Paragraph("3. Performance Produits", styles["SLHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 0.5 * cm))

    # Top 10
    story.append(Paragraph("Top 10 Produits par Revenu", styles["SLHeading2"]))
    top10 = products["top_10_products"]
    rows = [
        [str(p["rank"]), p["product_name"], p["category"],
         str(p["total_qty"]), f"{p['total_revenue']}€"]
        for p in top10
    ]
    story.append(_simple_table(
        ["#", "Produit", "Catégorie", "Unités", "Revenu"],
        rows,
        [1 * cm, 6 * cm, 3 * cm, 2 * cm, 3 * cm],
    ))
    story.append(Spacer(1, 0.5 * cm))

    # Revenu par catégorie
    story.append(Paragraph("Revenu par Catégorie", styles["SLHeading2"]))
    rev_cat = products["revenue_by_category"]
    fig, ax = plt.subplots(figsize=(8, 4))
    cats = list(rev_cat.keys())
    vals = list(rev_cat.values())
    ax.barh(cats, vals, color=CHART_COLORS[:len(cats)])
    ax.set_xlabel("Revenu (€)")
    ax.set_title("Revenu par catégorie", fontsize=11, fontweight="bold")
    for i, v in enumerate(vals):
        ax.text(v + max(vals) * 0.01, i, f"{v:,.0f}€", va="center", fontsize=9)
    fig.tight_layout()
    story.append(_fig_to_image(fig))

    # Bestsellers ratio
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        f"<b>Part de revenu des bestsellers (Top 20%) :</b> "
        f"{products['bestseller_revenue_share']}%",
        styles["SLBody"],
    ))
    story.append(Paragraph(
        f"<b>Produits long-tail (≤5 unités vendues) :</b> "
        f"{products['long_tail_count']} produits",
        styles["SLBody"],
    ))
    story.append(PageBreak())


def _section_basket(story, styles, baskets):
    """Section 4 — Analyse de panier."""
    story.append(Paragraph("4. Analyse de Panier & Cross-Sell", styles["SLHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 0.5 * cm))

    avg = baskets["avg_basket"]
    kpis = [
        (avg["items"], "Articles/panier"),
        (avg["unique_products"], "Produits uniques"),
        (avg["categories"], "Catégories"),
        (f"{avg['value']}€", "Valeur moyenne"),
    ]
    story.append(_make_kpi_row(kpis, styles))
    story.append(Spacer(1, 0.5 * cm))

    # Top paires
    story.append(Paragraph("Produits fréquemment achetés ensemble", styles["SLHeading2"]))
    pairs = baskets.get("top_product_pairs", [])[:7]
    if pairs:
        rows = [[p["product_a"], p["product_b"], str(p["frequency"])] for p in pairs]
        story.append(_simple_table(
            ["Produit A", "Produit B", "Fréquence"],
            rows,
            [6 * cm, 6 * cm, 3 * cm],
        ))

    # Règles d'association
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Règles d'association", styles["SLHeading2"]))
    rules = baskets.get("association_rules", [])
    for rule in rules:
        story.append(Paragraph(f"• {rule}", styles["SLBody"]))

    # Combinaisons catégories
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Top combinaisons de catégories", styles["SLHeading2"]))
    cat_combos = baskets.get("top_category_combos", {})
    if cat_combos:
        rows = [[k, str(v)] for k, v in cat_combos.items()]
        story.append(_simple_table(
            ["Combinaison", "Fréquence"], rows, [10 * cm, 5 * cm],
        ))

    story.append(PageBreak())


def _section_time_trends(story, styles, trends):
    """Section 5 — Tendances temporelles."""
    story.append(Paragraph("5. Tendances Temporelles", styles["SLHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 0.5 * cm))

    kpis = [
        (trends["peak_hour_label"], "Heure de pointe"),
        (trends["peak_day"], "Jour de pointe"),
        (trends["trend_signal"], "Tendance"),
    ]
    story.append(_make_kpi_row(kpis, styles))
    story.append(Spacer(1, 0.5 * cm))

    # Ventes par heure
    hourly = trends["sales_by_hour"]
    fig, ax = plt.subplots(figsize=(10, 3.5))
    hours = sorted(hourly["transactions"].keys())
    tx_vals = [hourly["transactions"].get(h, 0) for h in hours]
    ax.fill_between(hours, tx_vals, alpha=0.3, color=CHART_COLORS[0])
    ax.plot(hours, tx_vals, color=CHART_COLORS[0], linewidth=2)
    ax.set_xlabel("Heure")
    ax.set_ylabel("Transactions")
    ax.set_title("Ventes par heure de la journée", fontsize=11, fontweight="bold")
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([f"{h}h" for h in range(0, 24, 2)])
    fig.tight_layout()
    story.append(_fig_to_image(fig))

    # Ventes par jour
    daily = trends["sales_by_day"]
    fig, ax = plt.subplots(figsize=(10, 3.5))
    days = list(daily["revenue"].keys())
    rev_vals = list(daily["revenue"].values())
    ax.bar(days, rev_vals, color=CHART_COLORS[1], alpha=0.85)
    ax.set_ylabel("Revenu (€)")
    ax.set_title("Revenu par jour de la semaine", fontsize=11, fontweight="bold")
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    story.append(_fig_to_image(fig))

    # Évolution mensuelle
    monthly = trends.get("monthly_summary", [])
    if monthly:
        fig, ax1 = plt.subplots(figsize=(10, 4))
        months = [m["month"] for m in monthly]
        revenues = [m["revenue"] for m in monthly]
        customers = [m["unique_customers"] for m in monthly]

        ax1.bar(months, revenues, color=CHART_COLORS[0], alpha=0.7, label="Revenu (€)")
        ax1.set_ylabel("Revenu (€)", color=CHART_COLORS[0])
        ax1.tick_params(axis="y", labelcolor=CHART_COLORS[0])

        ax2 = ax1.twinx()
        ax2.plot(months, customers, color=CHART_COLORS[4], marker="o",
                 linewidth=2, label="Clients uniques")
        ax2.set_ylabel("Clients uniques", color=CHART_COLORS[4])
        ax2.tick_params(axis="y", labelcolor=CHART_COLORS[4])

        ax1.set_title("Évolution mensuelle", fontsize=11, fontweight="bold")
        plt.xticks(rotation=30, ha="right")
        fig.tight_layout()
        story.append(_fig_to_image(fig, height=9 * cm))

    story.append(PageBreak())


def _section_demand_forecast(story, styles, forecast):
    """Section 6 — Prévisions & optimisation stock."""
    story.append(Paragraph("6. Prévisions de Demande & Stock", styles["SLHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 0.5 * cm))

    kpis = [
        (f"🔴 {forecast['n_stockout_alerts']}", "Alertes rupture"),
        (f"🟠 {forecast['n_overstock_alerts']}", "Alertes surstock"),
    ]
    story.append(_make_kpi_row(kpis, styles))
    story.append(Spacer(1, 0.5 * cm))

    # Alertes
    story.append(Paragraph("Alertes Prédictives", styles["SLHeading2"]))
    for alert in forecast.get("alerts", [])[:10]:
        severity_style = styles["SLAlert"] if "CRITIQUE" in alert["severity"] else styles["SLBody"]
        story.append(Paragraph(
            f"{alert['severity']} — {alert['message']}<br/>"
            f"<i>Action : {alert['action']}</i>",
            severity_style,
        ))
        story.append(Spacer(1, 2 * mm))

    story.append(Spacer(1, 0.5 * cm))

    # Recommandations de réapprovisionnement
    story.append(Paragraph("Recommandations de Réapprovisionnement", styles["SLHeading2"]))
    reorder = forecast.get("reorder_recommendations", [])[:10]
    if reorder:
        rows = [
            [r["product_name"], str(r["reorder_qty"]), f"{r['days_until_stockout']}j"]
            for r in reorder
        ]
        story.append(_simple_table(
            ["Produit", "Qté à commander", "Jours avant rupture"],
            rows,
            [7 * cm, 4 * cm, 4 * cm],
        ))

    story.append(PageBreak())


def _section_executive_summary(story, styles, all_results):
    """Section 7 — Résumé exécutif auto-généré."""
    story.append(Paragraph("7. Résumé Exécutif", styles["SLHeading"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 0.5 * cm))

    demo = all_results["demographics"]
    behavior = all_results["behavior"]
    products = all_results["products"]
    forecast = all_results["forecast"]
    trends = all_results["trends"]

    # Performance drivers
    story.append(Paragraph("✅ Top Facteurs de Performance", styles["SLHeading2"]))
    drivers = [
        f"Base active de {demo['active_customers']} clients "
        f"({demo['returning_customers']} récurrents)",
        f"Panier moyen de {behavior['avg_basket_value']}€",
        f"Les bestsellers (Top 20%) représentent "
        f"{products['bestseller_revenue_share']}% du CA",
        f"Taux de conversion scan→achat : {behavior['scan_to_purchase_rate']}%",
        f"Tendance : {trends['trend_signal']}",
    ]
    for d in drivers:
        story.append(Paragraph(f"• {d}", styles["SLBody"]))

    story.append(Spacer(1, 0.5 * cm))

    # Risques
    story.append(Paragraph("⚠️ Top Risques", styles["SLHeading2"]))
    risks = []
    if forecast["n_stockout_alerts"] > 0:
        risks.append(f"{forecast['n_stockout_alerts']} produit(s) à risque de rupture")
    if forecast["n_overstock_alerts"] > 0:
        risks.append(f"{forecast['n_overstock_alerts']} produit(s) en surstock")
    seg = behavior["segments"]
    if seg["one_time"]["pct"] > 50:
        risks.append(f"{seg['one_time']['pct']}% de clients one-time — "
                     "risque de fidélisation")
    if products["long_tail_count"] > 10:
        risks.append(f"{products['long_tail_count']} produits long-tail à faible rotation")
    for r in risks[:3]:
        story.append(Paragraph(f"• {r}", styles["SLBody"]))

    story.append(Spacer(1, 0.5 * cm))

    # Opportunités
    story.append(Paragraph("💡 Top Opportunités", styles["SLHeading2"]))
    opportunities = [
        f"Heure de pointe à {trends['peak_hour_label']} — "
        "optimiser le staffing et les promotions flash",
        f"Jour de pointe : {trends['peak_day']} — "
        "planifier les opérations commerciales",
    ]
    if demo["tourist_pct"] > 15:
        opportunities.append(
            f"{demo['tourist_pct']}% de touristes — "
            "opportunité offre spéciale visiteurs"
        )
    for o in opportunities:
        story.append(Paragraph(f"• {o}", styles["SLBody"]))

    story.append(Spacer(1, 1 * cm))

    # Actions immédiates
    story.append(Paragraph("🔄 Actions Immédiates", styles["SLHeading2"]))
    reorder = forecast.get("reorder_recommendations", [])[:5]
    if reorder:
        story.append(Paragraph("<b>Commander maintenant :</b>", styles["SLBody"]))
        for r in reorder:
            story.append(Paragraph(
                f"  → {r['product_name']} : {r['reorder_qty']} unités "
                f"(rupture estimée dans {r['days_until_stockout']}j)",
                styles["SLBody"],
            ))


# ======================================================================
# FONCTION PRINCIPALE
# ======================================================================

def generate_report(
    all_results: Dict[str, Any],
    output_path: str,
    store_name: str = "Paris Marais",
    config_info: str = "",
) -> str:
    """
    Génère le rapport PDF complet.

    Args:
        all_results: Dictionnaire contenant les résultats de chaque module analytique.
        output_path: Chemin du fichier PDF de sortie.
        store_name: Nom du magasin.
        config_info: Information de contexte (période, etc.)

    Returns:
        Chemin du fichier PDF généré.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = _create_styles()
    story = []

    # Construire chaque section
    _section_cover(story, styles, store_name, config_info)
    _section_demographics(story, styles, all_results["demographics"])
    _section_purchase_behavior(story, styles, all_results["behavior"])
    _section_product_performance(story, styles, all_results["products"])
    _section_basket(story, styles, all_results["baskets"])
    _section_time_trends(story, styles, all_results["trends"])
    _section_demand_forecast(story, styles, all_results["forecast"])
    _section_executive_summary(story, styles, all_results)

    # Footer
    story.append(Spacer(1, 2 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Paragraph(
        f"SpringLane Intelligence Engine v0.1.0 — Rapport généré le "
        f"{datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles["SLSmall"],
    ))

    doc.build(story)
    print(f"📄 Rapport PDF généré : {output_path}")
    return output_path
