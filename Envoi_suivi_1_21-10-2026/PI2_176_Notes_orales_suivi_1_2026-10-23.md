# Script oral — Suivi PI² n°1

## Durée cible : 16 à 18 minutes

Le support contient 11 diapositives. L'objectif n'est pas de lire tous les éléments, mais de faire apparaître trois idées : la méthode est mathématiquement fondée, le prototype fonctionne sur une vraie chaîne SPX, et ses limites sont identifiées avant le passage à la dynamique.

## Diapositive 1 — Introduction — 30 secondes

« Bonjour Monsieur Garcin. Nous allons vous présenter l'avancement du projet PI² n°176, consacré à l'estimation et à la dynamique des distributions risque-neutres implicites dans les options SPX.

Notre travail actuel correspond au premier jalon : construire une densité à partir d'une chaîne réelle, vérifier sa qualité, puis étudier sa structure selon la maturité. Nous terminerons par la manière dont nous passerons à une série temporelle et à une stratégie de couverture. »

Transition : « Commençons par la question de recherche qui organise tout le projet. »

## Diapositive 2 — Question de recherche et protocole — 1 minute 15

« La question générale est de savoir si une densité risque-neutre peut être estimée et prévue de façon suffisamment stable pour apporter de l'information à la valorisation ou à la couverture d'options.

Le projet se décompose en trois blocs. Le premier est l'estimation : Breeden–Litzenberger constitue notre benchmark, puis nous comparerons une méthode Fourier-cosinus et une repondération entropique. Le deuxième bloc porte sur la dynamique : toutes les densités devront être calculées à maturité constante, placées sur une grille commune puis résumées par quelques facteurs. Le troisième bloc est l'évaluation hors échantillon par les erreurs de pricing et de couverture.

À ce stade, nous avons réalisé le pipeline d'estimation sur une date et le diagnostic de la structure par terme. »

Transition : « La première difficulté pratique est la qualité des cotations. »

## Diapositive 3 — Données Cboe et filtrage — 1 minute 40

« Le prototype repose sur le snapshot différé Cboe du 16 octobre 2026. Pour l'échéance du 15 janvier 2027, soit 91 jours, nous partons de 1 446 contrats. Après les contrôles de qualité, 1 277 cotations restent valides et 338 points hors de la monnaie sont utilisés pour la calibration.

Le graphique de gauche montre que les spreads augmentent fortement dans les ailes. À droite, certains derniers échanges sont très anciens. C'est pourquoi nous utilisons le mid bid–ask et non le dernier prix comme observation principale.

Nous éliminons les bids nuls, les marchés croisés, les mids inférieurs à 0,05 et les spreads relatifs supérieurs à 35 %. Ce dernier seuil reste provisoire et fera l'objet d'une analyse de sensibilité.

L'API gratuite Cboe suffit pour mettre au point le prototype, mais elle ne fournit pas la profondeur historique homogène nécessaire. Pour la dynamique et le backtest de la stratégie, nous utiliserons un export Bloomberg ; l'accès et le protocole d'extraction restent à confirmer. »

Transition : « À partir de ces cotations, trois identités structurent tout le calcul. »

## Diapositive 4 — Identités théoriques — 1 minute 50

« Premièrement, sous la mesure risque-neutre, le prix d'un call européen est l'espérance actualisée de son payoff. Le facteur D actualise entre la date courante et l'échéance.

Deuxièmement, la parité call-put est affine en strike. Nous l'utilisons autour de la monnaie pour estimer conjointement le forward F et le facteur d'actualisation D à partir de la chaîne elle-même.

Troisièmement, Breeden et Litzenberger montrent que la dérivée seconde du prix du call par rapport au strike, divisée par D, donne la densité risque-neutre. Cette relation est indépendante d'un choix de processus particulier pour le sous-jacent.

La difficulté est numérique : une double dérivation amplifie le bruit. La convexité de la fonction de calls est également nécessaire pour obtenir une densité positive. Il faut donc construire une courbe régulière avant de la dériver. »

Transition : « Nous obtenons cette courbe régulière par une calibration commune SVI. »

## Diapositive 5 — Calibration SVI — 1 minute 45

« La variance totale implicite est décrite par la SVI brute à cinq paramètres. Contrairement à une volatilité différente pour chaque contrat, un seul vecteur de paramètres explique toute la coupe de strikes.

La parité fournit un forward de 7 755,89, un facteur d'actualisation de 0,98837 et un taux continu implicite de 4,69 %. La RMSE de la parité vaut 0,118 point et la RMSE de reconstruction des calls 1,144 point.

Le graphique montre que la SVI suit très précisément les 338 volatilités retenues. Il faut néanmoins distinguer les rôles : SVI est notre outil de lissage ; la méthode d'extraction de la densité reste Breeden–Litzenberger. Un bon ajustement visuel ne garantit pas non plus l'absence d'arbitrage dans les ailes. »

Transition : « Nous pouvons alors passer de la smile à une courbe de calls, puis à la densité. »

## Diapositive 6 — De la courbe de calls à la RND — 1 minute 35

« À gauche, les points correspondent aux calls observés ou synthétiques obtenus à partir des puts hors de la monnaie. La courbe est reconstruite sur une grille régulière de 1 601 strikes.

À droite, nous appliquons la dérivée seconde à cette courbe lissée. La densité est asymétrique : la queue gauche est plus lourde, ce qui est cohérent avec la demande de protection sur un indice actions.

Cette figure donne la forme de la RND, mais elle ne suffit pas pour la valider. Nous devons vérifier son intégrale, sa positivité et sa moyenne. »

Transition : « La diapositive suivante rassemble précisément ces diagnostics. »

## Diapositive 7 — Diagnostics à 91 jours — 2 minutes

« La masse brute vaut 0,99528 : il manque environ 0,47 % de masse sur la grille. La masse négative absolue n'est que de 0,000117. Même si environ 20 % des points très éloignés sont légèrement négatifs, aucun n'a une amplitude supérieure à 0,1 % du pic. Le nombre de points négatifs serait donc trompeur sans regarder leur masse.

Après troncature et normalisation, la moyenne vaut 7 776,20, soit 20,31 points ou 0,26 % au-dessus du forward. Sous la mesure risque-neutre, la moyenne complète devrait être égale au forward. Le rapport montre que l'écart est compatible avec une masse manquante dans la queue gauche, au-delà de la borne de la grille.

La zone grisée correspond au support des strikes utilisés pour la calibration. Les résultats dans les zones extérieures reposent sur l'extrapolation SVI. Nous traitons donc la troncature comme un diagnostic provisoire et non comme une correction définitive. Nous comparerons eSSVI, une extension de queue de type Figlewski et un lissage directement convexe. »

Transition : « Nous avons ensuite répété le calcul sur six maturités. »

## Diapositive 8 — Surface tridimensionnelle — 1 minute 20

« La surface représente les densités pour six maturités comprises entre 31 et 182 jours. Pour les comparer, nous passons du niveau du SPX à la log-moneyness k et nous appliquons le changement de variable affiché en haut à droite.

Les lignes noires sont les six coupes réellement calibrées. La surface entre ces lignes est seulement une interpolation PCHIP destinée à la visualisation. Elle ne crée pas de nouvelles observations.

La densité s'aplatit et s'élargit avec la maturité. Surtout, l'axe vertical est ici la maturité résiduelle à une date fixe. Cette surface est une structure par terme, pas encore la dynamique temporelle demandée par le projet. »

Transition : « Cette représentation est utile, mais toutes les coupes ne sont pas aussi fiables. »

## Diapositive 9 — Fiabilité selon la maturité — 1 minute 50

« La carte thermique montre les six densités sans interpolation entre maturités. Les graphiques de droite testent deux conditions simples : une masse proche de un et une moyenne proche du forward.

Entre 63 et 182 jours, la masse brute est comprise entre 0,988 et 0,997. L'écart moyen-forward reste contenu entre environ 0,15 % et 0,68 %, tout en augmentant avec la maturité à cause du support fini.

La maturité 31 jours est clairement anormale : masse 1,138 et moyenne 5,4 % au-dessus du forward. Les points de calibration ne couvrent pas suffisamment l'aile droite et la SVI extrapolée viole la monotonie des calls. Nous conservons cette coupe pour montrer le diagnostic, mais nous l'excluons de toute conclusion économique. C'est précisément ce type de test qui empêchera une surface visuellement jolie de masquer un arbitrage. »

Transition : « Une fois les coupes fiables obtenues chaque jour, nous pourrons étudier leur dynamique. »

## Diapositive 10 — Dynamique et stratégie — 1 minute 50

« Avec l'historique Bloomberg, nous construirons une RND quotidienne à maturité constante, probablement autour de trois mois. Cela évite de confondre l'écoulement du temps avec une modification de la distribution anticipée par le marché.

Chaque densité sera représentée par une moyenne fonctionnelle et un petit nombre de fonctions de base. Les coefficients bêta seront les scores factoriels. Leur dynamique sera ensuite modélisée par un AR ou un VAR et comparée à une marche aléatoire fonctionnelle.

Les prévisions seront évaluées avec Jensen–Shannon, Wasserstein et l'erreur de pricing. Pour l'application finale, nous comparerons une couverture fondée sur la RND actuelle, une couverture fondée sur la RND prévue et Black–Scholes. Le test sera hors échantillon et net des coûts de transaction. »

Transition : « Nous terminons par ce qui est acquis et le prochain jalon. »

## Diapositive 11 — Conclusion — 1 minute

« Nous disposons maintenant d'un pipeline reproductible allant d'une chaîne SPX brute à une RND contrôlée. Le forward, l'actualisation et la SVI sont estimés sur 338 points, la densité à 91 jours est cohérente à quelques dixièmes de pour cent près, et la réplication Julia confirme le calcul Python : l'écart absolu moyen sur la densité normalisée vaut $3{,}4\times10^{-9}$ et le maximum $2{,}2\times10^{-6}$, localisé aux bords.

Nous avons aussi identifié les limites avant de lancer l'étude dynamique : support fini, extrapolation des ailes et arbitrage sur la coupe 31 jours.

Le prochain jalon est de sécuriser l'export historique Bloomberg, de construire des densités à maturité constante, puis de comparer les trois méthodes et d'estimer les facteurs. Nous souhaitons notamment valider avec vous l'horizon constant à retenir et le protocole d'accès aux données. »

## Questions techniques probables

### Pourquoi utiliser SVI alors que le projet demande Breeden–Litzenberger ?

SVI n'est pas la méthode d'extraction. Elle sert à obtenir une fonction de volatilité, puis une fonction de prix régulière et commune à tous les strikes. Breeden–Litzenberger est ensuite appliqué à cette fonction de prix.

### Pourquoi ne pas dériver directement les prix observés ?

Parce qu'une dérivée seconde amplifie fortement le bruit bid–ask, les erreurs d'arrondi et l'irrégularité de l'espacement des strikes. La densité obtenue directement serait très instable et souvent négative.

### Pourquoi utiliser les puts sous le forward ?

Les options hors de la monnaie sont généralement les plus liquides. Sous le forward, nous utilisons donc les puts OTM, puis la parité call-put les transforme en calls synthétiques compatibles avec la formule de Breeden–Litzenberger.

### Pourquoi 20 % des points sont-ils négatifs alors que la masse négative est presque nulle ?

Ces points sont concentrés dans l'extrême queue et leur amplitude est de l'ordre de $10^{-8}$, contre un pic voisin de $10^{-3}$. Le pourcentage de points dépend du maillage ; la masse intégrée et l'amplitude relative sont les diagnostics économiquement pertinents.

### Pourquoi la moyenne doit-elle être égale au forward ?

Sous la mesure risque-neutre associée au numéraire monétaire, $F_{t,T}=\mathbb{E}^{\mathbb{Q}}_t[S_T]$. Une différence entre la moyenne numérique de la densité et le forward révèle un support tronqué, une extrapolation insuffisante ou une violation d'arbitrage.

### Pourquoi la coupe à 31 jours est-elle rejetée ?

La calibration y repose sur seulement 105 points et couvre mal l'aile droite. L'extrapolation SVI produit une masse de 1,138, une moyenne 5,4 % au-dessus du forward et une courbe de calls qui finit par croître avec le strike. Elle est donc utile comme contre-exemple, mais pas comme estimation exploitable.

### Le modèle est-il totalement sans arbitrage ?

Non. La courbe est contrôlée numériquement, mais la SVI brute ne garantit pas toutes les contraintes d'arbitrage butterfly et calendrier. Une eSSVI contrainte ou un lissage convexe des calls sera testé.

### Comment obtenir une maturité constante ?

À chaque date, nous sélectionnerons les deux échéances qui encadrent l'horizon cible, puis nous interpolerons la variance totale avant d'extraire la RND. Une sélection de l'échéance la plus proche servira de test de robustesse.

### Pourquoi Bloomberg plutôt que l'API Cboe gratuite ?

L'API gratuite Cboe fournit une photographie différée utile au prototype, mais pas l'historique quotidien homogène requis pour estimer un modèle dynamique et effectuer un backtest. Bloomberg doit fournir cette profondeur historique et les champs de liquidité nécessaires.

### Que valide Julia ?

Julia réimplémente indépendamment la dérivée seconde, l'intégration, la normalisation et les moments. L'écart absolu moyen avec Python vaut $3{,}4\times10^{-9}$ sur la densité normalisée et l'écart maximal $2{,}2\times10^{-6}$, aux extrémités de la grille où les schémas de différences finies ne sont pas identiques. Cette vérification réduit le risque qu'une erreur propre au code Python soit interprétée comme un résultat financier.
