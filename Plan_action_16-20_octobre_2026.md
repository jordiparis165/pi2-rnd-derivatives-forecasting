# Projet PI² n°176 — Plan d'action avant le premier suivi

## Résultat attendu le 20 octobre

À la fin du mardi 20 octobre, l'équipe doit disposer d'un rapport d'avancement cohérent, d'un support oral de moins de vingt minutes et d'au moins un pipeline technique démontrable.

## Priorité 1 — Sécuriser les données

**À faire immédiatement :**

- vérifier l'accès Bloomberg, Cboe ou OptionMetrics ;
- identifier la fréquence disponible et les champs bid, ask, last, timestamp, volume et open interest ;
- extraire un petit échantillon SPX couvrant plusieurs strikes, plusieurs dates et une maturité proche de trois mois ;
- conserver les données brutes sans les modifier et produire séparément une table nettoyée.

**Décision de repli :** si les données historiques ne sont pas disponibles à temps, démontrer le pipeline sur données synthétiques Black–Scholes avec smile imposé, puis indiquer précisément la donnée réelle manquante.

## Priorité 2 — Construire le baseline Breeden–Litzenberger

Le prototype minimal doit :

1. charger une chaîne d'options pour une date et une échéance ;
2. calculer le forward ou la moneyness ;
3. filtrer les observations manifestement invalides ;
4. lisser la smile de volatilité implicite ;
5. reconstruire des prix de calls sur une grille régulière ;
6. calculer la dérivée seconde par différences finies ;
7. normaliser et tracer la densité ;
8. produire les contrôles de masse, moyenne, positivité et convexité.

## Priorité 3 — Rédiger le rapport

Structure conseillée :

1. contexte et objectif ;
2. Black–Scholes, smile et notion de RND commune ;
3. méthodes prévues : Breeden–Litzenberger, Fourier et distorsion historique ;
4. choix de SPX et protocole à maturité proche de trois mois ;
5. données et règles de filtrage ;
6. premier prototype et contrôles ;
7. stabilité, modèle factoriel et prévision envisagée ;
8. application future à la couverture ;
9. organisation, calendrier, risques et questions ouvertes ;
10. bibliographie.

## Répartition proposée

| Responsable | Mission jusqu'au 20 octobre | Preuve à fournir |
|---|---|---|
| Rayan | coordination, décisions et intégration | planning, compte rendu, version finale du rapport |
| Jordi | données SPX et règles de nettoyage | dictionnaire des champs, extraction test, statistiques de qualité |
| Matthieu | théorie et méthodes de calibration | section bibliographique et comparaison des trois méthodes |
| Ilan | stabilité, distances et incertitude | protocole KL/JS/Wasserstein et synthèse de Taboga |
| Nathan | Julia, modèle factoriel et tests | dépôt exécutable, fonctions de contrôle, architecture dynamique |

La répartition doit être validée par l'équipe. Chaque partie doit être relue par au moins un autre membre.

## Planning

### Vendredi 16 octobre

- confirmer l'accès aux données ;
- figer le protocole principal ;
- créer le dépôt, l'environnement Julia et le squelette du rapport LaTeX ;
- répartir les sections et les tâches de code.

### Samedi 17 octobre

- obtenir une première chaîne d'options propre ;
- coder les contrôles de données et le baseline sur données synthétiques ;
- rédiger le cadre théorique et la bibliographie.

### Dimanche 18 octobre

- appliquer le baseline aux données réelles si disponibles ;
- produire quatre graphiques : données brutes, smile lissée, prix reconstruits et RND ;
- comparer plusieurs règles de filtrage.

### Lundi 19 octobre

- consolider les résultats et les limites ;
- finaliser le rapport ;
- créer un support de huit à dix diapositives ;
- répéter la présentation et chronométrer chaque intervenant.

### Mardi 20 octobre

- relire les équations, figures, sources et conclusions ;
- vérifier que le code reproduit les figures ;
- exporter les PDF ;
- envoyer le rapport et le support avec une marge de sécurité.

## Support oral recommandé

1. titre, équipe et problématique ;
2. pourquoi une RND commune plutôt qu'une volatilité Black–Scholes unique ;
3. chaîne scientifique du projet ;
4. données SPX et filtrage ;
5. Breeden–Litzenberger et contrôles ;
6. premier résultat ou démonstration synthétique ;
7. comparaison future des trois méthodes ;
8. stabilité, facteurs et prévision ;
9. application à la couverture ;
10. avancement, risques et prochaines étapes.

## Critère de réussite du premier suivi

Le projet sera crédible si l'équipe peut montrer une chaîne reproductible allant d'une table d'options documentée à une densité contrôlée, tout en expliquant clairement les limites liées à la liquidité, au lissage, à la maturité et à l'incertitude. Une stratégie de trading complète n'est pas encore nécessaire à ce stade.
