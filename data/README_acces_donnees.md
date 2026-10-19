# État des accès aux données — 16 octobre 2026

## Cboe

**Accès confirmé** à la chaîne SPX publique et différée :

`https://cdn.cboe.com/api/global/delayed_quotes/options/_SPX.json`

Le 16 octobre 2026, l'API a fourni une chaîne horodatée, le niveau courant du SPX, ainsi que les champs bid, ask, volatilité, volume, open interest, prix et heure de dernière transaction.

Limite : cet endpoint fournit une photographie courante différée. Il ne constitue pas à lui seul une base historique quotidienne sur un mois. L'accès à Cboe DataShop, Bloomberg ou OptionMetrics reste nécessaire pour l'étude dynamique complète.

## Bloomberg

**Accès non confirmé sur cette machine.** Aucun terminal Bloomberg, package `blpapi` ou connecteur `xbbg` n'est installé. L'accès doit être testé sur un poste Bloomberg de l'école et l'extraction historique doit être exportée dans un format reproductible, idéalement CSV ou Parquet.

## Échantillon créé

- date de cotation : 16 octobre 2026 ;
- sous-jacent : SPX ;
- échéance : 15 janvier 2027 ;
- horizon : 91 jours ;
- fichier brut : `data/raw/cboe_spx_20261016_171217.json` ;
- fichier nettoyé : `data/processed/spx_quotes_20261016_20270115.csv` ;
- données de calibration : `data/processed/spx_calibration_20261016_20270115.csv`.

## Champs à demander pour l'historique

Date et heure de snapshot, symbole, échéance, strike, type call/put, bid, ask, last, heure du dernier trade, volume, open interest, spot, taux ou courbe de taux et, si possible, dividendes ou forward.
