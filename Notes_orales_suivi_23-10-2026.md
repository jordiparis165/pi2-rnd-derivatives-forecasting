# Notes orales — Suivi PI² n°1

## Répartition suggérée — 17 à 19 minutes

### Diapositive 1 — Introduction — 45 secondes

Présenter l'équipe, le sujet et annoncer le fil conducteur : construire une RND commune à une chaîne d'options, étudier sa dynamique et l'utiliser pour la couverture.

### Diapositive 2 — Problématique — 1 min 30

Expliquer que Black–Scholes ajuste une option avec une volatilité implicite, mais qu'une volatilité unique ne reproduit pas tous les strikes. Le smile motive l'estimation d'une distribution commune.

### Diapositive 3 — Données — 2 minutes

Présenter l'accès Cboe confirmé et les chiffres de l'échantillon. Insister sur la différence entre cotation bid-ask courante et dernier prix parfois ancien. Signaler honnêtement que l'historique Bloomberg/OptionMetrics reste à obtenir.

### Diapositive 4 — Nettoyage — 2 minutes

Décrire la sélection de maturité, les filtres, la parité call-put et le choix des options hors de la monnaie. Préciser que le seuil de spread de 35 % est provisoire et sera testé.

### Diapositive 5 — SVI — 2 minutes

Montrer qu'une seule smile à cinq paramètres est calibrée sur 338 points. Donner le forward, le taux implicite et la RMSE sans lire tous les paramètres.

### Diapositive 6 — Breeden–Litzenberger — 1 min 30

Présenter la formule et expliquer pourquoi la dérivée seconde est appliquée à la courbe lissée. Mentionner les contrôles de masse, positivité, moyenne et convexité.

### Diapositive 7 — RND — 2 minutes

Commenter la forme de la densité, sa masse de 0,9953 et sa moyenne. Expliquer que les valeurs négatives sont minuscules et concentrées dans la queue extrapolée ; elles révèlent une limite de SVI brute à corriger, pas un résultat économique.

### Diapositive 8 — Surface 3D — 1 min 30

Présenter les six maturités et expliquer l'élargissement de la densité avec l'horizon. Préciser explicitement que cette figure est une structure par terme observée à une seule date, et non encore la dynamique temporelle demandée par le projet.

### Diapositive 9 — Validation et limites — 2 minutes

Mettre en avant l'exécution Julia et la concordance numérique. Présenter les limites avant que le tuteur ne les soulève : absence d'historique, seuils provisoires, arbitrage butterfly et maturité constante.

### Diapositive 10 — Suite — 2 minutes

Présenter l'historique à obtenir, les trois méthodes, les distances entre densités, la réduction factorielle et la couverture. Terminer par les quatre décisions attendues du tuteur.

## Questions probables

**Pourquoi SVI alors que la fiche demande Breeden–Litzenberger ?**  
SVI sert uniquement à obtenir une courbe de prix lisse et commune avant l'application de Breeden–Litzenberger. La méthode d'extraction reste BL.

**Pourquoi ne pas dériver directement les prix ?**  
La double dérivation amplifie les erreurs de cotation et produit des densités très bruitées ou négatives.

**Pourquoi utiliser les puts sous le forward ?**  
Les options hors de la monnaie sont généralement plus liquides. La parité call-put permet de les convertir en calls synthétiques.

**Pourquoi la moyenne n'est-elle pas exactement égale au forward ?**  
La grille est finie, la queue est extrapolée et les très faibles valeurs négatives sont tronquées avant normalisation. L'écart sert de diagnostic pour améliorer la méthode.

**Le modèle est-il sans arbitrage ?**  
Les prix sont lissés et contrôlés, mais la SVI brute n'impose pas toutes les contraintes butterfly. Une eSSVI ou un lissage convexe sera testé.

**Où est Julia ?**  
Julia calcule de façon autonome la dérivée seconde, la densité, sa normalisation et ses moments à partir de la courbe reconstruite. Les résultats concordent avec Python.
