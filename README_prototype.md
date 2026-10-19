# Prototype SPX — Breeden–Litzenberger

## Exécution

Depuis PowerShell, dans le dossier du projet :

```powershell
python -m pip install -r requirements.txt
.\run_prototype.ps1
```

Le projet contient une distribution portable de Julia 1.10.10 dans `.tools/`. Elle n'est pas nécessaire à joindre au rapport.

## Pipeline

1. téléchargement de la chaîne SPX différée de Cboe ;
2. sélection de l'échéance la plus proche de 91 jours ;
3. filtrage bid-ask et liquidité ;
4. estimation du forward et du discount factor par parité call-put ;
5. conversion des puts OTM en calls synthétiques ;
6. calcul des volatilités implicites ;
7. calibration d'une SVI brute à cinq paramètres ;
8. reconstruction d'une courbe de calls régulière ;
9. application de Breeden–Litzenberger en Python ;
10. réplication indépendante de la dérivée, de la normalisation et des moments en Julia.

## Fichiers importants

- `src/spx_breeden_litzenberger.py` : acquisition, nettoyage, SVI et RND ;
- `src/breeden_litzenberger.jl` : calcul Julia de la densité ;
- `data/raw/` : snapshot Cboe brut ;
- `data/processed/` : chaîne nettoyée et points de calibration ;
- `results/diagnostics.json` : chiffres utilisés dans le rapport ;
- `results/rnd_python.csv` et `results/rnd_julia.csv` : densités comparables ;
- `results/01_...png` à `04_...png` : figures du rapport.

## Limite d'accès

L'API Cboe publique fournit une photographie différée, pas l'historique complet nécessaire à l'étude dynamique. L'équipe doit encore exporter l'historique depuis Bloomberg ou obtenir un accès OptionMetrics/Cboe DataShop.
