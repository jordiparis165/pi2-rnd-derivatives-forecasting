# Contribuer au projet

## Première installation

```powershell
git clone https://github.com/jordiparis165/pi2-rnd-derivatives-forecasting.git
cd pi2-rnd-derivatives-forecasting
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Méthode de travail recommandée

1. Mettre la branche principale à jour : `git switch main`, puis `git pull`.
2. Créer une branche : `git switch -c prenom/sujet-court`.
3. Effectuer et tester les changements.
4. Enregistrer le travail : `git add .`, puis `git commit -m "Description concise"`.
5. Publier la branche : `git push -u origin prenom/sujet-court`.
6. Ouvrir une pull request sur GitHub vers `main`.

Ne pas committer de mot de passe, jeton Bloomberg, identifiant personnel ou export de données soumis à une licence restrictive.

## Conventions

- placer le code d’analyse dans `src/` ;
- conserver les données brutes immuables dans `data/raw/` ;
- écrire les données transformées dans `data/processed/` ;
- écrire les figures et diagnostics reproductibles dans `results/` ;
- documenter toute nouvelle source dans `data/README_acces_donnees.md` ;
- mettre à jour `references.bib` pour toute référence scientifique ajoutée.

Avant une pull request, vérifier au minimum :

```powershell
python -m compileall src
python src/spx_breeden_litzenberger.py
python src/rnd_surface_3d.py
```

Les gros fichiers de données sous licence ne doivent pas être ajoutés au dépôt public. Décrire plutôt leur provenance et la procédure d’accès.
