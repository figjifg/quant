"""P1 KR-OHLCV-UNIT-INVARIANT-A0-001 build script.

Produces 6 artifacts in reports/experiments/measurement_A0/KR_OHLCV_UNIT_INVARIANT_A0/.

Measurement-layer A0 ONLY. No return / jump / momentum / reversal / performance outcome.
Trading_value / close / volume checks MUST NOT be converted into liquidity / turnover /
alpha signals.

Required outputs:
  1. ohlcv_invariant_summary.md
  2. ohlc_ordering_violations.csv
  3. nonpositive_price_rows.csv
  4. negative_volume_value_rows.csv
  5. trading_value_unit_plausibility.md
  6. invalid_row_quarantine_rules.md
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/home/jin/code/quant")
OUT = REPO / "reports/experiments/measurement_A0/KR_OHLCV_UNIT_INVARIANT_A0"
OUT.mkdir(parents=True, exist_ok=True)

PANEL_PATHS = [
    ("kiwoom_2010_2016", REPO / "research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv"),
    ("dynamic_top100_2017_2024", REPO / "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv"),
    ("dynamic_top100_2018_2024", REPO / "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv"),
    ("krx_2025_2026", REPO / "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"),
]
S1_PATH = REPO / "data/acquired/round4/s1_adjusted_ohlc/adjusted_ohlc_all_tickers_2018_2026.csv"
W001_V2_ADJUSTED = REPO / "data/processed/w001_v2/panel_with_adjusted_ohlc_2018_2026.csv"


PANEL_PRICE_COLS = ["시가", "고가", "저가", "종가"]
PANEL_VOLUME_COL = "거래량"
PANEL_VALUE_COL = "거래대금추정"
PANEL_VALUE_FLAG = "거래대금추정여부"
PANEL_DATE = "날짜"
PANEL_TICKER = "종목코드"


def detect_panel_violations(tag: str, path: Path) -> dict:
    df = pd.read_csv(
        path,
        usecols=[PANEL_DATE, PANEL_TICKER, *PANEL_PRICE_COLS, PANEL_VOLUME_COL, PANEL_VALUE_COL, PANEL_VALUE_FLAG],
        dtype={PANEL_TICKER: str},
        encoding="utf-8-sig",
    )
    n_total = len(df)

    o = df["시가"].astype("float64")
    h = df["고가"].astype("float64")
    l = df["저가"].astype("float64")
    c = df["종가"].astype("float64")
    v = df[PANEL_VOLUME_COL].astype("float64")
    tv = df[PANEL_VALUE_COL].astype("float64")

    # OHLC ordering
    rule_high_lt_low = h < l
    rule_high_lt_open = h < o
    rule_high_lt_close = h < c
    rule_low_gt_open = l > o
    rule_low_gt_close = l > c
    any_ohlc = rule_high_lt_low | rule_high_lt_open | rule_high_lt_close | rule_low_gt_open | rule_low_gt_close

    # Non-positive prices
    rule_nonpos_o = o <= 0
    rule_nonpos_h = h <= 0
    rule_nonpos_l = l <= 0
    rule_nonpos_c = c <= 0
    any_nonpos = rule_nonpos_o | rule_nonpos_h | rule_nonpos_l | rule_nonpos_c

    # Negative volume / value
    rule_neg_vol = v < 0
    rule_neg_tv = tv < 0
    any_neg_vol = rule_neg_vol | rule_neg_tv

    # Slice out violator rows
    ohlc_violations = df[any_ohlc].copy()
    ohlc_violations["panel"] = tag
    ohlc_violations["violation_codes"] = (
        rule_high_lt_low[any_ohlc].astype(int).astype(str).radd("high_lt_low=")
        + "|" + rule_high_lt_open[any_ohlc].astype(int).astype(str).radd("high_lt_open=")
        + "|" + rule_high_lt_close[any_ohlc].astype(int).astype(str).radd("high_lt_close=")
        + "|" + rule_low_gt_open[any_ohlc].astype(int).astype(str).radd("low_gt_open=")
        + "|" + rule_low_gt_close[any_ohlc].astype(int).astype(str).radd("low_gt_close=")
    )

    nonpos_rows = df[any_nonpos].copy()
    nonpos_rows["panel"] = tag
    nonpos_rows["nonpos_codes"] = (
        rule_nonpos_o[any_nonpos].astype(int).astype(str).radd("open_le_0=")
        + "|" + rule_nonpos_h[any_nonpos].astype(int).astype(str).radd("high_le_0=")
        + "|" + rule_nonpos_l[any_nonpos].astype(int).astype(str).radd("low_le_0=")
        + "|" + rule_nonpos_c[any_nonpos].astype(int).astype(str).radd("close_le_0=")
    )

    neg_rows = df[any_neg_vol].copy()
    neg_rows["panel"] = tag
    neg_rows["neg_codes"] = (
        rule_neg_vol[any_neg_vol].astype(int).astype(str).radd("volume_lt_0=")
        + "|" + rule_neg_tv[any_neg_vol].astype(int).astype(str).radd("traded_value_lt_0=")
    )

    # Trading value plausibility: when 거래대금추정여부 True, compare to close*volume
    # estimated_tv == close * volume by construction in these panels (sanity check)
    tv_est_flag = df[PANEL_VALUE_FLAG].astype("string").str.strip().eq("True")
    est_rows = df[tv_est_flag].copy()
    est_rows["close_x_volume"] = (c[tv_est_flag] * v[tv_est_flag]).astype("float64")
    est_rows["traded_value_minus_close_x_volume"] = est_rows[PANEL_VALUE_COL].astype("float64") - est_rows["close_x_volume"]
    est_rows["abs_rel_diff"] = (est_rows["traded_value_minus_close_x_volume"].abs()
                                 / est_rows["close_x_volume"].replace(0, np.nan).abs())
    mismatch_rows_n = int((est_rows["abs_rel_diff"].fillna(0) > 1e-6).sum())

    return {
        "tag": tag,
        "n_total": n_total,
        "ohlc_violations": ohlc_violations,
        "nonpos_rows": nonpos_rows,
        "neg_rows": neg_rows,
        "tv_estimated_rows": int(tv_est_flag.sum()),
        "tv_estimated_mismatches": mismatch_rows_n,
    }


def detect_s1_violations() -> dict:
    df = pd.read_csv(S1_PATH, dtype={"종목코드": str}, encoding="utf-8-sig")
    n_total = len(df)
    o = df["adj_open"].astype("float64")
    h = df["adj_high"].astype("float64")
    l = df["adj_low"].astype("float64")
    c = df["adj_close"].astype("float64")
    v = df["adj_volume"].astype("float64")

    rule_high_lt_low = h < l
    rule_high_lt_open = h < o
    rule_high_lt_close = h < c
    rule_low_gt_open = l > o
    rule_low_gt_close = l > c
    any_ohlc = rule_high_lt_low | rule_high_lt_open | rule_high_lt_close | rule_low_gt_open | rule_low_gt_close

    rule_nonpos = (o <= 0) | (h <= 0) | (l <= 0) | (c <= 0)
    rule_neg_vol = v < 0

    ohlc_violations = df[any_ohlc].copy()
    ohlc_violations["panel"] = "s1_adjusted_ohlc"
    nonpos_rows = df[rule_nonpos].copy()
    nonpos_rows["panel"] = "s1_adjusted_ohlc"
    neg_rows = df[rule_neg_vol].copy()
    neg_rows["panel"] = "s1_adjusted_ohlc"

    return {
        "tag": "s1_adjusted_ohlc",
        "n_total": n_total,
        "ohlc_violations": ohlc_violations,
        "nonpos_rows": nonpos_rows,
        "neg_rows": neg_rows,
    }


def write_combined_csv(out_path: Path, frames: list[pd.DataFrame], columns: list[str]) -> int:
    # Dedupe target column list (PANEL_TICKER == "종목코드" appears twice across panel & S1 lists)
    seen, dedup_cols = set(), []
    for c in columns:
        if c not in seen:
            dedup_cols.append(c)
            seen.add(c)
    rows = []
    for fr in frames:
        if len(fr) == 0:
            continue
        keep = [c for c in dedup_cols if c in fr.columns]
        sub = fr.loc[:, keep].copy()
        rows.append(sub)
    if not rows:
        pd.DataFrame(columns=dedup_cols).to_csv(out_path, index=False, encoding="utf-8")
        return 0
    out = pd.concat(rows, ignore_index=True, sort=False)
    out.to_csv(out_path, index=False, encoding="utf-8")
    return len(out)


def trading_value_unit_plausibility(results: list[dict]) -> str:
    lines = [
        "# Trading Value Unit Plausibility",
        "",
        "Date: 2026-05-23  ",
        "Scope: measurement-layer A0 only. No turnover / liquidity / alpha derivation.",
        "",
        "## Method",
        "",
        "When `거래대금추정여부 == True`, the vendor estimation rule is `거래대금추정 = 종가 × 거래량`.",
        "For each panel we compare `거래대금추정` to `close × volume` on the estimated subset and",
        "count mismatches above relative tolerance `1e-6`.",
        "",
        "## Panel-level results",
        "",
        "| panel | rows_total | rows_estimated | mismatch_count | mismatch_pct_of_estimated |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in results:
        if "tv_estimated_rows" not in r:
            continue
        total = r["n_total"]
        est = r["tv_estimated_rows"]
        mis = r["tv_estimated_mismatches"]
        pct = round(100.0 * mis / max(1, est), 4)
        lines.append(f"| `{r['tag']}` | {total} | {est} | {mis} | {pct}% |")
    lines += [
        "",
        "## Aggregate flow unit plausibility (market_flow files)",
        "",
        "`kospi_foreign_net`, `kospi_institution_net`, `kospi_individual_net` carry the column",
        "unit `KRW_mil_or_count` per `KR_FIELD_METADATA_CONTRACT_A0/column_contract_table.csv`.",
        "",
        "Plausibility heuristic — KOSPI total daily trading is on the order of ~10^13 KRW",
        "(~10 trillion KRW = 10 million 백만원). Observed magnitudes of `kospi_foreign_net`",
        "in panel files range in the low thousands per day. This is consistent with **count**",
        "(unit = number of net contracts / shares) or **억원** (10^8 KRW), but **not** with **백만원**",
        "as the column name pattern `_mil` might suggest.",
        "",
        "Conclusion: unit string `KRW_mil_or_count` is ambiguous; this defect is recorded in",
        "`KR_FIELD_METADATA_CONTRACT_A0/undocumented_field_defect_ledger.csv` as `unit_ambiguous`.",
        "Until resolved, downstream usage of those columns is **ALLOW_WITH_GUARD**: any code that",
        "treats them as KRW must annotate the conversion factor at the call site.",
        "",
        "## Hard locks",
        "",
        "- These checks must NOT be converted into liquidity / turnover / alpha signals.",
        "- These checks must NOT be used to grade a stock as tradable.",
        "- No phase-allowed output here recommends strategy reopen.",
        "",
    ]
    return "\n".join(lines)


def quarantine_rules() -> str:
    return "\n".join([
        "# Invalid-Row Quarantine Rules",
        "",
        "Date: 2026-05-23  ",
        "Scope: measurement-layer A0. Strict rules; no return / signal derivation downstream.",
        "",
        "## Rule set",
        "",
        "Any row that triggers ANY of the following becomes a **quarantined row**. Strategy",
        "code MUST exclude quarantined rows from feature construction, universe selection, and",
        "execution. Audit code may still observe them.",
        "",
        "1. OHLC ordering violation: `고가 < 저가` OR `고가 < {시가,종가}` OR `저가 > {시가,종가}`.",
        "2. Non-positive price: any of `시가/고가/저가/종가 <= 0`.",
        "3. Negative volume: `거래량 < 0`.",
        "4. Negative trading value: `거래대금추정 < 0`.",
        "5. Trading-value-estimated mismatch beyond tolerance `1e-6` relative diff when",
        "   `거래대금추정여부 == True`.",
        "6. (Adjusted overlay only) `adj_close <= 0` OR `adj_volume < 0`.",
        "",
        "## Mandatory annotations at quarantine time",
        "",
        "- `quarantine_reason_code`: one of `ohlc_order`, `nonpos_price`, `neg_volume`,",
        "  `neg_traded_value`, `tv_estimated_mismatch`, `adj_invalid`.",
        "- `quarantine_source_csv`: filename of input that produced the row.",
        "- `quarantine_timestamp`: ISO datetime at quarantine run.",
        "",
        "## Strategy-impact rule",
        "",
        "If any strategy code, sector aggregator, factor builder, ranking script, or execution",
        "simulator includes a quarantined row without an explicit `quarantine_override` annotation",
        "documented at the call site, the audit FAILS.",
        "",
        "## Hard locks",
        "",
        "- Quarantine rules MUST NOT be relaxed to recover sample size.",
        "- Quarantine rules MUST NOT be replaced by per-row 'winsorisation' that hides defects.",
        "- Quarantine rules MUST NOT be used as a feature.",
        "",
    ])


def main() -> None:
    results = []
    for tag, p in PANEL_PATHS:
        results.append(detect_panel_violations(tag, p))
    results.append(detect_s1_violations())

    n_ohlc = write_combined_csv(
        OUT / "ohlc_ordering_violations.csv",
        [r["ohlc_violations"] for r in results],
        columns=["panel", PANEL_DATE, PANEL_TICKER, "종목명", *PANEL_PRICE_COLS, "violation_codes",
                 "date", "종목코드", "adj_open", "adj_high", "adj_low", "adj_close"],
    )
    n_nonpos = write_combined_csv(
        OUT / "nonpositive_price_rows.csv",
        [r["nonpos_rows"] for r in results],
        columns=["panel", PANEL_DATE, PANEL_TICKER, "종목명", *PANEL_PRICE_COLS, "nonpos_codes",
                 "date", "종목코드", "adj_open", "adj_high", "adj_low", "adj_close"],
    )
    n_neg = write_combined_csv(
        OUT / "negative_volume_value_rows.csv",
        [r["neg_rows"] for r in results],
        columns=["panel", PANEL_DATE, PANEL_TICKER, "종목명", PANEL_VOLUME_COL, PANEL_VALUE_COL, "neg_codes",
                 "date", "종목코드", "adj_volume"],
    )

    (OUT / "trading_value_unit_plausibility.md").write_text(trading_value_unit_plausibility(results), encoding="utf-8")
    (OUT / "invalid_row_quarantine_rules.md").write_text(quarantine_rules(), encoding="utf-8")

    # Summary
    total_rows = sum(r["n_total"] for r in results)
    summary_lines = [
        "# OHLCV Unit Invariant Audit — Summary",
        "",
        "Date: 2026-05-23  ",
        "Scope: measurement-layer A0 only. NO return / jump / momentum / reversal / performance.",
        "",
        "## Headline numbers",
        "",
        f"- Total rows scanned across panels + S1: {total_rows}",
        f"- OHLC ordering violations: {n_ohlc}",
        f"- Non-positive price rows: {n_nonpos}",
        f"- Negative volume/value rows: {n_neg}",
        "",
        "## Per-source breakdown",
        "",
        "| source | rows_total | ohlc_violations | nonpos_rows | neg_rows |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in results:
        summary_lines.append(
            f"| `{r['tag']}` | {r['n_total']} | {len(r['ohlc_violations'])} | {len(r['nonpos_rows'])} | {len(r['neg_rows'])} |"
        )

    summary_lines += [
        "",
        "## Pattern finding — `OHL == 0` while `close > 0`",
        "",
        "Across **all** panels and S1 adjusted, the non-positive rows share one signature:",
        "`시가 = 고가 = 저가 = 0` (or `adj_open = adj_high = adj_low = 0`) with `종가 > 0`",
        "(or `adj_close > 0`). This is the vendor convention for **non-trading rows**",
        "(halts / suspensions / period-bookend rows) where intraday data is absent but the",
        "previous close is forwarded. These rows trigger BOTH the OHLC-ordering rule",
        "(`고가 < 종가` because `고가 == 0`) AND the non-positive-price rule.",
        "",
        "Implication:",
        "- The two violation counts coincide for the equity panels because they describe the",
        "  same row set.",
        "- These rows MUST be quarantined per the rules in `invalid_row_quarantine_rules.md`.",
        "- They MUST NOT be used as evidence of a price level on that day.",
        "- Cross-check with `KR-EXECUTABLE-STATUS-BACKLOG-001` and W001 v2 listing_status_events",
        "  is required before treating any of them as a suspension event.",
        "",
        "## Trading value estimation (vendor `거래대금추정`)",
        "",
        "| panel | rows_estimated | mismatch_count |",
        "|---|---:|---:|",
    ]
    for r in results:
        if "tv_estimated_rows" not in r:
            continue
        summary_lines.append(f"| `{r['tag']}` | {r['tv_estimated_rows']} | {r['tv_estimated_mismatches']} |")

    summary_lines += [
        "",
        "## Kill gates (Referee)",
        "",
        "- **OHLC ordering broad?** Look at counts above; broad = quarantine affected rows/fields.",
        "- **Price/value unit clear?** See `trading_value_unit_plausibility.md` — close×volume agreement on estimated rows is the plausibility evidence. Aggregate market_flow flow unit (KRW_mil vs count) is ambiguous → defect logged.",
        "- **Quarantined rows ever used downstream?** Strategy code uses `tradable_state` and adjusted overlay; the v2 wiring is responsible for excluding quarantined rows. This audit produces the canonical quarantine row list. Downstream verification = separate audit.",
        "",
        "## Allowed output enumeration (per Referee)",
        "",
        "- defect ledger ✔ (CSV form)",
        "- invariant defect tables ✔",
        "- quarantine rule doc ✔",
        "- unit plausibility doc ✔",
        "",
        "## Disallowed output (Referee-lock)",
        "",
        "- No turnover, liquidity, or volume-based ranking.",
        "- No close-on-close return.",
        "- No reversion / momentum / RS / quality metric.",
        "- No execution simulation.",
        "",
        "## Cross references",
        "",
        "- `ohlc_ordering_violations.csv`",
        "- `nonpositive_price_rows.csv`",
        "- `negative_volume_value_rows.csv`",
        "- `trading_value_unit_plausibility.md`",
        "- `invalid_row_quarantine_rules.md`",
        "- `../KR_FIELD_METADATA_CONTRACT_A0/`",
        "- `../KR_CALENDAR_PANEL_ALIGN_A0/`",
        "",
    ]
    (OUT / "ohlcv_invariant_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")

    print(json.dumps({
        "total_rows_scanned": total_rows,
        "ohlc_violations": n_ohlc,
        "nonpos_rows": n_nonpos,
        "neg_rows": n_neg,
        "per_source": [
            {"tag": r["tag"], "n_total": r["n_total"],
             "ohlc": len(r["ohlc_violations"]), "nonpos": len(r["nonpos_rows"]),
             "neg": len(r["neg_rows"]),
             "tv_estimated_rows": r.get("tv_estimated_rows", "n/a"),
             "tv_estimated_mismatches": r.get("tv_estimated_mismatches", "n/a")}
            for r in results
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
