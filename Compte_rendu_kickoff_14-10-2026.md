# Projet PI² n°176 — Compte rendu de la réunion de lancement

**Date :** mercredi 14 octobre 2026  
**Tuteur :** Matthieu Garcin  
**Objet :** cadrage scientifique, données, méthodologie et livrables

## 1. Objectif scientifique retenu

Le projet consiste à construire, à partir de prix historiques d'options, une série temporelle de **distributions de probabilité risque-neutre** (RND), puis à :

1. comparer plusieurs méthodes d'estimation de la RND ;
2. mesurer la stabilité de ces densités dans le temps ;
3. modéliser et prévoir leur dynamique ;
4. quantifier l'incertitude associée à leur estimation et à leur prévision ;
5. étudier une application à la valorisation, à la réplication ou à la couverture d'options.

Le projet combine donc théorie financière, traitement de données, estimation numérique, séries temporelles et programmation.

## 2. Clarification sur Black–Scholes et la calibration

Black–Scholes ne permet pas, avec une volatilité unique, de reproduire simultanément tous les prix observés pour une même maturité. En pratique, chaque option possède une volatilité implicite différente, ce qui fait apparaître le smile ou skew de volatilité.

Il faut distinguer deux démarches :

- **Ajustement option par option :** une volatilité implicite est calculée pour chaque couple strike–maturité. L'ajustement est exact par construction, mais il ne fournit pas un modèle commun parcimonieux de toute la chaîne.
- **Calibration conjointe :** un modèle ou une distribution comportant un nombre limité de paramètres — par exemple cinq paramètres — est calibré sur plusieurs options simultanément. Une seule distribution commune doit alors expliquer au mieux tous les strikes d'une même maturité.

Le cœur du projet n'est donc pas de construire un modèle différent pour chaque option, mais d'estimer une **RND commune à l'ensemble des options sur un même sous-jacent et une même échéance**.

## 3. Sous-jacent et données

Le sous-jacent de référence retenu pour commencer est le **S&P 500**, via les options sur indice **SPX**.

Sources envisagées :

- Bloomberg ;
- Cboe ;
- éventuellement une base académique telle qu'OptionMetrics si un accès est disponible.

Les données minimales sont : date et heure d'observation, échéance, strike, type call/put, bid, ask, prix de dernière transaction, date/heure de cette transaction, volume, open interest, niveau du sous-jacent, taux sans risque et données permettant d'estimer le forward.

## 4. Qualité et filtrage des observations

Un nombre important d'options sont affichées mais peu ou pas échangées. Le dernier prix peut être ancien et ne plus représenter l'état du marché.

Le pipeline devra donc :

- privilégier le **mid bid-ask** lorsque des cotations synchronisées sont disponibles ;
- contrôler l'ancienneté du dernier échange si seuls les prix de transaction sont exploitables ;
- supprimer les cotations avec bid nul, bid supérieur à ask ou spread excessif ;
- vérifier la monotonie et la convexité des prix par rapport au strike ;
- contrôler le volume et l'open interest sans en faire nécessairement des filtres absolus ;
- documenter précisément tous les seuils et tester la sensibilité des résultats à ces seuils.

Le seuil de « transaction trop ancienne » n'a pas encore été fixé. Il devra dépendre de la fréquence des données accessibles. Une règle provisoire peut être testée, puis comparée à des seuils plus ou moins stricts afin de mesurer la perte de couverture en strikes.

## 5. Horizon et constitution du panier

La réunion a fait émerger un exemple de travail : sélectionner des options d'une maturité initiale proche de **trois mois** et étudier leur évolution pendant **un mois**.

Deux protocoles sont possibles :

### Protocole A — Contrats fixes

Les mêmes contrats sont suivis pendant un mois. Leur maturité résiduelle passe approximativement de trois à deux mois.

- Avantage : on suit exactement les mêmes instruments.
- Limite : l'évolution de la RND mélange la dynamique du marché et l'effet mécanique de la diminution de la maturité.

### Protocole B — Maturité cible constante

À chaque date, on sélectionne l'échéance disponible la plus proche de trois mois, ou on interpole entre deux échéances encadrant l'horizon cible.

- Avantage : les densités sont plus comparables dans le temps.
- Limite : les contrats composant le panier changent et une interpolation en maturité peut être nécessaire.

**Recommandation :** utiliser le protocole B pour l'analyse principale de la dynamique des RND et conserver le protocole A comme contrôle de robustesse ou exercice initial. Cette recommandation reste à confirmer avec le tuteur.

## 6. Méthodes d'estimation à comparer

La fiche projet prévoit trois familles :

1. **Breeden–Litzenberger :** extraction de la densité à partir de la dérivée seconde des prix de calls par rapport au strike ;
2. **méthode Fourier :** estimation par séries de Fourier-cosinus et intégration des prix d'options ;
3. **distorsion de la probabilité historique :** calibration par repondération, notamment via l'entropie relative.

Pour chaque méthode et chaque date, la sortie doit être une densité sur une grille commune de log-moneyness. Les contrôles minimaux seront : positivité, masse totale proche de 1, moyenne cohérente avec le forward, reproduction des prix d'options et stabilité vis-à-vis du nettoyage et du maillage.

## 7. Stabilité et dynamique des densités

Il faudra examiner si chacune des densités estimées est stable dans le temps et si les trois méthodes produisent des évolutions cohérentes.

Une densité étant un objet fonctionnel, elle ne peut pas être directement traitée comme un petit vecteur autorégressif. Le protocole proposé est :

1. représenter toutes les densités sur une grille commune ;
2. réduire leur dimension grâce à un modèle factoriel ou une analyse en composantes principales fonctionnelle ;
3. modéliser les scores factoriels par un modèle autorégressif ou VAR ;
4. prévoir les facteurs, puis reconstruire la densité future ;
5. évaluer la prévision hors échantillon contre la densité du jour précédent.

L'article de Giacomini, Härdle et Krätschmer constitue la référence principale pour cette étape. L'article de Taboga doit guider l'étude de l'incertitude et éviter d'interpréter comme économique une irrégularité créée par l'estimation.

## 8. Application à la couverture

L'application finale peut porter sur la réplication ou la couverture d'une option. Un vendeur d'option ajuste notamment une position dans le sous-jacent afin de réduire son exposition directionnelle.

Le projet devra comparer :

- une couverture fondée sur un modèle ou une RND courante ;
- une couverture utilisant la RND prévue ;
- un benchmark simple, par exemple Black–Scholes ou une volatilité implicite constante à court terme.

La comparaison devra prendre en compte l'erreur de couverture, la fréquence de rebalancement, les coûts de transaction et l'incertitude de la prévision.

## 9. Choix informatique

Une partie substantielle du code doit être réalisée en OCaml ou Julia. L'équipe privilégie **Julia**, adapté au calcul numérique, à l'optimisation et à la visualisation scientifique.

Le cœur Julia devrait au minimum couvrir le nettoyage final, la calibration d'une ou plusieurs RND, les contrôles numériques et la génération des résultats reproductibles. Le périmètre exact doit être confirmé avec le tuteur.

## 10. Prochain jalon

La première réunion de suivi notée aura lieu le **vendredi 23 octobre 2026 de 11 h à 11 h 45**.

À transmettre au plus tard le **mardi 20 octobre 2026** :

- un rapport d'avancement ;
- un support pour une présentation de vingt minutes maximum.

Le premier suivi devra montrer une problématique stabilisée, la bibliographie, le protocole de données, les règles de filtrage, une architecture de code et, si possible, un premier résultat Breeden–Litzenberger sur données réelles ou synthétiques.

## 11. Points encore à confirmer

1. Quelle base historique est effectivement accessible et avec quelle fréquence ?
2. Dispose-t-on de cotations bid-ask historiques ou uniquement de derniers prix ?
3. Le protocole principal doit-il utiliser une maturité cible constante proche de trois mois ?
4. Les trois méthodes d'estimation doivent-elles toutes être implémentées intégralement ?
5. Le modèle paramétrique à environ cinq paramètres est-il imposé ou seulement donné comme exemple ?
6. Quel seuil d'ancienneté et quels critères de liquidité faut-il retenir ?
7. Quelle part exacte du pipeline doit être codée en Julia ?
8. L'application finale doit-elle privilégier la couverture plutôt que le trading directionnel ?
