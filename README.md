# PI² 176 — Dynamique des densités risque-neutres

Projet académique ESILV consacré à l’extraction, l’analyse et la prévision de densités risque-neutres (RND) à partir de prix d’options sur le S&P 500.

## Objectifs

- reconstruire une densité risque-neutre à chaque date par l’approche de Breeden–Litzenberger ;
- utiliser une paramétrisation SVI commune à une coupe d’options plutôt qu’un modèle indépendant par option ;
- étudier la stabilité temporelle des densités et leur structure par terme ;
- réduire leur dimension par facteurs, puis modéliser leur dynamique ;
- évaluer l’intérêt des prévisions pour la valorisation et la couverture d’options.

## État du prototype

Le pipeline actuel :

1. télécharge une chaîne SPX différée depuis Cboe ;
2. filtre les cotations selon leur qualité et leur liquidité ;
3. estime le forward et le facteur d’actualisation par parité call-put ;
4. calibre une SVI brute à cinq paramètres ;
5. reconstruit une courbe de calls régulière ;
6. applique Breeden–Litzenberger ;
7. produit la densité, les diagnostics et une surface RND 3D selon la maturité ;
8. contrôle le calcul dans une implémentation Julia indépendante.

Les résultats déjà calculés se trouvent dans [`results/`](results/) et les livrables du premier suivi dans [`Livrables_suivi_23-10-2026/`](Livrables_suivi_23-10-2026/).

## Démarrage rapide

Prérequis : Python 3.11 ou plus récent. Julia 1.10 est facultatif pour la réplication indépendante.

```powershell
git clone https://github.com/jordiparis165/pi2-rnd-derivatives-forecasting.git
cd pi2-rnd-derivatives-forecasting
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\run_prototype.ps1
```

Le script principal peut aussi être lancé directement :

```powershell
python src/spx_breeden_litzenberger.py
python src/rnd_surface_3d.py
```

## Organisation

```text
src/                              code Python et Julia
data/raw/                         snapshots publics Cboe
data/processed/                   données filtrées et points de calibration
results/                          densités, diagnostics et graphiques
Livrables_reunion_14-10-2026/     documents de la réunion de lancement
Livrables_suivi_23-10-2026/       rapport, papier et support de présentation
references.bib                    bibliographie BibTeX
```

## Données

Les snapshots inclus proviennent de l’API publique de cotations différées Cboe. Cette source ne fournit pas l’historique complet nécessaire à l’étude dynamique. La suite du projet nécessite donc un export Bloomberg, OptionMetrics ou Cboe DataShop. Voir [`data/README_acces_donnees.md`](data/README_acces_donnees.md).

## Travailler en équipe

Le dépôt est public : toute personne peut le consulter, le cloner et proposer une modification par pull request. Pour modifier directement les branches du dépôt, chaque membre doit être ajouté comme collaborateur avec son nom d’utilisateur GitHub.

La procédure recommandée est décrite dans [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Équipe

- Jordi Paris
- Rayan Ait Arkoub
- Matthieu Balliste
- Ilan Chahdi
- Nathan Denoux

Encadrement : Matthieu Garcin.

## Statut juridique

Projet académique. Aucun fichier de licence n’est défini à ce stade ; la publication du code n’accorde donc pas automatiquement de licence de réutilisation externe.
