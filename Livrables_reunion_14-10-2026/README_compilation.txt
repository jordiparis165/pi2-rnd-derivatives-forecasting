PROJET PI2 N°176 — FICHIERS À ENVOYER

PDF principal : Dossier_complet_reunion_14-10-2026.pdf
PDF court : 01_Brief_reunion_16h.pdf
PDF bibliographie : 03_Bibliographie_structuree.pdf

Sources LaTeX :
- bibliographie_projet_176.tex
- brief_reunion_14-10-2026.tex
- references.bib

Compilation de la bibliographie avec une distribution LaTeX :

    pdflatex bibliographie_projet_176.tex
    biber bibliographie_projet_176
    pdflatex bibliographie_projet_176.tex
    pdflatex bibliographie_projet_176.tex

Le document utilise BibLaTeX avec le backend Biber.
