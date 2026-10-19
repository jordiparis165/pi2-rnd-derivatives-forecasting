# Projet PI² n°176 — Bibliographie commentée

## 1. Fil directeur du projet

La bibliographie doit servir les cinq étapes indiquées dans la fiche projet :

1. constituer une base temporelle de prix d'options ;
2. estimer les distributions risque-neutre (RND) ;
3. mesurer leur stabilité dans le temps ;
4. prévoir leur dynamique et quantifier l'incertitude de cette prévision ;
5. utiliser ces prévisions dans une stratégie de couverture ou de trading.

La relation centrale, pour un taux déterministe et une option européenne d'échéance \(T\), est :

\[
q_t(K,T)=e^{r(T-t)}\frac{\partial^2 C_t(K,T)}{\partial K^2}.
\]

En pratique, la double dérivation amplifie fortement le bruit des cotations. La qualité du nettoyage, du lissage sans arbitrage, de l'interpolation et du traitement des queues est donc aussi importante que la formule elle-même.

## 2. Références imposées par la fiche projet

### Calibration et théorie des RND

**Breeden, D. T., & Litzenberger, R. H. (1978).** “Prices of State-Contingent Claims Implicit in Option Prices.” *The Journal of Business*, 51(4), 621–651. DOI: [10.1086/296025](https://doi.org/10.1086/296025).

- Résultat fondateur : la dérivée seconde du prix d'un call par rapport au strike donne le prix d'état et, après actualisation, la densité risque-neutre.
- À utiliser pour la partie théorique et pour construire le premier estimateur numérique par différences finies.

**Figlewski, S. (2010).** “Estimating the Implied Risk-Neutral Density for the US Market Portfolio.” In T. Bollerslev, J. R. Russell, & M. W. Watson (eds.), *Volatility and Time Series Econometrics: Essays in Honor of Robert F. Engle*, 323–353. Oxford University Press. DOI: [10.1093/acprof:oso/9780199549498.003.0015](https://doi.org/10.1093/acprof:oso/9780199549498.003.0015).

- Référence pratique sur l'interpolation, le lissage, la prise en compte des fourchettes bid-ask et l'ajout de queues.
- Très utile pour définir les tests de validité : positivité, intégrale proche de 1, moyenne cohérente avec le forward et absence d'arbitrage.

**Figlewski, S. (2018).** “Risk-Neutral Densities: A Review.” *Annual Review of Financial Economics*, 10, 329–359. DOI: [10.1146/annurev-financial-110217-022944](https://doi.org/10.1146/annurev-financial-110217-022944).

- Revue d'ensemble prioritaire pour cartographier les méthodes d'estimation, leurs hypothèses et leurs usages.
- Bon point d'entrée pour l'état de l'art du mémoire.

**Cui, Z., & Yu, Z. (2021).** “A Model-Free Fourier Cosine Method for Estimating the Risk-Neutral Density.” *The Journal of Derivatives*, 29(2), 149–171. DOI: [10.3905/JOD.2021.1.137](https://doi.org/10.3905/JOD.2021.1.137).

- Alternative à Breeden–Litzenberger fondée sur des intégrales de prix d'options et une série de Fourier-cosinus.
- À comparer au baseline par différences finies, notamment sur la robustesse au bruit et aux strikes rares.

**Cui, Z., Liu, Y., & Yao, Y. (2025).** “Model-Free Option-Implied Quantiles.” Prépublication, version du 29 septembre 2025. DOI indiqué sur la prépublication : [10.13140/RG.2.2.11695.80808/1](https://doi.org/10.13140/RG.2.2.11695.80808/1).

- Méthode récente pour extraire CDF et quantiles implicites via séries de Fourier.
- Référence secondaire à ce stade : intéressante pour les quantiles de queue, mais non encore évaluée comme un article publié dans la fiche projet.

**Avellaneda, M., Buff, R., Friedman, C., Grandchamp, N., Kruk, Ł., & Newman, J. (2001).** “Weighted Monte Carlo: A New Technique for Calibrating Asset-Pricing Models.” *International Journal of Theoretical and Applied Finance*, 4(1), 91–119. DOI: [10.1142/S0219024901000882](https://doi.org/10.1142/S0219024901000882).

- Repondère des trajectoires simulées en minimisant une entropie relative sous contraintes de prix.
- Sert au bloc « distorsion de la probabilité historique » et relie calibration, entropie et pricing.

### Stabilité, dynamique et incertitude

**Cover, T. M., & Thomas, J. A. (1991).** *Elements of Information Theory*. Wiley.

- Base théorique pour l'entropie, la divergence de Kullback–Leibler et leurs propriétés.
- Attention en pratique : une KL directe entre densités estimées devient instable si la densité de référence est presque nulle ; prévoir un plancher numérique ou une mesure symétrisée en test de robustesse.

**Giacomini, E., Härdle, W. K., & Krätschmer, V. (2009).** “Dynamic Semiparametric Factor Models in Risk Neutral Density Estimation.” *AStA Advances in Statistical Analysis*, 93(4), 387–402. DOI: [10.1007/s10182-009-0115-4](https://doi.org/10.1007/s10182-009-0115-4).

- Référence principale pour représenter une série temporelle de surfaces/densités par un petit nombre de facteurs dynamiques.
- Sert directement au bloc prévision : réduction de dimension, dynamique des scores, reconstruction de la densité prévue.

**Taboga, M. (2016).** “Option-Implied Probability Distributions: How Reliable? How Jagged?” *International Review of Economics & Finance*, 45, 453–469. DOI: [10.1016/j.iref.2016.07.013](https://doi.org/10.1016/j.iref.2016.07.013).

- Traite explicitement l'incertitude autour des densités estimées et le risque de multimodalité artificielle causée par le sur-ajustement.
- À mobiliser pour les intervalles d'incertitude et pour ne pas confondre irrégularité numérique et signal économique.

## 3. Documents fournis par l'équipe

**Bocconi Students Investment Club (BSIC). (2026, 29 mars).** “Risk Neutral Density Estimation from Option Prices.” [Article en ligne](https://bsic.it/risk-neutral-density-estimation-from-option-prices/).

- Tutoriel empirique récent : données SPX 2015–2025, spline cubique de volatilité implicite, repricing Black–Scholes, puis Breeden–Litzenberger.
- Montre pourquoi les différences finies sur prix bruts produisent des densités négatives et bruitées.
- Prolonge l'analyse vers VIX, SVIX, moments, régressions prédictives et stratégie de timing.
- Très utile pour prototyper, mais il faut s'appuyer sur les articles académiques pour justifier les choix méthodologiques.

Le second PDF fourni est une copie de l'article de **Breeden & Litzenberger (1978)** déjà référencé ci-dessus.

## 4. Compléments prioritaires

**Shimko, D. (1993).** “Bounds of Probability.” *Risk*, 6(4), 33–37.

- Source classique du lissage de la volatilité implicite avant reconstruction des prix et dérivation.
- À lire avec Figlewski pour encadrer les risques d'extrapolation dans les queues.

**Martin, I. (2017).** “What Is the Expected Return on the Market?” *The Quarterly Journal of Economics*, 132(1), 367–433. DOI: [10.1093/qje/qjw034](https://doi.org/10.1093/qje/qjw034).

- Relie la variance risque-neutre des rendements au rendement excédentaire attendu et introduit SVIX.
- Complément naturel pour la partie signal prédictif et stratégie, sans supposer qu'une significativité statistique garantit un alpha après risque et coûts.

**Cboe Global Indices.** *Volatility Index Methodology: Cboe Volatility Index*. [Méthodologie officielle](https://cdn.cboe.com/api/global/us_indices/governance/Volatility_Index_methodology_VIXMO_only.pdf).

- Référence de mise en œuvre si le projet utilise SPX/VIX et une échéance constante proche de 30 jours.

## 5. Ordre de lecture recommandé

1. Figlewski (2018) pour la carte générale.
2. Breeden & Litzenberger (1978), section sur la dérivée seconde.
3. BSIC (2026) pour voir un pipeline empirique complet et ses écueils.
4. Figlewski (2010) et Shimko (1993) pour rendre l'estimation robuste.
5. Cui & Yu (2021) pour l'alternative Fourier.
6. Cover & Thomas (1991), puis Giacomini et al. (2009), pour stabilité et prévision.
7. Taboga (2016) pour l'incertitude d'estimation.
8. Avellaneda et al. (2001) et Martin (2017) pour les extensions calibration/trading.

## 6. Grille de lecture commune

Pour chaque article, consigner dans un tableau partagé : objectif, données, hypothèses, méthode, contraintes d'arbitrage, traitement des queues, métriques de validation, résultats, limites et éléments reproductibles. Cette grille évitera cinq résumés indépendants difficiles à assembler dans le mémoire.
