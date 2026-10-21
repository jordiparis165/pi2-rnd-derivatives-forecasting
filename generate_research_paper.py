"""Compile le papier LaTeX et prépare le dossier de livraison.

La source LaTeX est canonique : équations, citations et tableaux sont composés comme
dans un article scientifique plutôt que reconstruits en texte simple dans le PDF.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "Livrables_suivi_23-10-2026"
MANUSCRIPT = ROOT / "papier_recherche_PI2_176.tex"


def build() -> Path:
    tectonic = shutil.which("tectonic")
    if tectonic is None:
        raise RuntimeError(
            "Tectonic est requis. Installez-le puis relancez "
            "python generate_research_paper.py."
        )

    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pi2-paper-") as temp_dir:
        command = [
            tectonic,
            "--keep-logs",
            "--keep-intermediates",
            "--outdir",
            temp_dir,
            str(MANUSCRIPT),
        ]
        subprocess.run(command, cwd=ROOT, check=True)
        compiled = Path(temp_dir) / "papier_recherche_PI2_176.pdf"
        if not compiled.exists():
            raise RuntimeError("La compilation LaTeX n'a pas produit le PDF attendu.")
        destination = OUT / "Papier_recherche_PI2_176.pdf"
        shutil.copy2(compiled, destination)

    shutil.copy2(MANUSCRIPT, OUT / MANUSCRIPT.name)
    shutil.copy2(ROOT / "references.bib", OUT / "references.bib")
    shutil.copy2(ROOT / "src" / "rnd_surface_3d.py", OUT / "rnd_surface_3d.py")
    return destination


if __name__ == "__main__":
    print(build())
