"""ATTR001 enhancements — pre-registration compliance items flagged by the Referee.

A) artifact-fix audit table (gap-guard NaN counts + before/after forward-return stats).
B) data_gated rows (KR fundamentals; borrow fee/rebate/restriction/buy-in) preserved in map.
C) FDR/q-value columns added to the cross-section / macro / event maps.
D) liquidity-bucket breakdown (20d traded-value tercile + market-cap tercile + 거래대금추정 slice).
E) event matched control (same date x sector x cap bucket) + overlap de-dup (unique ticker/date).
(F macro beta-adjusted/interaction = documented caveat in FINDINGS_corrected.md.)
Diagnostic-only, preserve-all.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))
from src.audit.attribution.attr001_influence_map import (  # noqa: E402
    load, add_forward_returns, daily_ic, regime_mask, HORIZONS, OUT, build_signals,
)
from src.audit.attribution.attr001_pass2_sector_borrow import build as build_sb  # noqa: E402

SECTOR_PATH = REPO / "data/processed/stock_with_sector_daily_pit.csv"
DART = REPO / "research_input_data/inputs/events/opendart_kospi_disclosures_20180101_20260505.parquet"
FLAGS = ["flag_treasury_stock", "flag_earnings", "flag_capital_raise", "flag_cb_bw",
         "flag_capital_reduction", "flag_merger_split", "flag_contract", "flag_litigation",
         "flag_audit_issue", "flag_large_holder", "flag_trading_halt", "flag_event_risk"]


def bh_qvalues(p: pd.Series) -> pd.Series:
    """Benjamini-Hochberg FDR q-values."""
    p = p.copy()
    m = p.notna()
    pv = p[m].values
    n = len(pv)
    order = np.argsort(pv)
    ranked = pv[order]
    q = ranked * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.full(n, np.nan)
    out[order] = np.clip(q, 0, 1)
    res = p.copy(); res[m] = out
    return res


def A_audit_table(panel_guarded: pd.DataFrame) -> None:
    # recompute RAW (no gap guard) forward returns for comparison
    raw = panel_guarded.sort_values(["ticker", "date"]).copy()
    g = raw.groupby("ticker", group_keys=False)
    rows = []
    for h in HORIZONS:
        fwd = g["close"].shift(-h) / raw["close"] - 1.0
        fwd_date = g["date"].shift(-h)
        gap = (fwd_date - raw["date"]).dt.days
        guard_ok = gap <= (h * 1.7 + 7)
        guarded = panel_guarded[f"pred_ret_{h}"]
        rows.append({
            "horizon_d": h,
            "raw_n": int(fwd.notna().sum()), "guarded_n": int(guarded.notna().sum()),
            "nan_by_guard": int((fwd.notna() & ~guard_ok).sum()),
            "raw_max": float(fwd.max()), "guarded_max": float(guarded.max()),
            "raw_mean": float(fwd.mean()), "guarded_mean": float(guarded.mean()),
            "gap_days_p99": float(gap.quantile(0.99)), "gap_days_max": float(gap.max()),
            "threshold_days": h * 1.7 + 7,
        })
    pd.DataFrame(rows).to_csv(OUT / "artifact_fix_audit_table.csv", index=False, lineterminator="\n")
    print("[enh] A audit table written", flush=True)


def B_data_gated() -> None:
    rows = []
    fund = ["value_PBR", "value_PER", "quality_ROE", "quality_accruals", "shareholder_yield_buyback_div"]
    for s in fund:
        rows.append({"signal_id": f"sig_fund_{s}", "family": "DATA_GATED_fundamental", "status": "data_gated",
                     "reason": "no clean KR PIT fundamentals on disk; pykrx fundamental endpoint broken; DART body parser standby — NOT measured this sweep"})
    for s in ["borrow_fee", "short_rebate", "shortsale_restriction_list", "buy_in_events"]:
        rows.append({"signal_id": f"sig_{s}", "family": "DATA_GATED_borrow_residual", "status": "data_gated",
                     "reason": "W000 item6 residual: API gives borrow BALANCE only (no fee/rebate/restriction/buy-in) — NOT measured this sweep"})
    pd.DataFrame(rows).to_csv(OUT / "data_gated_rows.csv", index=False, lineterminator="\n")
    print(f"[enh] B {len(rows)} data_gated rows written", flush=True)


def C_fdr() -> None:
    # cross-section maps: p from IC t-stat (2-sided, df=n_dates-1); macro: from ts-corr; event: from abn t-stat
    for fn, tcol, ncol in [("influence_map_pass1.csv", "ic_tstat", "n_dates"),
                           ("influence_map_pass2a_sector_borrow.csv", "ic_tstat", "n_dates"),
                           ("influence_map_pass2c_events.csv", "abn_tstat", "n_events")]:
        p = OUT / fn
        if not p.exists():
            continue
        d = pd.read_csv(p)
        df_dof = pd.to_numeric(d[ncol], errors="coerce") - 1
        t = pd.to_numeric(d[tcol], errors="coerce")
        d["p_value"] = 2 * stats.t.sf(t.abs(), df_dof.clip(lower=1))
        d["q_value_bh"] = bh_qvalues(d["p_value"])
        d.to_csv(p, index=False, lineterminator="\n")
    # macro: ts-corr -> approx t = r*sqrt((n-2)/(1-r^2))
    p = OUT / "influence_map_pass2b_macro.csv"
    if p.exists():
        d = pd.read_csv(p)
        r = pd.to_numeric(d["ts_corr_pred"], errors="coerce"); n = pd.to_numeric(d["n_dates"], errors="coerce")
        t = r * np.sqrt((n - 2).clip(lower=1) / (1 - r.clip(-0.999, 0.999) ** 2))
        d["p_value"] = 2 * stats.t.sf(t.abs(), (n - 2).clip(lower=1))
        d["q_value_bh"] = bh_qvalues(d["p_value"])
        d.to_csv(p, index=False, lineterminator="\n")
    print("[enh] C FDR/q-values added to all maps", flush=True)


def D_liquidity_buckets(panel: pd.DataFrame) -> None:
    panel = panel.copy()
    g = panel.groupby("ticker", group_keys=False)
    panel["tv20"] = g["traded_value"].transform(lambda s: s.rolling(20, min_periods=10).mean())
    panel["liq_bucket"] = panel.groupby("date")["tv20"].transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=["low", "mid", "high"]) if s.notna().sum() >= 30 else np.nan)
    panel["cap_bucket"] = panel.groupby("date")["market_cap"].transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=["small", "mid", "large"]) if s.notna().sum() >= 30 else np.nan)
    sigs = ["sig_reversal_5", "sig_mom_5", "sig_mom_20", "sig_flow_foreign_amt_mcap", "sig_borrow_ratio", "sig_borrow_chg20"]
    sigs = [s for s in sigs if s in panel.columns]
    rows = []
    for sig in sigs:
        for bcol, bvals in [("liq_bucket", ["low", "mid", "high"]), ("cap_bucket", ["small", "mid", "large"])]:
            for bv in bvals:
                for regime in ("PAST", "PRESENT"):
                    sub = panel.loc[regime_mask(panel, regime) & (panel[bcol] == bv) & ~panel["tv_estimated"].fillna(False)]
                    ic = daily_ic(sub, sig, "pred_ret_5").dropna()
                    rows.append({"signal_id": sig, "bucket_dim": bcol, "bucket": bv, "regime": regime,
                                 "ic5_mean": float(ic.mean()) if len(ic) else np.nan, "n_dates": int(len(ic)),
                                 "status": "measured_with_caveat"})
    # 거래대금추정==True diagnostic slice (excluded from headline)
    for sig in sigs:
        for regime in ("PAST", "PRESENT"):
            sub = panel.loc[regime_mask(panel, regime) & panel["tv_estimated"].fillna(False)]
            ic = daily_ic(sub, sig, "pred_ret_5").dropna()
            rows.append({"signal_id": sig, "bucket_dim": "tv_estimated_slice", "bucket": "estimated_True", "regime": regime,
                         "ic5_mean": float(ic.mean()) if len(ic) else np.nan, "n_dates": int(len(ic)),
                         "status": "measured_with_caveat"})
    pd.DataFrame(rows).to_csv(OUT / "liquidity_bucket_breakdown.csv", index=False, lineterminator="\n")
    print(f"[enh] D liquidity buckets: {len(rows)} rows", flush=True)


def E_event_matched(panel: pd.DataFrame) -> None:
    # sector + cap bucket; matched control = mean fwd ret of same (date, sector, cap_bucket)
    panel = panel.copy()
    if "sector_code" not in panel.columns:  # build_sb may already have merged it in main()
        sec = pd.read_csv(SECTOR_PATH, usecols=["date", "ticker", "sector_code"], dtype={"ticker": str})
        sec["date"] = pd.to_datetime(sec["date"], errors="coerce"); sec["ticker"] = sec["ticker"].str.zfill(6)
        panel = panel.merge(sec, on=["date", "ticker"], how="left")
    panel["cap_bucket"] = panel.groupby("date")["market_cap"].transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=False) if s.notna().sum() >= 30 else np.nan)
    panel = panel.loc[~panel["tv_estimated"].fillna(False)].copy()
    for h in HORIZONS:
        grp = panel.groupby(["date", "sector_code", "cap_bucket"])[f"pred_ret_{h}"].transform("mean")
        panel[f"mabn_{h}"] = panel[f"pred_ret_{h}"] - grp  # matched abnormal
    panel["ticker"] = panel["ticker"].astype(str)
    px = panel[["date", "ticker"] + [f"mabn_{h}" for h in HORIZONS]].sort_values("date").reset_index(drop=True)
    ev = pd.read_parquet(DART, columns=["rcept_dt", "stock_code"] + FLAGS)
    ev["ticker"] = ev["stock_code"].astype(str).str.zfill(6)
    ev["rcept_dt"] = pd.to_datetime(ev["rcept_dt"].astype(str), format="%Y%m%d", errors="coerce")
    ev = ev.dropna(subset=["rcept_dt", "ticker"]).sort_values("rcept_dt").reset_index(drop=True)
    ev_e = pd.merge_asof(ev, px, left_on="rcept_dt", right_on="date", by="ticker",
                         direction="forward", allow_exact_matches=False).dropna(subset=["date"])
    rows = []
    for flag in FLAGS:
        sel = ev_e[ev_e[flag] == True]  # noqa: E712
        for regime in ("FULL", "PAST", "PRESENT"):
            s = sel[regime_mask(sel, regime)] if len(sel) else sel
            for h in HORIZONS:
                a = pd.to_numeric(s[f"mabn_{h}"], errors="coerce").dropna()
                n = len(a)
                rows.append({"signal_id": flag, "family": "G_event_matched", "horizon_d": h, "regime": regime,
                             "matched_abn_ret": float(a.mean()) if n else np.nan,
                             "matched_abn_tstat": float(a.mean() / (a.std() / np.sqrt(n))) if n > 2 and a.std() > 0 else np.nan,
                             "n_events": n,
                             "n_unique_ticker": int(s.loc[a.index, "ticker"].nunique()) if n else 0,
                             "n_unique_date": int(s.loc[a.index, "date"].nunique()) if n else 0,
                             "status": "measured_with_caveat",
                             "caveat": "matched control = same date x sector x cap-tercile; presence-level (title flag); overlapping events (see n_unique); R-family caveat"})
    pd.DataFrame(rows).to_csv(OUT / "influence_map_pass2c_events_matched.csv", index=False, lineterminator="\n")
    print(f"[enh] E event matched-control: {len(rows)} rows", flush=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("[enh] loading + building signals ...", flush=True)
    panel = add_forward_returns(load())
    build_signals(panel)            # adds pass-1 signal cols (reversal_5, mom_*, flow_*)
    _, panel = build_sb(panel)      # adds sector + borrow signal cols
    A_audit_table(panel)
    B_data_gated()
    D_liquidity_buckets(panel)
    E_event_matched(panel)
    C_fdr()                          # post-process the written maps
    print("[enh] DONE", flush=True)


if __name__ == "__main__":
    main()
