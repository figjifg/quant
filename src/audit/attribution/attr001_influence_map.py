"""ATTR001 — Korean equity data influence map (diagnostic attribution sweep).

Pre-registration: research/experiments/ATTR001_korean_data_influence_map.md (locked;
Referee-signed-off 2026-05-28). Diagnostic-only. PRESERVE-ALL (no discard of bad/negative/
null results). Audit-first validity (PIT, T+1 execution, after-tax+cost, placebo, regime
split, FDR-aware). NOT a strategy search; output = an influence map. KR long-short =
statistical spread only (short not executable).

Pass 1 (this module): cross-section families A (flow), B (price/volume), D (total-return).
Families C (sector), E (borrow), F (market/macro conditional), G (event-study) follow in
later passes (same locked pre-registration; preserve-all). Output rows carry a status label.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))
from src.data.sector_aggregator import _read_panel, DEFAULT_CONFIG  # noqa: E402
import yaml  # noqa: E402

OUT = REPO / "reports/experiments/ATTR001_korean_data_influence_map"
TR_PATH = REPO / "data/acquired/w000_korean_total_return/kr_total_return_prices_2018_2026.csv"

HORIZONS = [1, 3, 5, 10, 20]
PRESENT_START = pd.Timestamp("2022-01-03")
PAST_START = pd.Timestamp("2018-01-02")
PAST_END = pd.Timestamp("2021-12-30")
# cost model (bps): commission/leg + tax on sell + slippage/leg  -> round-trip long-only
COST_RT_LONG_BPS = 1.5 + 5 + 1.5 + 5 + 20  # buy(comm+slip) + sell(comm+slip) + tax(sell)
RNG = np.random.default_rng(20260528)


def load() -> pd.DataFrame:
    cfg = yaml.safe_load(Path(DEFAULT_CONFIG).read_text(encoding="utf-8"))
    frames = []
    for rel in cfg["panels"]:
        p = REPO / rel
        if not p.exists():
            continue
        # _read_panel gives canonical fields + OHLCV quarantine + in_universe
        f = _read_panel(p)
        # also pull raw price/volume/shares + estimate flags for signal construction
        raw = pd.read_csv(p, encoding="utf-8-sig", dtype={"종목코드": "string"})
        raw["date"] = pd.to_datetime(raw["날짜"], errors="coerce")
        raw["ticker"] = raw["종목코드"].astype("string").str.zfill(6)
        keep = {"종가": "close", "시가": "open", "거래량": "volume",
                "상장주식수": "shares_out", "거래대금추정여부": "tv_estimated"}
        rawk = raw[["date", "ticker"] + list(keep)].rename(columns=keep)
        f = f.merge(rawk, on=["date", "ticker"], how="left")
        frames.append(f)
    panel = pd.concat(frames, ignore_index=True)
    panel = panel.loc[panel["in_universe"]].drop_duplicates(["date", "ticker"], keep="last")
    panel = panel.sort_values(["ticker", "date"]).reset_index(drop=True)
    for c in ["close", "open", "volume", "shares_out"]:
        panel[c] = pd.to_numeric(panel[c], errors="coerce")
    panel["tv_estimated"] = panel["tv_estimated"].astype("string").str.upper().isin(["TRUE", "1", "1.0", "Y"])
    # total-return adj_close (W000 item2, yfinance proxy)
    tr = pd.read_csv(TR_PATH, dtype={"ticker": str}, low_memory=False)
    tr["date"] = pd.to_datetime(tr["date"], errors="coerce")
    tr["ticker"] = tr["ticker"].str.zfill(6)
    panel = panel.merge(tr[["date", "ticker", "adj_close"]], on=["date", "ticker"], how="left")
    return panel


def add_forward_returns(panel: pd.DataFrame) -> pd.DataFrame:
    """PIT forward returns per ticker. prediction = close->close over h (info >T).
    executability = enter T+1 open -> exit close at T+h, minus round-trip cost.

    GAP GUARD (fixes dynamic-universe re-entry artifact): the panel is in_universe-filtered,
    so a ticker can leave and re-enter top100 → shift(-h) would connect across a multi-month
    hole and (because re-entry is conditional on the stock rising) inject a huge survivorship
    -positive forward return. We NaN any forward return whose T→T+h window spans more calendar
    days than ~h trading days plausibly allow (h*1.7 + 7), so only genuinely consecutive
    in-universe windows count."""
    panel = panel.sort_values(["ticker", "date"]).reset_index(drop=True)
    g = panel.groupby("ticker", group_keys=False)
    panel["_close"] = panel["close"]
    for h in HORIZONS:
        fwd_close = g["close"].shift(-h)
        fwd_date = g["date"].shift(-h)
        gap_days = (fwd_date - panel["date"]).dt.days
        gap_ok = gap_days <= (h * 1.7 + 7)  # consecutive in-universe window only
        pred = fwd_close / panel["close"] - 1.0
        panel[f"pred_ret_{h}"] = pred.where(gap_ok)
        nxt_open = g["open"].shift(-1)
        exit_close = g["close"].shift(-h)  # exit at close of T+h (h>=1 → after T+1 open)
        gross = exit_close / nxt_open - 1.0
        panel[f"exec_ret_{h}"] = (gross - COST_RT_LONG_BPS / 1e4).where(gap_ok)
    return panel


def build_signals(panel: pd.DataFrame) -> dict[str, tuple[str, str]]:
    """Define PIT cross-section signals (value at date T uses info <= T). Returns
    {signal_id: (family, caveat)}; writes signal columns into panel in place."""
    g = panel.groupby("ticker", group_keys=False)
    defs: dict[str, tuple[str, str]] = {}

    # ---- Family A: flow (EOD -> t+1, PIT) ----
    panel["sig_flow_foreign_amt_tv"] = panel["foreign_net_buy_amount"] / panel["traded_value"].replace(0, np.nan)
    panel["sig_flow_inst_amt_tv"] = panel["institution_net_buy_amount"] / panel["traded_value"].replace(0, np.nan)
    panel["sig_flow_foreign_amt_mcap"] = panel["foreign_net_buy_amount"] / panel["market_cap"].replace(0, np.nan)
    panel["sig_flow_fi_divergence"] = (panel["foreign_net_buy_amount"] - panel["institution_net_buy_amount"]) / panel["traded_value"].replace(0, np.nan)
    for w in (3, 5, 20):
        panel[f"sig_flow_foreign_amt_cum{w}"] = g["foreign_net_buy_amount"].transform(lambda s: s.rolling(w, min_periods=w).sum()) / panel["market_cap"].replace(0, np.nan)
    for s in ["sig_flow_foreign_amt_tv", "sig_flow_inst_amt_tv", "sig_flow_foreign_amt_mcap",
              "sig_flow_fi_divergence", "sig_flow_foreign_amt_cum3", "sig_flow_foreign_amt_cum5", "sig_flow_foreign_amt_cum20"]:
        defs[s] = ("A_flow", "vendor-estimated flow (수급금액추정여부 all-True)")

    # ---- Family B: price / volume (PIT) ----
    for w in (1, 3, 5, 10, 20, 60):
        panel[f"sig_mom_{w}"] = g["close"].transform(lambda s: s / s.shift(w) - 1.0)
        defs[f"sig_mom_{w}"] = ("B_price", "")
    panel["sig_reversal_5"] = -panel["sig_mom_5"]
    defs["sig_reversal_5"] = ("B_price", "negation of 5d momentum")
    panel["sig_vol_20"] = g["daily_return"].transform(lambda s: s.rolling(20, min_periods=20).std())
    defs["sig_vol_20"] = ("B_price", "")
    panel["sig_turnover_chg5"] = g["traded_value"].transform(lambda s: s / s.rolling(5, min_periods=5).mean().shift(1) - 1.0)
    defs["sig_turnover_chg5"] = ("B_price", "")
    panel["sig_vol_surge"] = g["volume"].transform(lambda s: s / s.rolling(20, min_periods=20).mean().shift(1) - 1.0)
    defs["sig_vol_surge"] = ("B_price", "")
    panel["sig_gap"] = panel["open"] / g["close"].shift(1) - 1.0
    defs["sig_gap"] = ("B_price", "")
    panel["sig_intraday"] = panel["close"] / panel["open"] - 1.0
    defs["sig_intraday"] = ("B_price", "")

    # ---- Family D: total return (W000 item2 proxy) ----
    for w in (20, 60):
        panel[f"sig_tr_mom_{w}"] = g["adj_close"].transform(lambda s: s / s.shift(w) - 1.0)
        defs[f"sig_tr_mom_{w}"] = ("D_totalreturn", "yfinance TR proxy; adj_close used for RETURN only")
    return defs


def _spearman(a: pd.Series, b: pd.Series) -> float:
    m = a.notna() & b.notna()
    if m.sum() < 20:
        return np.nan
    return a[m].rank().corr(b[m].rank())


def daily_ic(panel: pd.DataFrame, sig: str, ret: str) -> pd.Series:
    return panel.groupby("date").apply(lambda df: _spearman(df[sig], df[ret]))


def decile_spread(panel: pd.DataFrame, sig: str, ret: str) -> tuple[float, float]:
    """Mean per-date (Q10-Q1) long-short [statistical] and long-only top-decile excess."""
    ls, lo = [], []
    for _, df in panel.groupby("date"):
        d = df[[sig, ret]].dropna()
        if len(d) < 30:
            continue
        q = pd.qcut(d[sig].rank(method="first"), 10, labels=False, duplicates="drop")
        if q.nunique() < 10:
            continue
        top = d[ret][q == 9].mean(); bot = d[ret][q == 0].mean(); uni = d[ret].mean()
        ls.append(top - bot); lo.append(top - uni)
    return (float(np.mean(ls)) if ls else np.nan, float(np.mean(lo)) if lo else np.nan)


def regime_mask(panel: pd.DataFrame, regime: str) -> pd.Series:
    if regime == "PAST":
        return (panel["date"] >= PAST_START) & (panel["date"] <= PAST_END)
    if regime == "PRESENT":
        return panel["date"] >= PRESENT_START
    return panel["date"] >= PAST_START  # FULL


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("[ATTR001] loading panel + total-return ...", flush=True)
    panel = load()
    panel = add_forward_returns(panel)
    defs = build_signals(panel)
    # headline excludes 거래대금추정여부==True rows (kept as diagnostic slice separately)
    headline = panel.loc[~panel["tv_estimated"].fillna(False)].copy()
    print(f"[ATTR001] {len(defs)} signals; panel rows={len(panel):,} headline={len(headline):,} "
          f"dates {panel['date'].min().date()}..{panel['date'].max().date()}", flush=True)

    rows = []
    for sig, (family, caveat) in defs.items():
        for regime in ("FULL", "PAST", "PRESENT"):
            sub = headline.loc[regime_mask(headline, regime)]
            for h in HORIZONS:
                ic = daily_ic(sub, sig, f"pred_ret_{h}").dropna()
                ic_mean = float(ic.mean()) if len(ic) else np.nan
                ic_t = float(ic.mean() / (ic.std() / np.sqrt(len(ic)))) if len(ic) > 2 and ic.std() > 0 else np.nan
                ic_hit = float((ic > 0).mean()) if len(ic) else np.nan
                ls, lo = decile_spread(sub, sig, f"exec_ret_{h}")  # executability (net cost)
                # placebo: within-date ticker permutation of the signal, IC on 5d only (primary)
                placebo_ic = np.nan
                if h == 5 and len(sub):
                    perm = sub.copy()
                    perm[sig] = perm.groupby("date")[sig].transform(lambda s: pd.Series(RNG.permutation(s.values), index=s.index))
                    pic = daily_ic(perm, sig, "pred_ret_5").dropna()
                    placebo_ic = float(pic.mean()) if len(pic) else np.nan
                rows.append({
                    "signal_id": sig, "family": family, "horizon_d": h, "regime": regime,
                    "ic_mean_pred": ic_mean, "ic_tstat": ic_t, "ic_hit_rate": ic_hit, "n_dates": int(len(ic)),
                    "decile_ls_exec_netcost": ls, "longonly_topdecile_exec_netcost": lo,
                    "placebo_ic_5d": placebo_ic if h == 5 else "",
                    "status": "measured_with_caveat" if caveat else "measured_valid",
                    "execution_note": "long-only is executable view; long-short = statistical only (KR short not executable)",
                    "caveat": caveat, "label_note": "ic=close-to-close prediction; decile=T+1-open executability net cost",
                })
        print(f"[ATTR001] done signal {sig}", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "influence_map_pass1.csv", index=False, lineterminator="\n")
    # influence-map ranking view (NOT a recommendation): by |PRESENT 5d IC|
    rank = df[(df["regime"] == "PRESENT") & (df["horizon_d"] == 5)].copy()
    rank["abs_ic"] = rank["ic_mean_pred"].abs()
    rank = rank.sort_values("abs_ic", ascending=False)
    rank.to_csv(OUT / "influence_map_ranking_present_5d.csv", index=False, lineterminator="\n")
    print(f"[ATTR001] wrote {len(df)} rows -> influence_map_pass1.csv", flush=True)


if __name__ == "__main__":
    main()
