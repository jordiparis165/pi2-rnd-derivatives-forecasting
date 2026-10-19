from __future__ import annotations

import json
import shutil
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, Image, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "Livrables_suivi_23-10-2026"
RESULTS = ROOT / "results"
DIAG = json.loads((RESULTS / "diagnostics.json").read_text(encoding="utf-8"))
TERM = json.loads((RESULTS / "rnd_term_structure_diagnostics.json").read_text(encoding="utf-8"))
NAVY = colors.HexColor("#153A5B")
CYAN = colors.HexColor("#168AAD")
LIGHT = colors.HexColor("#EDF3F6")
TEXT = colors.HexColor("#22282D")
MUTED = colors.HexColor("#5F6B73")

pdfmetrics.registerFont(TTFont("TimesNR", r"C:\Windows\Fonts\times.ttf"))
pdfmetrics.registerFont(TTFont("TimesNR-Bold", r"C:\Windows\Fonts\timesbd.ttf"))
pdfmetrics.registerFont(TTFont("TimesNR-Italic", r"C:\Windows\Fonts\timesi.ttf"))

base = getSampleStyleSheet()
ST = {
    "title": ParagraphStyle("PaperTitle", parent=base["Title"], fontName="TimesNR-Bold", fontSize=20, leading=24, textColor=TEXT, alignment=TA_CENTER, spaceAfter=10),
    "authors": ParagraphStyle("Authors", parent=base["Normal"], fontName="TimesNR", fontSize=10.5, leading=14, alignment=TA_CENTER, textColor=TEXT, spaceAfter=7),
    "affiliation": ParagraphStyle("Affiliation", parent=base["Normal"], fontName="TimesNR-Italic", fontSize=9.5, leading=13, alignment=TA_CENTER, textColor=MUTED, spaceAfter=10),
    "abstract": ParagraphStyle("Abstract", parent=base["BodyText"], fontName="TimesNR", fontSize=9.2, leading=12.2, alignment=TA_JUSTIFY, textColor=TEXT, leftIndent=10, rightIndent=10, borderColor=colors.HexColor("#C3CDD3"), borderWidth=0.6, borderPadding=9, backColor=colors.HexColor("#F7F9FA"), spaceAfter=8),
    "meta": ParagraphStyle("Meta", parent=base["BodyText"], fontName="TimesNR", fontSize=8.8, leading=11.5, alignment=TA_LEFT, textColor=TEXT, spaceAfter=4),
    "h1": ParagraphStyle("Section", parent=base["Heading1"], fontName="TimesNR-Bold", fontSize=13.2, leading=16, textColor=NAVY, spaceBefore=12, spaceAfter=6, keepWithNext=True),
    "h2": ParagraphStyle("Subsection", parent=base["Heading2"], fontName="TimesNR-Bold", fontSize=11.2, leading=14, textColor=TEXT, spaceBefore=9, spaceAfter=4, keepWithNext=True),
    "body": ParagraphStyle("PaperBody", parent=base["BodyText"], fontName="TimesNR", fontSize=9.6, leading=13.1, alignment=TA_JUSTIFY, textColor=TEXT, firstLineIndent=14, spaceAfter=6),
    "body0": ParagraphStyle("PaperBodyNoIndent", parent=base["BodyText"], fontName="TimesNR", fontSize=9.6, leading=13.1, alignment=TA_JUSTIFY, textColor=TEXT, spaceAfter=6),
    "equation": ParagraphStyle("Equation", parent=base["BodyText"], fontName="TimesNR-Italic", fontSize=11.2, leading=15, alignment=TA_CENTER, textColor=TEXT, spaceBefore=7, spaceAfter=8),
    "caption": ParagraphStyle("Caption", parent=base["BodyText"], fontName="TimesNR", fontSize=8.1, leading=10.3, alignment=TA_CENTER, textColor=MUTED, spaceBefore=3, spaceAfter=8),
    "small": ParagraphStyle("Small", parent=base["BodyText"], fontName="TimesNR", fontSize=8, leading=10.4, textColor=TEXT),
    "refs": ParagraphStyle("Refs", parent=base["BodyText"], fontName="TimesNR", fontSize=8.2, leading=10.6, textColor=TEXT, leftIndent=12, firstLineIndent=-12, spaceAfter=4),
}


def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    if doc.page > 1:
        canvas.setStrokeColor(colors.HexColor("#CBD4D9")); canvas.setLineWidth(0.4)
        canvas.line(2.4 * cm, h - 1.25 * cm, w - 2.4 * cm, h - 1.25 * cm)
        canvas.setFont("TimesNR-Italic", 7.7); canvas.setFillColor(MUTED)
        canvas.drawString(2.4 * cm, h - 1.05 * cm, "Estimation et dynamique des distributions risque-neutre — PI² n°176")
    canvas.setFont("TimesNR", 8); canvas.setFillColor(MUTED)
    canvas.drawCentredString(w / 2, 1.0 * cm, str(doc.page))
    canvas.restoreState()


def fig(path, width_cm, height_cm, caption):
    return [Image(str(RESULTS / path), width=width_cm * cm, height=height_cm * cm), Paragraph(caption, ST["caption"])]


def build():
    out = OUT / "Papier_recherche_PI2_176.pdf"
    doc = BaseDocTemplate(str(out), pagesize=A4, leftMargin=2.35 * cm, rightMargin=2.35 * cm, topMargin=1.55 * cm, bottomMargin=1.55 * cm, title="Estimation et dynamique des distributions risque-neutre")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="paper")
    doc.addPageTemplates(PageTemplate(id="paper", frames=frame, onPage=header_footer))
    b, b0, h1, h2 = ST["body"], ST["body0"], ST["h1"], ST["h2"]
    story = [
        Spacer(1, 0.45 * cm),
        Paragraph("Estimation et dynamique des distributions risque-neutre<br/>à partir d’options SPX", ST["title"]),
        Paragraph("Rayan Ait Arkoub · Matthieu Balliste · Ilan Chahdi · Nathan Denoux · Jordi Paris", ST["authors"]),
        Paragraph("ESILV — Pôle Léonard de Vinci · Projet PI² n°176<br/>Tuteur : Matthieu Garcin · 20 octobre 2026", ST["affiliation"]),
        Paragraph("<b>Résumé.</b> Nous développons un pipeline reproductible d’estimation de distributions risque-neutre (RND) à partir d’options sur l’indice S&P 500. Une photographie différée de Cboe du 16 octobre 2026 est nettoyée, puis le forward et le facteur d’actualisation sont estimés par parité call-put. Une paramétrisation SVI à cinq paramètres fournit une coupe de volatilité commune à l’ensemble des strikes. La densité est extraite par Breeden–Litzenberger et calculée indépendamment en Python et en Julia. Pour l’échéance à 91 jours, 338 observations alimentent la calibration, la RMSE de prix vaut 1,144 point et la masse brute de densité atteint 0,9953. Nous étendons l’exercice à six maturités entre 31 et 182 jours et construisons une surface tridimensionnelle en log-moneyness. Cette surface représente la structure par terme à date fixe ; l’étude dynamique nécessitera un historique quotidien.", ST["abstract"]),
        Paragraph("<b>Mots-clés :</b> distribution risque-neutre ; options SPX ; Breeden–Litzenberger ; SVI ; structure par terme ; Julia.", ST["meta"]),
        Paragraph("<b>Codes JEL :</b> C14, C58, G13, G17.", ST["meta"]),
        Paragraph("1. Introduction", h1),
        Paragraph("Les prix d’options contiennent une information prospective sur la distribution du sous-jacent à l’échéance. Dans Black–Scholes, cette distribution est lognormale et une volatilité unique devrait expliquer tous les strikes. L’existence empirique du smile invalide cette restriction. Une volatilité implicite peut ajuster chaque option séparément, mais elle ne constitue pas un modèle commun parcimonieux de la chaîne.", b),
        Paragraph("Ce projet poursuit cinq objectifs : constituer une base historique de prix d’options, comparer trois méthodes d’extraction de RND, mesurer leur stabilité, prévoir leur dynamique au moyen d’un modèle factoriel et tester une application à la couverture. Le présent article documente le premier jalon : une estimation complète sur SPX, sa validation en Julia et une extension tridimensionnelle selon la maturité.", b),
        Paragraph("Notre contribution à ce stade est triple. Premièrement, nous mettons en place un pipeline reproductible allant de la cotation brute à une densité contrôlée. Deuxièmement, nous séparons explicitement l’ajustement option par option d’une calibration commune à cinq paramètres. Troisièmement, nous construisons une structure par terme de RND sur une grille homogène de log-moneyness, tout en distinguant cette coupe de la future dynamique temporelle.", b),
        Paragraph("2. Revue de littérature", h1),
        Paragraph("Breeden et Litzenberger (1978) relient les prix d’états à la dérivée seconde des calls. Figlewski (2010, 2018) souligne les difficultés empiriques : bruit bid-ask, interpolation, support fini et traitement des queues. Cui et Yu (2021) proposent une alternative Fourier-cosinus fondée sur l’intégration des prix plutôt que leur double dérivation. Avellaneda et al. (2001) construisent une mesure calibrée par minimisation d’entropie relative. Pour la dynamique, Giacomini, Härdle et Krätschmer (2009) réduisent les densités en facteurs semiparamétriques, tandis que Taboga (2016) étudie l’incertitude et le risque de multimodalité artificielle.", b),
        Paragraph("Le projet reprendra ces trois familles — Breeden–Litzenberger, Fourier et distorsion historique — sur les mêmes dates, maturités et grilles afin d’éviter qu’une différence de préparation des données ne soit confondue avec une différence de méthode.", b),
        PageBreak(),
        Paragraph("3. Cadre théorique", h1),
        Paragraph("Sous la mesure risque-neutre Q, le prix d’un call européen est l’espérance actualisée de son payoff :", b0),
        Paragraph("C_t(K,T) = D(t,T) × E^Q_t[(S_T − K)^+].", ST["equation"]),
        Paragraph("Sous des conditions de régularité, la densité du prix terminal est obtenue par :", b0),
        Paragraph("q_t(K,T) = [1 / D(t,T)] × ∂²C_t(K,T) / ∂K².", ST["equation"]),
        Paragraph("Cette identité est indépendante du processus choisi pour le sous-jacent. Sa mise en œuvre est toutefois mal conditionnée, car une double dérivation amplifie le bruit des cotations. Nous dérivons donc une courbe de calls lissée et non les prix bruts.", b),
        Paragraph("3.1. Forward et facteur d’actualisation", h2),
        Paragraph("La parité call-put fournit une relation affine en strike :", b0),
        Paragraph("C_t(K,T) − P_t(K,T) = D(t,T)[F_t,T − K].", ST["equation"]),
        Paragraph("Une régression pondérée autour de la monnaie estime simultanément D et F. Les poids pénalisent les paires présentant des spreads larges. Cette procédure évite d’introduire une courbe de taux externe incohérente avec les cotations de la coupe.", b),
        Paragraph("3.2. Paramétrisation SVI", h2),
        Paragraph("La variance totale implicite est représentée par cinq paramètres :", b0),
        Paragraph("w(k) = a + b[ρ(k − m) + √((k − m)² + σ²)],    k = log(K/F).", ST["equation"]),
        Paragraph("SVI constitue ici un outil de lissage commun à la coupe. La méthode d’extraction reste Breeden–Litzenberger. La distinction est importante : une volatilité par option ajuste exactement chaque contrat, tandis que SVI cherche une structure partagée par tous les strikes.", b),
        Paragraph("4. Données et construction de l’échantillon", h1),
        Paragraph("La source est l’API publique différée de Cboe. La photographie principale est horodatée au 16 octobre 2026 à 17:12:17. L’accès Bloomberg n’est pas disponible dans l’environnement actuel. L’API publique permet de valider une coupe, mais ne remplace pas l’historique nécessaire à l’étude dynamique.", b),
    ]
    rows = [["Variable", "Valeur"], ["Spot SPX", f"{DIAG['spot']:,.2f}"], ["Échéance", "15 janvier 2027"], ["Maturité", "91 jours"], ["Contrats bruts", f"{DIAG['selected_contracts_before_filtering']:,}"], ["Cotations valides", f"{DIAG['valid_contract_quotes']:,}"], ["Paires call-put", f"{DIAG['matched_call_put_strikes']:,}"], ["Points calibrés", f"{DIAG['calibration_points']:,}"]]
    table = Table(rows, colWidths=[7.3 * cm, 7.3 * cm], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), NAVY), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("FONTNAME", (0,0), (-1,0), "TimesNR-Bold"), ("FONTNAME", (0,1), (-1,-1), "TimesNR"), ("FONTSIZE", (0,0), (-1,-1), 8.6), ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#B8C3C9")), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT]), ("ALIGN", (1,1), (1,-1), "RIGHT"), ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4)]))
    story.extend([table, Paragraph("Tableau 1 — Composition de l’échantillon principal.", ST["caption"]),
        Paragraph("Les cotations avec bid nul, marché croisé, mid inférieur à 0,05 ou spread relatif supérieur à 35 % sont écartées. Le mid bid-ask est privilégié au dernier prix, dont l’horodatage sert de diagnostic de staleness. Les options hors de la monnaie sont utilisées : calls au-dessus du forward, puts transformés par parité en dessous.", b),
        PageBreak(),
        Paragraph("5. Analyse de la qualité des données", h1),
    ])
    story.extend(fig("01_data_quality.png", 16.0, 6.1, "Figure 1 — Spreads relatifs et ancienneté des derniers échanges pour l’échéance du 15 janvier 2027."))
    story.extend([
        Paragraph("La majorité des cotations proches de la monnaie présente un spread relatif faible. Les strikes éloignés deviennent plus fragiles, ce qui justifie un filtre explicite et une analyse de sensibilité. Le panneau droit confirme que certains derniers échanges sont anciens ; les utiliser sans contrôle créerait des irrégularités artificielles dans la dérivée seconde.", b),
        Paragraph("6. Méthodologie empirique", h1),
        Paragraph("Le pipeline suit huit étapes : sélection d’une échéance, validation des quotes, appariement call-put, estimation de F et D, conversion des OTM en calls synthétiques, inversion Black–Scholes, calibration SVI, puis reconstruction et double dérivation. Les densités sont contrôlées par leur masse, leur positivité, leur moyenne, la convexité des calls et l’erreur de repricing.", b),
        Paragraph("Le choix d’une grille en log-moneyness log(K/F) rend les coupes comparables malgré les variations du niveau de l’indice. Pour une série temporelle, chaque date devra en outre viser une maturité constante ou interpolée.", b),
        Paragraph("7. Résultats pour l’échéance à 91 jours", h1),
        Paragraph(f"La parité fournit F = {DIAG['forward_from_parity']:,.2f}, D = {DIAG['discount_factor_from_parity']:.5f} et un taux continu implicite de {100*DIAG['implied_continuous_rate']:.2f} %. La RMSE de parité est {DIAG['put_call_parity_rmse']:.3f} point. La RMSE de reconstruction des calls vaut {DIAG['call_price_rmse']:.3f} point.", b),
    ])
    story.extend(fig("02_svi_smile.png", 14.7, 8.2, "Figure 2 — Volatilités implicites et calibration SVI commune à cinq paramètres."))
    story.extend([
        Paragraph("Les paramètres estimés sont a = −0,02923, b = 0,12073, ρ = −0,05133, m = 0,08167 et σ = 0,26829. La courbe épouse précisément les 338 points retenus. L’ajustement visuel ne suffit toutefois pas : l’absence d’arbitrage doit être contrôlée sur la courbe de calls dérivée.", b),
        Paragraph("7.1. Courbe de calls et densité", h2),
    ])
    story.extend(fig("03_call_curve.png", 14.7, 8.2, "Figure 3 — Calls synthétiques et courbe reconstruite avant dérivation."))
    story.extend(fig("04_risk_neutral_density.png", 14.7, 8.2, "Figure 4 — RND SPX obtenue par Breeden–Litzenberger."))
    story.extend([
        Paragraph(f"La masse brute sur la grille vaut {DIAG['raw_density_mass_on_grid']:.5f}. La masse négative absolue est {DIAG['absolute_negative_mass']:.6f}. Environ {100*DIAG['negative_grid_fraction']:.1f} % des points de l’extrême queue droite sont numériquement négatifs, mais aucun ne dépasse 0,1 % du pic en amplitude. Après troncature des seules valeurs négatives et normalisation, la moyenne vaut {DIAG['normalized_density_mean']:,.2f}.", b),
        Paragraph("Ces diagnostics révèlent une limite réelle de la SVI brute dans les zones extrapolées. Une eSSVI avec contraintes d’arbitrage ou un lissage directement convexe des calls sera comparé au prototype. La troncature n’est utilisée ici que pour visualiser et calculer des moments ; elle ne doit pas devenir un substitut permanent à une calibration sans arbitrage.", b),
        PageBreak(),
        Paragraph("8. Structure tridimensionnelle des RND", h1),
        Paragraph("Le pipeline est répété pour six maturités : 31, 63, 91, 126, 154 et 182 jours. Les densités sont transformées dans l’espace de log-moneyness. Si s = F exp(k), le changement de variable donne q_k(k) = q_S(s)s. Chaque coupe est normalisée sur la grille commune k ∈ [−0,32 ; 0,24].", b),
    ])
    story.extend(fig("05_rnd_surface_3d_maturity.png", 16.2, 10.4, "Figure 5 — Surface 3D des RND selon la maturité. L’axe vertical représente l’échéance résiduelle, non le temps calendaire."))
    story.extend([
        Paragraph("La distribution est très concentrée à 31 jours, puis s’aplatit et s’élargit avec l’horizon. Cette évolution est cohérente avec l’accumulation d’incertitude. La position du mode se déplace légèrement en log-moneyness et la queue gauche conserve davantage de masse, ce qui reflète l’asymétrie des options sur indice.", b),
        Paragraph("Il serait incorrect d’interpréter cette figure comme une dynamique. Toutes les coupes proviennent de la même date d’observation. La future surface dynamique remplacera l’axe de maturité par la date, tout en maintenant une échéance cible constante.", b),
        PageBreak(),
    ])
    story.extend(fig("06_rnd_heatmap_maturity.png", 16.0, 8.2, "Figure 6 — Carte thermique de la structure par terme en log-moneyness."))
    story.extend([
        Paragraph("La carte thermique confirme le resserrement du pic à court terme et son élargissement progressif. Elle permet également de repérer d’éventuelles discontinuités entre maturités, qui pourraient signaler un problème de liquidité, d’interpolation ou d’arbitrage calendrier.", b),
        Paragraph("9. Validation informatique", h1),
        Paragraph("La dérivée seconde, la masse, la normalisation et les moments sont réimplémentés en Julia 1.10.10 sans package externe. L’écart absolu moyen avec Python est 3,3 × 10^-9 ; l’écart maximal est 2,1 × 10^-6 et se situe aux bords, où les conventions de différences finies diffèrent. Cette réplication indépendante réduit le risque d’une erreur silencieuse dans le prototype principal.", b),
        Paragraph("10. Vers une dynamique temporelle", h1),
        Paragraph("Avec un historique quotidien, chaque date produira une densité à horizon constant. Les densités seront évaluées sur une grille commune, puis réduites par analyse factorielle fonctionnelle. Les scores suivront un modèle AR ou VAR. Les prévisions seront comparées à une marche aléatoire fonctionnelle — la densité de la veille — au moyen des divergences KL et Jensen–Shannon, de la distance de Wasserstein et de l’erreur de repricing.", b),
        Paragraph("La surface cible du projet aura alors pour axes la date, la log-moneyness et la densité. Un intervalle d’incertitude sera construit par bootstrap des cotations ou par propagation de l’incertitude de calibration.", b),
        Paragraph("11. Application future à la couverture", h1),
        Paragraph("Nous comparerons une couverture fondée sur la RND courante, une couverture utilisant la RND prévue et un benchmark Black–Scholes. Les critères seront l’erreur de couverture cumulée, sa variance, le drawdown et les coûts de transaction. L’incertitude de la prévision devra limiter l’agressivité des ajustements.", b),
        PageBreak(),
        Paragraph("12. Limites et robustesse", h1),
        Paragraph("L’étude repose encore sur une seule date. Le seuil de spread de 35 % est provisoire et devra être testé. La SVI brute n’impose pas toutes les contraintes d’arbitrage butterfly. La surface 3D interpole seulement six maturités. Enfin, l’absence d’un historique empêche toute conclusion sur la stabilité ou le pouvoir prédictif des RND.", b),
        Paragraph("Les tests de robustesse prévus sont : plusieurs seuils de spread, comparaison mid/last, grilles alternatives, exclusion progressive des queues, lissage eSSVI, interpolation à maturité constante et comparaison des trois méthodes d’extraction sur exactement le même échantillon.", b),
        Paragraph("13. Conclusion", h1),
        Paragraph("Le premier prototype relie une chaîne SPX réelle à une densité contrôlée et reproductible. Les résultats Python et Julia concordent. L’extension à six maturités offre une première représentation tridimensionnelle économiquement interprétable. Le prochain jalon essentiel est l’acquisition d’un historique quotidien permettant de remplacer l’axe de maturité par un axe temporel et d’estimer les facteurs dynamiques.", b),
        Paragraph("Annexe A — Reproductibilité", h1),
        Paragraph("Le dépôt contient les snapshots bruts, les tables nettoyées, les scripts Python et Julia, les diagnostics, les figures et les commandes d’exécution. Le script run_prototype.ps1 reconstruit la coupe à 91 jours. Le script src/rnd_surface_3d.py produit la structure par terme. Les résultats numériques sont exportés en CSV et JSON.", b),
        Paragraph("Références", h1),
    ])
    refs = [
        "Avellaneda, M., Buff, R., Friedman, C., Grandchamp, N., Kruk, L. & Newman, J. (2001). Weighted Monte Carlo: A New Technique for Calibrating Asset-Pricing Models. International Journal of Theoretical and Applied Finance, 4(1), 91–119.",
        "Breeden, D. T. & Litzenberger, R. H. (1978). Prices of State-Contingent Claims Implicit in Option Prices. The Journal of Business, 51(4), 621–651.",
        "Cui, Z. & Yu, Z. (2021). A Model-Free Fourier Cosine Method for Estimating the Risk-Neutral Density. The Journal of Derivatives, 29(2), 149–171.",
        "Figlewski, S. (2010). Estimating the Implied Risk-Neutral Density for the US Market Portfolio. In Volatility and Time Series Econometrics, 323–353. Oxford University Press.",
        "Figlewski, S. (2018). Risk-Neutral Densities: A Review. Annual Review of Financial Economics, 10, 329–359.",
        "Giacomini, E., Härdle, W. K. & Krätschmer, V. (2009). Dynamic Semiparametric Factor Models in Risk Neutral Density Estimation. AStA Advances in Statistical Analysis, 93(4), 387–402.",
        "Taboga, M. (2016). Option-Implied Probability Distributions: How Reliable? How Jagged? International Review of Economics & Finance, 45, 453–469.",
    ]
    for ref in refs:
        story.append(Paragraph(ref, ST["refs"]))
    doc.build(story)
    shutil.copy2(ROOT / "papier_recherche_PI2_176.tex", OUT / "papier_recherche_PI2_176.tex")
    shutil.copy2(ROOT / "src" / "rnd_surface_3d.py", OUT / "rnd_surface_3d.py")
    print(out)


if __name__ == "__main__":
    build()
