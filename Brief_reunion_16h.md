# Brief équipe — Réunion PI² du 14 octobre à 16 h

## Ce qu'il faut obtenir aujourd'hui

1. Le sous-jacent et la source de données historiques.
2. Le périmètre exact : méthodes, maturités et cible finale couverture/trading.
3. La règle concernant la part de Julia ou OCaml.
4. Le contenu attendu au premier suivi du 23 octobre.
5. La confirmation de la date d'envoi du rapport et du support : 20 octobre.

## Pitch de 45 secondes

> Notre objectif est d'extraire une série temporelle de distributions risque-neutre à partir de prix d'options, d'en comparer les méthodes de calibration, puis d'étudier leur stabilité et leur prévisibilité avant de tester une application de couverture ou de trading. Nous proposons de commencer par SPX à horizon proche de 30 jours, avec un baseline Breeden–Litzenberger en Julia, contrôlé par des tests de non-arbitrage et de cohérence probabiliste. Nous comparerons ensuite ce baseline à la méthode Fourier-cosinus et utiliserons un modèle factoriel pour la dynamique.

## Les cinq questions indispensables

1. Avons-nous accès à OptionMetrics/WRDS, Cboe, Bloomberg ou Refinitiv ?
2. Validez-vous SPX et une échéance constante proche de 30 jours pour le MVP ?
3. Faut-il implémenter les trois méthodes de calibration ou en approfondir deux ?
4. Que signifie précisément « une part substantielle en Julia ou OCaml » ?
5. La cible finale prioritaire est-elle la couverture, le trading, ou les deux ?

## Proposition pour le 23 octobre

- bibliographie commentée et carte des méthodes ;
- source ou schéma définitif des données ;
- prototype Breeden–Litzenberger, au minimum sur données synthétiques ;
- graphiques de smile, calls reconstruits et densité ;
- contrôles : positivité, masse, moyenne/forward et convexité ;
- protocole de comparaison avec Fourier ;
- planning, responsabilités et risques.

## À ne pas promettre

- une stratégie rentable avant d'avoir défini un test hors échantillon et les coûts ;
- une RND fiable à partir de prix bruts sans lissage ni contrôle d'arbitrage ;
- le TTF comme marché principal sans accès confirmé aux données ICE ;
- une prévision de probabilité « réelle » : la RND incorpore aussi les prix du risque.

## Juste après la réunion

- envoyer un compte rendu des décisions ;
- ouvrir le dépôt Git et répartir les cinq blocs ;
- demander immédiatement les accès aux données ;
- commencer le baseline sur une surface synthétique si les données réelles ne sont pas encore accessibles.
