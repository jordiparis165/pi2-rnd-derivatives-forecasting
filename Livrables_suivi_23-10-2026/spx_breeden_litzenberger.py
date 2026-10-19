"""Prototype reproductible SPX -> smile SVI -> RND Breeden-Litzenberger.

Source publique : Cboe delayed quotes API.
Le script télécharge une chaîne, choisit l'échéance la plus proche de 3 mois,
filtre les cotations, estime forward et discount factor par parité call-put,
calibre une SVI brute à cinq paramètres et exporte la courbe de calls lissée.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from scipy.optimize import brentq, least_squares
from scipy.special import ndtr


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "results"
for folder in (RAW, PROCESSED, RESULTS):
    folder.mkdir(parents=True, exist_ok=True)

CBOE_URL = "https://cdn.cboe.com/api/global/delayed_quotes/options/_SPX.json"
TARGET_DAYS = 91


def parse_symbol(symbol: str):
    match = re.fullmatch(r"SPXW?(\d{6})([CP])(\d{8})", symbol)
    if not match:
        return None
    expiry = datetime.strptime(match.group(1), "%y%m%d").date()
    return expiry, match.group(2), int(match.group(3)) / 1000.0


def download_chain() -> tuple[dict, Path]:
    response = requests.get(CBOE_URL, timeout=90)
    response.raise_for_status()
    payload = response.json()
    stamp = datetime.fromisoformat(payload["timestamp"])
    path = RAW / f"cboe_spx_{stamp:%Y%m%d_%H%M%S}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return payload, path


def dataframe_from_payload(payload: dict) -> tuple[pd.DataFrame, datetime, float]:
    stamp = datetime.fromisoformat(payload["timestamp"])
    spot = float(payload["data"]["current_price"])
    records = []
    for item in payload["data"]["options"]:
        parsed = parse_symbol(item["option"])
        if parsed is None:
            continue
        expiry, option_type, strike = parsed
        record = dict(item)
        record.update(expiry=expiry, option_type=option_type, strike=strike)
        records.append(record)
    frame = pd.DataFrame(records)
    return frame, stamp, spot


def select_expiry(frame: pd.DataFrame, stamp: datetime):
    expiries = sorted(frame["expiry"].unique())
    return min(expiries, key=lambda x: abs((x - stamp.date()).days - TARGET_DAYS))


def clean_quotes(frame: pd.DataFrame, stamp: datetime, spot: float, expiry):
    selected = frame.loc[frame["expiry"] == expiry].copy()
    selected["mid"] = (selected["bid"] + selected["ask"]) / 2.0
    selected["spread"] = selected["ask"] - selected["bid"]
    selected["relative_spread"] = selected["spread"] / selected["mid"].replace(0, np.nan)
    last = pd.to_datetime(selected["last_trade_time"], errors="coerce")
    selected["last_trade_age_hours"] = (pd.Timestamp(stamp) - last).dt.total_seconds() / 3600.0
    selected["quote_valid"] = (
        (selected["bid"] > 0)
        & (selected["ask"] >= selected["bid"])
        & (selected["mid"] >= 0.05)
        & (selected["relative_spread"] <= 0.35)
        & (selected["strike"] / spot).between(0.65, 1.40)
    )
    return selected


def estimate_forward_discount(selected: pd.DataFrame, spot: float):
    valid = selected.loc[selected["quote_valid"]]
    pairs = valid.pivot_table(index="strike", columns="option_type", values=["mid", "spread"], aggfunc="first").dropna()
    strikes = pairs.index.to_numpy(float)
    calls = pairs[("mid", "C")].to_numpy(float)
    puts = pairs[("mid", "P")].to_numpy(float)
    widths = pairs[("spread", "C")].to_numpy(float) + pairs[("spread", "P")].to_numpy(float)
    near = (strikes / spot > 0.90) & (strikes / spot < 1.10)
    x = strikes[near]
    y = (calls - puts)[near]
    weights = 1.0 / np.maximum(widths[near], 0.10) ** 2
    design = np.column_stack([np.ones_like(x), x])
    beta = np.linalg.lstsq(design * np.sqrt(weights[:, None]), y * np.sqrt(weights), rcond=None)[0]
    discount = -beta[1]
    forward = beta[0] / discount
    if not (0.90 < discount < 1.05 and 0.90 * spot < forward < 1.12 * spot):
        raise RuntimeError(f"Put-call parity estimate is implausible: D={discount}, F={forward}")
    fitted = design @ beta
    rmse = float(np.sqrt(np.average((y - fitted) ** 2, weights=weights)))
    return forward, discount, rmse, pairs


def bs_forward_call(forward, strike, discount, maturity, sigma):
    vol_t = sigma * math.sqrt(maturity)
    if vol_t <= 0:
        return discount * max(forward - strike, 0.0)
    d1 = (math.log(forward / strike) + 0.5 * vol_t * vol_t) / vol_t
    d2 = d1 - vol_t
    return discount * (forward * ndtr(d1) - strike * ndtr(d2))


def implied_vol(price, forward, strike, discount, maturity):
    intrinsic = discount * max(forward - strike, 0.0)
    upper = discount * forward
    if not (intrinsic - 1e-8 <= price < upper):
        return np.nan
    objective = lambda sigma: bs_forward_call(forward, strike, discount, maturity, sigma) - price
    try:
        return brentq(objective, 1e-4, 5.0, maxiter=200)
    except ValueError:
        return np.nan


def prepare_calibration(selected, pairs, forward, discount, maturity):
    rows = []
    for strike, row in pairs.iterrows():
        if strike >= forward:
            price = float(row[("mid", "C")])
            spread = float(row[("spread", "C")])
            source = "OTM call"
        else:
            price = float(row[("mid", "P")]) + discount * (forward - strike)
            spread = float(row[("spread", "P")])
            source = "OTM put + parity"
        iv = implied_vol(price, forward, float(strike), discount, maturity)
        if np.isfinite(iv) and 0.03 <= iv <= 2.0 and 0.72 <= strike / forward <= 1.28:
            rows.append({"strike": strike, "synthetic_call": price, "spread_proxy": spread, "iv": iv, "source": source})
    out = pd.DataFrame(rows).sort_values("strike")
    out["log_moneyness"] = np.log(out["strike"] / forward)
    out["total_variance"] = out["iv"] ** 2 * maturity
    return out


def svi_total_variance(k, params):
    a, b, rho, m, sigma = params
    return a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + sigma**2))


def calibrate_svi(calibration: pd.DataFrame):
    k = calibration["log_moneyness"].to_numpy()
    w = calibration["total_variance"].to_numpy()
    spread = calibration["spread_proxy"].to_numpy()
    weights = 1.0 / np.maximum(spread / np.median(spread), 0.25)
    x0 = np.array([max(np.min(w) * 0.5, 1e-4), 0.08, -0.4, 0.0, 0.15])

    def residuals(params):
        fitted = svi_total_variance(k, params)
        floor = params[0] + params[1] * params[4] * math.sqrt(max(1.0 - params[2] ** 2, 0.0))
        penalty = np.array([min(floor, 0.0) * 100.0])
        return np.concatenate([(fitted - w) * np.sqrt(weights), penalty])

    fit = least_squares(
        residuals,
        x0,
        bounds=([-0.25, 1e-5, -0.999, -1.0, 1e-4], [1.0, 5.0, 0.999, 1.0, 3.0]),
        max_nfev=10000,
    )
    if not fit.success:
        raise RuntimeError(f"SVI calibration failed: {fit.message}")
    return fit.x, fit.cost


def reconstructed_curve(params, forward, discount, maturity):
    strike_grid = np.linspace(0.55 * forward, 1.55 * forward, 1601)
    k = np.log(strike_grid / forward)
    total_variance = np.maximum(svi_total_variance(k, params), 1e-8)
    iv = np.sqrt(total_variance / maturity)
    calls = np.array([bs_forward_call(forward, K, discount, maturity, sigma) for K, sigma in zip(strike_grid, iv)])
    return pd.DataFrame({"strike": strike_grid, "log_moneyness": k, "svi_iv": iv, "call_price": calls})


def python_density(curve: pd.DataFrame, discount: float):
    strikes = curve["strike"].to_numpy()
    calls = curve["call_price"].to_numpy()
    first = np.gradient(calls, strikes, edge_order=2)
    second = np.gradient(first, strikes, edge_order=2)
    raw = second / discount
    positive = np.maximum(raw, 0.0)
    mass_raw = float(np.trapezoid(raw, strikes))
    mass_positive = float(np.trapezoid(positive, strikes))
    density = positive / mass_positive
    mean = float(np.trapezoid(strikes * density, strikes))
    negative_mass = float(np.trapezoid(np.maximum(-raw, 0.0), strikes))
    peak = float(np.max(raw))
    out = curve.copy()
    out["rnd_raw"] = raw
    out["rnd_normalized"] = density
    diagnostics = {
        "raw_density_mass_on_grid": mass_raw,
        "positive_density_mass_before_normalization": mass_positive,
        "negative_grid_fraction": float(np.mean(raw < -1e-10)),
        "material_negative_grid_fraction_below_0.1pct_peak": float(np.mean(raw < -1e-3 * peak)),
        "absolute_negative_mass": negative_mass,
        "minimum_raw_density": float(np.min(raw)),
        "maximum_raw_density": peak,
        "normalized_density_mean": mean,
    }
    return out, diagnostics


def create_figures(selected, calibration, curve, density, forward, spot, stamp, expiry):
    plt.style.use("seaborn-v0_8-whitegrid")
    navy, cyan, orange = "#153A5B", "#168AAD", "#E07A3F"

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    valid = selected.loc[selected["quote_valid"]]
    axes[0].scatter(valid["strike"] / spot, valid["relative_spread"], s=8, alpha=0.45, color=navy)
    axes[0].axhline(0.35, color=orange, ls="--", lw=1, label="seuil 35 %")
    axes[0].set(xlabel="Strike / spot", ylabel="Spread relatif", title="Liquidité des cotations retenues")
    axes[0].legend()
    ages = selected["last_trade_age_hours"].dropna().clip(lower=0, upper=24 * 10)
    axes[1].hist(ages, bins=40, color=cyan, alpha=0.85)
    axes[1].set(xlabel="Ancienneté du dernier trade (heures, tronquée à 10 jours)", ylabel="Nombre", title="Pourquoi le last price doit être filtré")
    fig.suptitle(f"Qualité de la chaîne SPX — {stamp:%d/%m/%Y}, échéance {expiry:%d/%m/%Y}")
    fig.tight_layout()
    fig.savefig(RESULTS / "01_data_quality.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.scatter(calibration["log_moneyness"], calibration["iv"], s=14, alpha=0.65, color=navy, label="IV observée / synthétique")
    central = curve[curve["log_moneyness"].between(calibration["log_moneyness"].min(), calibration["log_moneyness"].max())]
    ax.plot(central["log_moneyness"], central["svi_iv"], color=orange, lw=2.2, label="SVI, 5 paramètres")
    ax.set(xlabel="Log-moneyness log(K/F)", ylabel="Volatilité implicite", title="Calibration commune de la smile SPX")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "02_svi_smile.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.scatter(calibration["strike"], calibration["synthetic_call"], s=12, alpha=0.6, color=navy, label="Prix utilisés")
    ax.plot(curve["strike"], curve["call_price"], color=cyan, lw=2, label="Calls reconstruits par SVI")
    ax.axvline(forward, color=orange, ls="--", lw=1.2, label=f"Forward estimé {forward:.1f}")
    ax.set(xlabel="Strike", ylabel="Prix du call", title="Courbe lissée avant dérivation")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "03_call_curve.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.plot(density["strike"], density["rnd_normalized"], color=navy, lw=2.2)
    ax.axvline(forward, color=orange, ls="--", lw=1.2, label=f"Forward {forward:.1f}")
    ax.axvline(spot, color=cyan, ls=":", lw=1.4, label=f"Spot {spot:.1f}")
    ax.set(xlabel="Niveau terminal du SPX", ylabel="Densité risque-neutre", title="RND Breeden–Litzenberger issue de la smile SVI")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "04_risk_neutral_density.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    payload, raw_path = download_chain()
    frame, stamp, spot = dataframe_from_payload(payload)
    expiry = select_expiry(frame, stamp)
    maturity_days = (expiry - stamp.date()).days
    maturity = maturity_days / 365.0
    selected = clean_quotes(frame, stamp, spot, expiry)
    forward, discount, parity_rmse, pairs = estimate_forward_discount(selected, spot)
    calibration = prepare_calibration(selected, pairs, forward, discount, maturity)
    params, svi_cost = calibrate_svi(calibration)
    curve = reconstructed_curve(params, forward, discount, maturity)
    density, density_diag = python_density(curve, discount)

    model_prices = np.array([bs_forward_call(forward, K, discount, maturity, s) for K, s in zip(calibration["strike"], np.sqrt(np.maximum(svi_total_variance(calibration["log_moneyness"].to_numpy(), params), 1e-8) / maturity))])
    price_rmse = float(np.sqrt(np.mean((model_prices - calibration["synthetic_call"].to_numpy()) ** 2)))
    valid_count = int(selected["quote_valid"].sum())
    selected.to_csv(PROCESSED / f"spx_quotes_{stamp:%Y%m%d}_{expiry:%Y%m%d}.csv", index=False)
    calibration.to_csv(PROCESSED / f"spx_calibration_{stamp:%Y%m%d}_{expiry:%Y%m%d}.csv", index=False)
    curve.to_csv(RESULTS / "reconstructed_call_grid.csv", index=False)
    density.to_csv(RESULTS / "rnd_python.csv", index=False)

    diagnostics = {
        "source": CBOE_URL,
        "raw_file": str(raw_path.relative_to(ROOT)),
        "quote_timestamp": payload["timestamp"],
        "spot": spot,
        "selected_expiry": str(expiry),
        "maturity_days": maturity_days,
        "selected_contracts_before_filtering": int(len(selected)),
        "valid_contract_quotes": valid_count,
        "matched_call_put_strikes": int(len(pairs)),
        "calibration_points": int(len(calibration)),
        "forward_from_parity": forward,
        "discount_factor_from_parity": discount,
        "implied_continuous_rate": -math.log(discount) / maturity,
        "put_call_parity_rmse": parity_rmse,
        "svi_parameters": {k: float(v) for k, v in zip(["a", "b", "rho", "m", "sigma"], params)},
        "svi_least_squares_cost": float(svi_cost),
        "call_price_rmse": price_rmse,
        **density_diag,
    }
    (RESULTS / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    create_figures(selected, calibration, curve, density, forward, spot, stamp, expiry)
    print(json.dumps(diagnostics, indent=2))


if __name__ == "__main__":
    main()
