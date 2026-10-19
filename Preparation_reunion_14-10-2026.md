# Projet PI² n°176 — Préparation de la réunion de lancement

**Date :** mercredi 14 octobre 2026, 16 h–16 h 30, à distance  
**Tuteur :** Matthieu Garcin  
**Équipe :** Rayan Ait Arkoub, Matthieu Balliste, Ilan Chahdi, Nathan Denoux, Jordi Paris

## 1. Objectif de la réunion

Cette réunion est le **kick-off/cadrage**, et non le premier suivi noté. Il faut en sortir avec un périmètre expérimental faisable, une source de données, une définition claire du premier prototype et une répartition du travail validée.

Le **premier suivi noté** aura lieu le vendredi 23 octobre 2026 de 11 h à 11 h 45. Le rapport d'avancement doit être envoyé trois jours avant, donc **au plus tard le mardi 20 octobre 2026**. Par prudence, prévoir que le support oral soit prêt et envoyé à la même date. La présentation du 23 octobre ne doit pas dépasser 20 minutes.

## 2. Reformulation du projet à présenter en une minute

> Nous voulons construire une série temporelle de distributions risque-neutre à partir de prix d'options, comparer plusieurs méthodes de calibration, mesurer la stabilité et la prévisibilité de ces distributions, puis tester si une prévision accompagnée de son incertitude améliore une décision de couverture ou une stratégie. Nous commencerons par un pipeline Breeden–Litzenberger simple et vérifiable, avant d'ajouter une méthode Fourier et un modèle factoriel dynamique.

## 3. Proposition de périmètre initial

- **Sous-jacent recommandé pour le MVP :** indice S&P 500 / options SPX, si l'école donne accès à OptionMetrics, Cboe DataShop ou une autre base historique fiable.
- **Pourquoi :** options européennes, forte liquidité, littérature abondante et résultats comparables aux références.
- **Horizon initial :** une échéance constante proche de 30 jours ; une densité par date.
- **Variable de grille :** log-moneyness \(\log(K/F_{t,T})\), afin de comparer les densités dans le temps malgré le déplacement du spot.
- **Baseline :** nettoyage des cotations, calcul des mid-prices, interpolation/lissage de la smile de volatilité implicite, repricing, puis dérivée seconde par rapport au strike.
- **Alternative :** méthode Fourier-cosinus de Cui & Yu (2021).
- **Validation minimale :** densité non négative, masse proche de 1, moyenne cohérente avec le forward, convexité des calls, robustesse au maillage et stabilité hors échantillon.
- **Implémentation :** Julia recommandé pour le cœur numérique afin de satisfaire dès le départ l'exigence « part substantielle en OCaml ou Julia ». Python peut rester un outil exploratoire seulement si le tuteur le valide.

Le TTF est une piste pertinente grâce à l'expérience de Jordi, mais les données historiques d'options ICE sont généralement plus difficiles d'accès. Ne pas le retenir comme sous-jacent principal sans confirmer l'accès aux données.

## 4. Agenda proposé pour les 30 minutes

### 0–3 min — Présentation et objectif

- rappeler l'équipe et l'expérience de Jordi sur les RND/TTF ;
- annoncer le résultat attendu de la réunion : verrouiller données, périmètre et premier jalon.

### 3–8 min — Compréhension du sujet

- présenter la reformulation d'une minute ;
- montrer la chaîne : options → RND → stabilité → prévision → couverture/trading ;
- préciser que la RND n'est pas une prévision physique directe : elle mélange anticipations et prix du risque.

### 8–17 min — Arbitrages à faire valider

- sous-jacent et base de données ;
- échéance fixe ou plusieurs maturités ;
- méthodes réellement attendues parmi Breeden–Litzenberger, Fourier et distorsion historique ;
- signification de « part substantielle » en Julia/OCaml ;
- priorité entre trading directionnel, couverture et comparaison de modèles.

### 17–24 min — Premier prototype et validation

- annoncer un baseline Breeden–Litzenberger ;
- présenter les contrôles de non-arbitrage et de cohérence probabiliste ;
- proposer une comparaison prix bruts/différences finies contre smile lissée ;
- fixer les résultats à montrer le 23 octobre.

### 24–28 min — Organisation

- répartition des responsabilités ;
- dépôt Git, environnement reproductible et tableau de lecture commun ;
- point hebdomadaire court recommandé dans le courriel d'affectation.

### 28–30 min — Conclusion

- reformuler les décisions prises ;
- confirmer les livrables du 20 octobre et le contenu de la présentation du 23 ;
- convenir du canal et du rythme de communication.

## 5. Questions à poser au tuteur

### Questions bloquantes

1. À quelles bases de données historiques d'options l'équipe a-t-elle accès via l'ESILV : OptionMetrics/WRDS, Cboe DataShop, Bloomberg, Refinitiv ou autre ?
2. Préférez-vous imposer un sous-jacent, ou pouvons-nous retenir SPX pour le MVP ?
3. Attendez-vous l'implémentation des trois familles de calibration, ou une comparaison approfondie de deux méthodes suffit-elle ?
4. Quelle proportion du code doit être écrite en Julia ou OCaml pour être considérée comme « substantielle » ?
5. Pour la dernière étape, la priorité est-elle une stratégie de **couverture** avec Greeks prévus, une stratégie de **trading**, ou les deux ?

### Questions de cadrage scientifique

6. Faut-il prévoir une seule maturité constante ou modéliser conjointement plusieurs maturités ?
7. Quelle métrique de stabilité privilégier : KL, Jensen–Shannon, Wasserstein, ou comparaison de plusieurs mesures ?
8. La prévision doit-elle porter sur la densité complète, ses facteurs, ses moments, ou les trois ?
9. Quel benchmark doit être utilisé pour juger la prévision : marche aléatoire, densité du jour précédent, Black–Scholes, ou modèle autorégressif des moments ?
10. Quel niveau de prise en compte des coûts de transaction, bid-ask et contraintes de liquidité est attendu dans le backtest ?

### Questions de suivi

11. Le rapport et le support du premier suivi doivent-ils tous deux être envoyés le 20 octobre ?
12. Y a-t-il un modèle imposé pour le rapport d'avancement et une grille d'évaluation détaillée à suivre ?
13. Les quatre groupes suivis sur ce sujet partageront-ils données, code de base ou réunions, et comment sera distingué le travail de chaque équipe ?

## 6. Répartition proposée

| Responsable | Bloc initial | Sortie attendue pour le 20 octobre |
|---|---|---|
| Rayan | pilotage, calendrier, intégration | backlog, décisions, structure du rapport |
| Jordi | données et baseline Breeden–Litzenberger | schéma de données, formule, pseudo-code et premiers contrôles |
| Matthieu | état de l'art calibration | synthèse Figlewski, Shimko, Cui & Yu |
| Ilan | stabilité et incertitude | fiche KL/Jensen–Shannon/Wasserstein et limites numériques |
| Nathan | dynamique, backtest et architecture Julia | synthèse modèle factoriel, benchmarks, squelette technique |

Cette répartition est une proposition à valider collectivement ; chaque bloc doit être relu par un second membre pour éviter les silos.

## 7. Plan de travail jusqu'au premier suivi

### 14 octobre après la réunion

- consigner les décisions et responsabilités ;
- ouvrir le dépôt Git et créer la structure `data/`, `src/`, `notebooks/`, `tests/`, `report/` ;
- obtenir ou demander immédiatement l'accès aux données.

### 15–16 octobre

- compléter les fiches de lecture prioritaires ;
- définir le schéma de données et les règles de nettoyage ;
- implémenter sur données synthétiques la formule de Breeden–Litzenberger et ses tests.

### 17–18 octobre

- appliquer le pipeline à une chaîne d'options réelle si les données sont disponibles ;
- produire les diagnostics : smile, calls reconstruits, densité, intégrale, moyenne/forward, zones négatives ;
- documenter les blocages de données plutôt que de masquer l'absence de résultats.

### 19 octobre

- figer les graphiques et résultats du rapport ;
- construire un support de 8 à 10 diapositives pour 15 à 18 minutes ;
- faire une répétition et répartir la parole.

### 20 octobre

- relire, exporter et envoyer le rapport d'avancement ainsi que le support ;
- conserver une marge avant l'heure limite au lieu d'envoyer tard le soir.

## 8. Contenu minimal du rapport du 20 octobre

1. contexte, problématique et livrables du projet ;
2. état de l'art ciblé et carte des méthodes ;
3. périmètre retenu, données et hypothèses ;
4. architecture du pipeline et équations du baseline ;
5. résultats préliminaires ou, à défaut, tests sur données synthétiques ;
6. contrôles de validité et risques identifiés ;
7. répartition, planning et prochaines étapes ;
8. bibliographie.

## 9. Risques à annoncer honnêtement

- **Accès aux données :** risque principal et décision à prendre aujourd'hui.
- **Bruit numérique :** la dérivée seconde amplifie bid-ask et erreurs d'interpolation.
- **Arbitrage statique :** un lissage visuel peut encore produire une densité négative.
- **Queues :** les strikes observés couvrent un support fini ; l'intégrale peut être inférieure à 1.
- **Comparabilité temporelle :** travailler en strike brut déplace artificiellement les densités avec le niveau de l'indice.
- **Fuite d'information :** tout lissage, normalisation et réglage du backtest doit utiliser uniquement l'information disponible à la date considérée.
- **Sur-ajustement :** signal prédictif et performance économique doivent être évalués hors échantillon, avec coûts et benchmark.

## 10. Phrase de clôture proposée

> Si vous validez SPX, l'horizon proche de 30 jours et Julia, notre objectif pour le 23 octobre sera de présenter une bibliographie structurée, une base de données ou son schéma final, un estimateur Breeden–Litzenberger testé, les contrôles de cohérence associés et le protocole de comparaison avec la méthode Fourier.
