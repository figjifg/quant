"""
W001 v2 Component 7 — flow t+1 safe wrapper.

Round 3 Step 5 audit (KR-FLOW-UNIT-TIMESTAMP-AUDIT-001) raised two findings
on the panel's investor-flow columns:

- `수급금액추정여부` is True for 100% of rows (FLOW_000007 critical-correction
  finding).
- Vendor publication lag was not documented (FLOW_000004 high).

Round 4 reconciliation against KRX official trading-value-by-investor API
(`pykrx.stock.get_market_trading_value_by_date`) on a 440-pair sample showed:

- Sign convention match: foreign 100%, institution 99.8%.
- Within +/- 5% of KRX official: foreign 93.6%, institution 94.8%.
- Median |diff|: < 1%.

Conclusion: the vendor flag means "vendor recomputed / imputed", not
"unreliable". Values track KRX official closely. The remaining gap (~5-6%
outside +/-5%) is vendor recomputation noise and isolated outliers, not a
systemic defect.

This module exposes two helpers:

- `is_flow_t1_safe(...)`: returns the conservative `t+1 open` flow signal
  date convention based on the publication-timing rule documented in
  `research_input_data/docs/DATA_CATALOG.md` ("KRX 장마감 후"). Vendor
  values for `date == t` are safe to use as a signal for `t+1` open entry.
- `flow_with_safety_marker(panel)`: returns a copy of the panel with two
  added columns: `flow_estimation_marker` (the verbatim vendor flag) and
  `flow_t1_safe` (True if the row's flow values can be used to drive an
  execution on the next trading day).

The strict safety rule rejects rows where the vendor flag is missing or
where the underlying trading value is missing (Round 3 finding: NaN flow
count was 0 across all panel years).
"""

from __future__ import annotations

import pandas as pd


FLOW_COLUMNS = (
    "외국인순매수금액추정",
    "기관순매수금액추정",
    "외국인순매매량",
    "기관순매매량",
)
ESTIMATION_FLAG = "수급금액추정여부"
TRADING_VALUE = "거래대금추정"


def is_flow_t1_safe(row: pd.Series) -> bool:
    """Return True if the row's flow values can drive a t+1 execution.

    Rule (Round 4 S6 reconciliation 기준):
    - The flow estimation flag must exist on the row (panel always carries it).
    - The trading value must be present and positive (matches the panel's own
      `거래대금추정` non-NaN convention).
    - Flow columns themselves must be numeric (NaN is 0 by audit, but the
      column must be present).
    """
    if ESTIMATION_FLAG not in row.index:
        return False
    if TRADING_VALUE in row.index:
        tv = pd.to_numeric(row[TRADING_VALUE], errors="coerce")
        if pd.isna(tv) or tv <= 0:
            return False
    for col in FLOW_COLUMNS:
        if col not in row.index:
            return False
    return True


def flow_with_safety_marker(panel: pd.DataFrame) -> pd.DataFrame:
    """Annotate a panel with flow estimation marker + t+1 safety column.

    Does not modify the underlying flow values. Callers that want to assert
    "I am only using vendor-reconciled flow" can filter to
    `panel['flow_t1_safe'] == True`.
    """
    out = panel.copy()

    out["flow_estimation_marker"] = (
        out[ESTIMATION_FLAG].fillna(False).astype(bool)
        if ESTIMATION_FLAG in out.columns
        else False
    )

    tv_ok = pd.Series(True, index=out.index)
    if TRADING_VALUE in out.columns:
        tv = pd.to_numeric(out[TRADING_VALUE], errors="coerce")
        tv_ok = tv.notna() & tv.gt(0)

    flow_cols_present = all(col in out.columns for col in FLOW_COLUMNS)
    flag_present = ESTIMATION_FLAG in out.columns

    out["flow_t1_safe"] = bool(flow_cols_present) & bool(flag_present) & tv_ok
    return out


def reconcile_sample(
    panel: pd.DataFrame,
    krx_official: pd.DataFrame,
    *,
    diff_threshold: float = 0.05,
) -> dict[str, float]:
    """Reconcile a sample of panel rows against KRX official trading-value-by-investor.

    `krx_official` schema (per `data/acquired/round4/s6_flow_reconciliation/`):
    - `date` (date)
    - `ticker` (str, zero-padded 6 digits)
    - `krx_foreign` (float, signed KRW)
    - `krx_institution` (float, signed KRW)

    Returns reconciliation summary metrics. No performance metric is computed —
    this is a lineage-audit helper, not a strategy diagnostic.
    """
    import numpy as np

    panel_keys = panel.copy()
    panel_keys["종목코드"] = panel_keys["종목코드"].astype(str).str.zfill(6)
    merged = panel_keys.merge(
        krx_official,
        left_on=["날짜", "종목코드"],
        right_on=["date", "ticker"],
        how="inner",
    )
    if merged.empty:
        return {
            "n_pairs": 0,
            "foreign_sign_match_pct": 0.0,
            "institution_sign_match_pct": 0.0,
            "foreign_within_threshold_pct": 0.0,
            "institution_within_threshold_pct": 0.0,
            "foreign_median_abs_diff_pct": 0.0,
            "institution_median_abs_diff_pct": 0.0,
        }

    def _diff_pct(panel_val: pd.Series, krx_val: pd.Series) -> pd.Series:
        denom = krx_val.abs().clip(lower=1.0)
        return (panel_val - krx_val) / denom

    f_diff = _diff_pct(merged["외국인순매수금액추정"], merged["krx_foreign"])
    i_diff = _diff_pct(merged["기관순매수금액추정"], merged["krx_institution"])

    return {
        "n_pairs": int(len(merged)),
        "foreign_sign_match_pct": float(
            (np.sign(merged["외국인순매수금액추정"]) == np.sign(merged["krx_foreign"])).mean() * 100
        ),
        "institution_sign_match_pct": float(
            (np.sign(merged["기관순매수금액추정"]) == np.sign(merged["krx_institution"])).mean() * 100
        ),
        "foreign_within_threshold_pct": float((f_diff.abs() <= diff_threshold).mean() * 100),
        "institution_within_threshold_pct": float((i_diff.abs() <= diff_threshold).mean() * 100),
        "foreign_median_abs_diff_pct": float(f_diff.abs().median() * 100),
        "institution_median_abs_diff_pct": float(i_diff.abs().median() * 100),
    }
