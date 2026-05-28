"""ATTR001 Pass 2b — family F: market / macro signals (time-series CONDITIONAL).

Per the locked pre-registration: market/macro signals are the SAME value for all stocks,
so cross-sectional rank-IC is inappropriate. Instead we measure whether the signal (known
at T, lagged 1 extra day for availability) predicts the UNIVERSE-MEAN forward return
(market timing) — time-series Spearman + tercile-conditional spread, per regime. Preserve
-all, diagnostic-only. CAVEAT: overlapping h-day returns autocorrelate → significance is
overstated; report tercile spread + n alongside, and treat as influence not edge.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))
from src.audit.attribution.attr001_influence_map import (  # noqa: E402
    load, add_forward_returns, regime_mask, HORIZONS, OUT,
)

MACRO = REPO / "research_input_data/inputs/macro_features"


def _fred(name: str, col: str) -> pd.DataFrame:
    p = next(iter(sorted(MACRO.glob(f"{name}*.csv"))), None)
    if p is None:
        return pd.DataFrame(columns=["date", col])
    d = pd.read_csv(p)
    d = d.rename(columns={"observation_date": "date"})
    d["date"] = pd.to_datetime(d["date"], errors="coerce")
    # value column = first non-date column (FRED uses the series code, which varies)
    valcol = next(c for c in d.columns if c != "date")
    d[col] = pd.to_numeric(d[valcol], errors="coerce")
    return d[["date", col]].dropna()


def build_macro(dates: pd.DatetimeIndex) -> pd.DataFrame:
    base = pd.DataFrame({"date": dates}).sort_values("date")
    def join(df, col):
        nonlocal base
        base = base.merge(df, on="date", how="left")
        base[col] = base[col].ffill()  # carry last obs to KRX trading dates
    join(_fred("fred_dexkous_usdkrw", "DEXKOUS"), "DEXKOUS")
    join(_fred("fred_vix", "VIXCLS"), "VIXCLS")
    join(_fred("fred_dgs3mo", "DGS3MO"), "DGS3MO")
    join(_fred("fred_dxy", "DXY") if list(MACRO.glob("fred_dxy*")) else pd.DataFrame(columns=["date","DXY"]), "DXY")
    # KRX breadth
    bp = next(iter(sorted(MACRO.glob("krx_market_breadth_kospi*.csv"))), None)
    if bp is not None:
        b = pd.read_csv(bp)
        b["date"] = pd.to_datetime(b["date"], errors="coerce")
        for c in ["advance_ratio", "pct_above_ma20"]:
            if c in b.columns:
                base = base.merge(b[["date", c]], on="date", how="left")
    # signals (level/change). Then LAG 1 extra trading day for availability.
    s = pd.DataFrame({"date": base["date"]})
    s["sig_usdkrw_chg5"] = base["DEXKOUS"] / base["DEXKOUS"].shift(5) - 1.0
    s["sig_vix_level"] = base["VIXCLS"]
    s["sig_vix_chg5"] = base["VIXCLS"] / base["VIXCLS"].shift(5) - 1.0
    s["sig_us3mo_chg20"] = base["DGS3MO"] - base["DGS3MO"].shift(20)
    if "DXY" in base and base["DXY"].notna().any():
        s["sig_dxy_chg5"] = base["DXY"] / base["DXY"].shift(5) - 1.0
    if "advance_ratio" in base:
        s["sig_breadth_advance"] = base["advance_ratio"]
    if "pct_above_ma20" in base:
        s["sig_breadth_ma20"] = base["pct_above_ma20"]
    sigcols = [c for c in s.columns if c.startswith("sig_")]
    for c in sigcols:
        s[c] = s[c].shift(1)  # availability lag: use value known at T-1 to predict from T
    return s, sigcols


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("[ATTR001-2b] loading panel for universe-mean forward returns ...", flush=True)
    panel = add_forward_returns(load())
    panel = panel.loc[~panel["tv_estimated"].fillna(False)]
    # universe equal-weight mean forward return per date, per horizon
    um = panel.groupby("date")[[f"pred_ret_{h}" for h in HORIZONS]].mean().reset_index()
    macro, sigcols = build_macro(pd.DatetimeIndex(sorted(um["date"].unique())))
    df = um.merge(macro, on="date", how="left")
    print(f"[ATTR001-2b] {len(sigcols)} macro signals; {len(df)} dates", flush=True)

    rows = []
    for sig in sigcols:
        for regime in ("FULL", "PAST", "PRESENT"):
            d = df.loc[regime_mask(df, regime)]
            for h in HORIZONS:
                sub = d[[sig, f"pred_ret_{h}"]].dropna()
                n = len(sub)
                ts_corr = float(sub[sig].rank().corr(sub[f"pred_ret_{h}"].rank())) if n >= 30 else np.nan
                # tercile-conditional universe mean forward return (high - low)
                hi_lo = np.nan
                if n >= 60:
                    q = pd.qcut(sub[sig].rank(method="first"), 3, labels=False, duplicates="drop")
                    if q.nunique() == 3:
                        hi_lo = float(sub[f"pred_ret_{h}"][q == 2].mean() - sub[f"pred_ret_{h}"][q == 0].mean())
                rows.append({
                    "signal_id": sig, "family": "F_market_macro", "horizon_d": h, "regime": regime,
                    "ts_corr_pred": ts_corr, "tercile_hi_lo_univ_ret": hi_lo, "n_dates": n,
                    "metric_note": "TIME-SERIES market-timing (univ-mean fwd ret); NOT cross-section IC",
                    "status": "measured_with_caveat",
                    "caveat": "overlapping h-day returns autocorrelate (significance overstated); macro lagged 1 extra day; market-timing influence not edge",
                })
        print(f"[ATTR001-2b] done {sig}", flush=True)
    pd.DataFrame(rows).to_csv(OUT / "influence_map_pass2b_macro.csv", index=False, lineterminator="\n")
    print(f"[ATTR001-2b] wrote {len(rows)} rows", flush=True)


if __name__ == "__main__":
    main()
