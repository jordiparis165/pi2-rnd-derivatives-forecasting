"""Construit une surface 3D de RND selon la maturité à partir d'un snapshot SPX.

Important : la seconde dimension est la maturité, pas le temps calendaire.
Une surface dynamique date × moneyness exigera un historique de snapshots.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm

from spx_breeden_litzenberger import (
    calibrate_svi,
    clean_quotes,
    dataframe_from_payload,
    estimate_forward_discount,
    prepare_calibration,
    python_density,
    reconstructed_curve,
)


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RESULTS = ROOT / "results"
TARGET_DAYS = [30, 60, 91, 120, 150, 180]
K_GRID = np.linspace(-0.32, 0.24, 281)


def latest_snapshot():
    paths = sorted(RAW.glob("cboe_spx_*.json"))
    if not paths:
        raise FileNotFoundError("Aucun snapshot Cboe dans data/raw")
    path = paths[-1]
    return json.loads(path.read_text(encoding="utf-8")), path


def choose_expiries(frame, stamp):
    expiries = sorted(frame["expiry"].unique())
    chosen = []
    for target in TARGET_DAYS:
        expiry = min(expiries, key=lambda x: abs((x - stamp.date()).days - target))
        if expiry not in chosen:
            chosen.append(expiry)
    return chosen


def main():
    payload, raw_path = latest_snapshot()
    frame, stamp, spot = dataframe_from_payload(payload)
    expiries = choose_expiries(frame, stamp)
    surfaces, diagnostics = [], []

    for expiry in expiries:
        days = (expiry - stamp.date()).days
        maturity = days / 365.0
        try:
            selected = clean_quotes(frame, stamp, spot, expiry)
            forward, discount, parity_rmse, pairs = estimate_forward_discount(selected, spot)
            calibration = prepare_calibration(selected, pairs, forward, discount, maturity)
            if len(calibration) < 30:
                raise RuntimeError(f"Seulement {len(calibration)} points de calibration")
            params, cost = calibrate_svi(calibration)
            curve = reconstructed_curve(params, forward, discount, maturity)
            density, density_diag = python_density(curve, discount)

            # Conversion de la densité en prix q_S(s) vers la densité de
            # log-moneyness q_k(k) = q_S(F exp(k)) * F exp(k).
            k_native = density["log_moneyness"].to_numpy()
            strike_native = density["strike"].to_numpy()
            qk_native = density["rnd_normalized"].to_numpy() * strike_native
            qk = np.interp(K_GRID, k_native, qk_native, left=0.0, right=0.0)
            mass = np.trapezoid(qk, K_GRID)
            qk = qk / mass
            for k, value in zip(K_GRID, qk):
                surfaces.append({
                    "quote_date": stamp.date().isoformat(),
                    "expiry": expiry.isoformat(),
                    "maturity_days": days,
                    "log_moneyness": k,
                    "density_log_moneyness": value,
                    "forward": forward,
                })
            diagnostics.append({
                "expiry": expiry.isoformat(), "maturity_days": days,
                "calibration_points": len(calibration), "forward": forward,
                "discount": discount, "parity_rmse": parity_rmse,
                "svi_cost": cost, **density_diag,
            })
        except Exception as exc:
            diagnostics.append({"expiry": expiry.isoformat(), "maturity_days": days, "error": str(exc)})

    surface = pd.DataFrame(surfaces)
    if surface.empty:
        raise RuntimeError("Aucune maturité n'a pu être calibrée")
    surface.to_csv(RESULTS / "rnd_term_structure.csv", index=False)
    (RESULTS / "rnd_term_structure_diagnostics.json").write_text(json.dumps({"source_snapshot": str(raw_path.relative_to(ROOT)), "quote_timestamp": payload["timestamp"], "expiries": diagnostics}, indent=2), encoding="utf-8")

    pivot = surface.pivot(index="maturity_days", columns="log_moneyness", values="density_log_moneyness").sort_index()
    x = pivot.columns.to_numpy(float)
    y = pivot.index.to_numpy(float)
    X, Y = np.meshgrid(x, y)
    Z = pivot.to_numpy(float)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig = plt.figure(figsize=(11.5, 7.2))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(X, Y, Z, cmap=cm.viridis, linewidth=0.15, edgecolor=(1, 1, 1, 0.25), antialiased=True, alpha=0.95)
    ax.set_xlabel("Log-moneyness  log(K/F)", labelpad=10)
    ax.set_ylabel("Maturité (jours)", labelpad=10)
    ax.set_zlabel("Densité de log-moneyness", labelpad=9)
    ax.set_title(f"Structure par terme des densités risque-neutre SPX\nSnapshot Cboe du {stamp:%d/%m/%Y}", pad=18, color="#153A5B", fontweight="bold")
    ax.view_init(elev=27, azim=-132)
    fig.colorbar(surf, ax=ax, shrink=0.62, pad=0.09, label="Densité")
    fig.text(0.5, 0.015, "Surface selon la maturité — ne constitue pas encore une dynamique temporelle", ha="center", fontsize=9, color="#60717D")
    fig.savefig(RESULTS / "05_rnd_surface_3d_maturity.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10.5, 5.4))
    image = ax.imshow(Z, aspect="auto", origin="lower", extent=[x.min(), x.max(), y.min(), y.max()], cmap="viridis")
    ax.set(xlabel="Log-moneyness  log(K/F)", ylabel="Maturité (jours)", title="Carte thermique des RND SPX par maturité")
    fig.colorbar(image, ax=ax, label="Densité de log-moneyness")
    fig.tight_layout()
    fig.savefig(RESULTS / "06_rnd_heatmap_maturity.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    print(json.dumps({"successful_maturities": sorted(surface["maturity_days"].unique().tolist()), "rows": len(surface)}, indent=2))


if __name__ == "__main__":
    main()
