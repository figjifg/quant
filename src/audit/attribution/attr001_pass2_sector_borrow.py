"""ATTR001 Pass 2a — cross-section families C (sector PIT) + E (borrow balance).

Reuses the locked pass-1 engine (load / forward returns / IC / decile / regime / placebo).
Same pre-registration (research/experiments/ATTR001_korean_data_influence_map.md), same
metrics, preserve-all, diagnostic-only. Output rows appended as pass-2a.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))
from src.audit.attribution.attr001_influence_map import (  # noqa: E402
    load, add_forward_returns, daily_ic, decile_spread, regime_mask, HORIZONS, RNG, OUT,
)

SECTOR_PATH = REPO / "data/processed/stock_with_sector_daily_pit.csv"
BORROW_PATH = REPO / "data/acquired/w000_kr_borrow/kr_borrow_balance_2018_2026.csv"


def build(panel: pd.DataFrame) -> dict[str, tuple[str, str]]:
    g = panel.groupby("ticker", group_keys=False)
    # building blocks (PIT: uses close<=T)
    panel["_mom5"] = g["close"].transform(lambda s: s / s.shift(5) - 1.0)
    panel["_mom20"] = g["close"].transform(lambda s: s / s.shift(20) - 1.0)
    defs: dict[str, tuple[str, str]] = {}

    # ---- C: sector (PIT) ----
    sec = pd.read_csv(SECTOR_PATH, usecols=["date", "ticker", "sector_code"], dtype={"ticker": str})
    sec["date"] = pd.to_datetime(sec["date"], errors="coerce")
    sec["ticker"] = sec["ticker"].str.zfill(6)
    sec["sector_code"] = sec["sector_code"].astype("string")
    panel = panel.merge(sec, on=["date", "ticker"], how="left")
    # sector aggregates per (date, sector) from info<=T (uses _mom20 / daily_return at T)
    bysec = panel.groupby(["date", "sector_code"])
    panel["sig_sector_rs"] = bysec["_mom20"].transform("mean")            # sector momentum
    panel["sig_sector_breadth"] = bysec["daily_return"].transform(lambda s: (s > 0).mean())
    panel["sig_within_sector_rs"] = panel["_mom20"] - panel["sig_sector_rs"]  # stock vs its sector
    for s in ["sig_sector_rs", "sig_sector_breadth", "sig_within_sector_rs"]:
        defs[s] = ("C_sector", "PIT sector mapping (E014 closed on PIT-sector look-ahead; caveat not veto)")

    # ---- E: borrow balance (W000 item6, balance-only) ----
    bor = pd.read_csv(BORROW_PATH, usecols=["date", "ticker", "borrow_balance_shares"], dtype={"ticker": str})
    bor["date"] = pd.to_datetime(bor["date"], errors="coerce")
    bor["ticker"] = bor["ticker"].str.zfill(6)
    bor["borrow_balance_shares"] = pd.to_numeric(bor["borrow_balance_shares"], errors="coerce")
    panel = panel.merge(bor, on=["date", "ticker"], how="left")
    gb = panel.sort_values(["ticker", "date"]).groupby("ticker", group_keys=False)
    panel["sig_borrow_ratio"] = panel["borrow_balance_shares"] / panel["shares_out"].replace(0, np.nan)
    panel["sig_borrow_chg5"] = gb["borrow_balance_shares"].transform(lambda s: s / s.shift(5) - 1.0)
    panel["sig_borrow_chg20"] = gb["borrow_balance_shares"].transform(lambda s: s / s.shift(20) - 1.0)
    # interactions: borrow rising while price falling (pressure); borrow falling while price rising (cover)
    panel["sig_borrow_pressure"] = panel["sig_borrow_chg5"] * (-panel["_mom5"])
    panel["sig_borrow_cover"] = (-panel["sig_borrow_chg5"]) * panel["_mom5"]
    for s in ["sig_borrow_ratio", "sig_borrow_chg5", "sig_borrow_chg20", "sig_borrow_pressure", "sig_borrow_cover"]:
        defs[s] = ("E_borrow", "borrow BALANCE only (no fee/rebate/restriction); W000 item6; 2018+ coverage")
    return defs, panel


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("[ATTR001-2a] loading ...", flush=True)
    panel = add_forward_returns(load())
    defs, panel = build(panel)
    headline = panel.loc[~panel["tv_estimated"].fillna(False)].copy()
    print(f"[ATTR001-2a] {len(defs)} signals; headline rows={len(headline):,}", flush=True)

    rows = []
    for sig, (family, caveat) in defs.items():
        for regime in ("FULL", "PAST", "PRESENT"):
            sub = headline.loc[regime_mask(headline, regime)]
            for h in HORIZONS:
                ic = daily_ic(sub, sig, f"pred_ret_{h}").dropna()
                ic_mean = float(ic.mean()) if len(ic) else np.nan
                ic_t = float(ic.mean() / (ic.std() / np.sqrt(len(ic)))) if len(ic) > 2 and ic.std() > 0 else np.nan
                ic_hit = float((ic > 0).mean()) if len(ic) else np.nan
                ls, lo = decile_spread(sub, sig, f"exec_ret_{h}")
                placebo = ""
                if h == 5 and len(sub):
                    perm = sub.copy()
                    perm[sig] = perm.groupby("date")[sig].transform(lambda s: pd.Series(RNG.permutation(s.values), index=s.index))
                    pic = daily_ic(perm, sig, "pred_ret_5").dropna()
                    placebo = float(pic.mean()) if len(pic) else np.nan
                rows.append({
                    "signal_id": sig, "family": family, "horizon_d": h, "regime": regime,
                    "ic_mean_pred": ic_mean, "ic_tstat": ic_t, "ic_hit_rate": ic_hit, "n_dates": int(len(ic)),
                    "decile_ls_exec_netcost": ls, "longonly_topdecile_exec_netcost": lo,
                    "placebo_ic_5d": placebo,
                    "status": "measured_with_caveat", "caveat": caveat,
                    "execution_note": "long-only executable view; long-short statistical only",
                    "label_note": "ic=close-to-close prediction; decile=T+1-open executability net cost",
                })
        print(f"[ATTR001-2a] done {sig}", flush=True)

    pd.DataFrame(rows).to_csv(OUT / "influence_map_pass2a_sector_borrow.csv", index=False, lineterminator="\n")
    print(f"[ATTR001-2a] wrote {len(rows)} rows", flush=True)


if __name__ == "__main__":
    main()
