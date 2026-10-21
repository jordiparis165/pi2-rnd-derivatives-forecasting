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
from scipy.interpolate import PchipInterpolator

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

    # Interpolation uniquement graphique entre les maturités effectivement
    # calibrées. PCHIP évite les oscillations que produirait une spline cubique
    # sur seulement six coupes. Chaque coupe intermédiaire est renormalisée.
    y_smooth = np.linspace(y.min(), y.max(), 90)
    z_smooth = PchipInterpolator(y, Z, axis=0)(y_smooth)
    z_smooth = np.maximum(z_smooth, 0.0)
    z_smooth /= np.trapezoid(z_smooth, x, axis=1)[:, None]
    X_smooth, Y_smooth = np.meshgrid(x, y_smooth)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig = plt.figure(figsize=(12.6, 7.6), facecolor="white")
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(
        X_smooth,
        Y_smooth,
        z_smooth,
        cmap=cm.viridis,
        rcount=len(y_smooth),
        ccount=150,
        linewidth=0,
        antialiased=True,
        alpha=0.88,
        shade=True,
    )

    # Les lignes sombres matérialisent les six coupes réellement calibrées ;
    # la surface colorée située entre elles n'est qu'une aide visuelle.
    for maturity, density_slice in zip(y, Z):
        ax.plot(
            x,
            np.full_like(x, maturity),
            density_slice,
            color="#17202A",
            linewidth=1.25,
            alpha=0.92,
            zorder=5,
        )

    ax.contourf(
        X_smooth,
        Y_smooth,
        z_smooth,
        zdir="z",
        offset=0,
        levels=18,
        cmap=cm.viridis,
        alpha=0.34,
    )
    ax.set_xlabel(r"Log-moneyness  $k=\log(K/F)$", labelpad=12)
    ax.set_ylabel("Maturité (jours)", labelpad=12)
    ax.set_zlabel(r"Densité $q_k(k)$", labelpad=9)
    ax.set_title(
        f"Structure par terme des densités risque-neutre SPX\n"
        f"Snapshot Cboe du {stamp:%d/%m/%Y}",
        pad=16,
        color="#111111",
        fontsize=17,
        fontweight="bold",
    )
    ax.set_yticks(y)
    ax.set_zlim(bottom=0)
    ax.view_init(elev=29, azim=-126)
    ax.set_box_aspect((1.55, 1.05, 0.72))
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor((0.97, 0.97, 0.97, 1.0))
        axis.pane.set_edgecolor((0.82, 0.82, 0.82, 1.0))
    ax.grid(True, alpha=0.28)
    colorbar = fig.colorbar(surf, ax=ax, shrink=0.68, pad=0.075, aspect=24)
    colorbar.set_label(r"Densité $q_k(k)$", rotation=90, labelpad=11)
    fig.text(
        0.5,
        0.018,
        "Lignes noires : maturités calibrées  •  Surface : interpolation visuelle PCHIP  •  Date d’observation fixe",
        ha="center",
        fontsize=9.2,
        color="#333333",
    )
    fig.subplots_adjust(left=0.02, right=0.91, top=0.86, bottom=0.09)
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
