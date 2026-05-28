"""ATTR001 Pass 2c — family G: disclosure event-study (OPENDART KOSPI, metadata only).

Per the locked pre-registration: event-presence by category FLAG (title/metadata only — NO
body parser, NO effective-date extraction), entry strictly t+1 after rcept_dt, abnormal
return vs same-date universe-mean control. Preserve-all, diagnostic-only. The pre-computed
flags capture PRESENCE not magnitude (R-family closed on title-only insufficiency — kept as
caveat, not veto).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))
from src.audit.attribution.attr001_influence_map import (  # noqa: E402
    load, add_forward_returns, regime_mask, HORIZONS, OUT, PAST_START,
)

DART = REPO / "research_input_data/inputs/events/opendart_kospi_disclosures_20180101_20260505.parquet"
FLAGS = ["flag_treasury_stock", "flag_earnings", "flag_capital_raise", "flag_cb_bw",
         "flag_capital_reduction", "flag_merger_split", "flag_contract", "flag_litigation",
         "flag_audit_issue", "flag_large_holder", "flag_trading_halt", "flag_event_risk"]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("[ATTR001-2c] loading panel + events ...", flush=True)
    panel = add_forward_returns(load())
    panel = panel.loc[~panel["tv_estimated"].fillna(False)].copy()
    # universe-mean forward return per date (control)
    um = panel.groupby("date")[[f"pred_ret_{h}" for h in HORIZONS]].mean()
    um.columns = [f"univ_{h}" for h in HORIZONS]
    panel = panel.merge(um, on="date", how="left")
    # abnormal forward return per (ticker,date) = stock - universe (same date)
    for h in HORIZONS:
        panel[f"abn_{h}"] = panel[f"pred_ret_{h}"] - panel[f"univ_{h}"]
    pcols = ["date", "ticker"] + [f"abn_{h}" for h in HORIZONS]
    px = panel[pcols].copy()
    px["ticker"] = px["ticker"].astype(str)  # plain object str (match event side for merge_asof by-key)
    px = px.sort_values("date").reset_index(drop=True)  # merge_asof requires sort by the ON key

    ev = pd.read_parquet(DART, columns=["rcept_dt", "stock_code"] + FLAGS)
    ev["ticker"] = ev["stock_code"].astype(str).str.zfill(6)
    ev["rcept_dt"] = pd.to_datetime(ev["rcept_dt"].astype(str), format="%Y%m%d", errors="coerce")
    ev = ev.dropna(subset=["rcept_dt", "ticker"]).sort_values("rcept_dt").reset_index(drop=True)
    # map each event to entry = first panel date STRICTLY AFTER rcept_dt (t+1), same ticker
    ev_e = pd.merge_asof(ev, px, left_on="rcept_dt", right_on="date", by="ticker",
                         direction="forward", allow_exact_matches=False)
    ev_e = ev_e.dropna(subset=["date"])
    print(f"[ATTR001-2c] {len(ev)} events, {len(ev_e)} matched to a t+1 panel entry", flush=True)

    rows = []
    for flag in FLAGS:
        sel = ev_e[ev_e[flag] == True]  # noqa: E712
        for regime in ("FULL", "PAST", "PRESENT"):
            s = sel[regime_mask(sel, regime)] if len(sel) else sel
            for h in HORIZONS:
                a = pd.to_numeric(s[f"abn_{h}"], errors="coerce").dropna()
                n = len(a)
                mean_abn = float(a.mean()) if n else np.nan
                tstat = float(a.mean() / (a.std() / np.sqrt(n))) if n > 2 and a.std() > 0 else np.nan
                rows.append({
                    "signal_id": flag, "family": "G_event", "horizon_d": h, "regime": regime,
                    "mean_abnormal_ret": mean_abn, "abn_tstat": tstat, "n_events": n,
                    "metric_note": "EVENT-STUDY t+1 entry; abnormal = stock - universe-mean(same date); title/flag presence only",
                    "status": "measured_with_caveat",
                    "caveat": "metadata/title flag (presence not magnitude); R-family closed on title-only insufficiency (caveat not veto); overlapping events; no body parser",
                })
        print(f"[ATTR001-2c] done {flag}: {len(sel)} events", flush=True)
    pd.DataFrame(rows).to_csv(OUT / "influence_map_pass2c_events.csv", index=False, lineterminator="\n")
    print(f"[ATTR001-2c] wrote {len(rows)} rows", flush=True)


if __name__ == "__main__":
    main()
