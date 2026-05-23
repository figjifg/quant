"""P0-2 KR-CALENDAR-PANEL-ALIGN-A0-001 build script.

Produces 6 artifacts in reports/experiments/measurement_A0/KR_CALENDAR_PANEL_ALIGN_A0/.

Measurement-layer A0 only. No strategy testing. No return / NAV / Sharpe.

Required outputs:
  1. calendar_panel_alignment_summary.md
  2. krx_calendar_source_check.md
  3. off_calendar_rows.csv
  4. missing_calendar_panel_days.csv
  5. duplicate_stock_date_rows.csv
  6. t_plus_1_mapping_reproducibility.md
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
OUT = REPO / "reports/experiments/measurement_A0/KR_CALENDAR_PANEL_ALIGN_A0"
OUT.mkdir(parents=True, exist_ok=True)

PANEL_PATHS = {
    "kiwoom_2010_2016": REPO / "research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv",
    "dynamic_top100_2017_2024": REPO / "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv",
    "dynamic_top100_2018_2024": REPO / "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv",
    "krx_2025_2026": REPO / "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv",
}
MARKET_FLOW_PATHS = {
    "market_flow_2010_2017": REPO / "research_input_data/inputs/market_flow/kiwoom_market_flow_2010_2017_krx_trading_days.csv",
    "market_flow_2018_2026_integrated": REPO / "research_input_data/inputs/market_flow/kiwoom_market_flow_2018_2026_integrated.csv",
    "market_flow_2025_2026_krx": REPO / "research_input_data/inputs/market_flow/kiwoom_market_flow_2025_2026_krx.csv",
}
S1_PATH = REPO / "data/acquired/round4/s1_adjusted_ohlc/adjusted_ohlc_all_tickers_2018_2026.csv"
W001_V2_TRADABLE = REPO / "data/processed/w001_v2/panel_with_tradable_state.csv"


def read_panel_date_ticker(path: Path) -> pd.DataFrame:
    # 2017-2024 / 2018-2024 panels have no native KRX종가; fall back to 종가
    try:
        df = pd.read_csv(path, usecols=["날짜", "종목코드", "KRX종가"], dtype={"종목코드": str, "KRX종가": "string"}, encoding="utf-8-sig")
        close_col = "KRX종가"
    except ValueError:
        df = pd.read_csv(path, usecols=["날짜", "종목코드", "종가"], dtype={"종목코드": str, "종가": "string"}, encoding="utf-8-sig")
        df = df.rename(columns={"종가": "KRX종가"})
        close_col = "종가_fallback"
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    df = df.dropna(subset=["날짜"]).copy()
    df["panel_id"] = path.stem
    df["has_krx_close"] = df["KRX종가"].notna() & (df["KRX종가"].astype(str).str.strip() != "")
    df.attrs["close_source"] = close_col
    return df.rename(columns={"날짜": "date", "종목코드": "ticker"})


def main() -> None:
    # ---- Load panel date×ticker pairs ----
    panel_frames = {}
    for tag, p in PANEL_PATHS.items():
        panel_frames[tag] = read_panel_date_ticker(p)

    # ---- Build candidate KRX trading calendars ----
    panel_calendars = {tag: sorted(df["date"].dt.normalize().unique()) for tag, df in panel_frames.items()}

    # market flow calendars
    flow_calendars = {}
    for tag, p in MARKET_FLOW_PATHS.items():
        flow = pd.read_csv(p, usecols=["date"], encoding="utf-8-sig")
        flow["date"] = pd.to_datetime(flow["date"], errors="coerce")
        flow = flow.dropna(subset=["date"])
        flow_calendars[tag] = sorted(flow["date"].dt.normalize().unique())

    # S1 adjusted OHLC
    s1 = pd.read_csv(S1_PATH, usecols=["date", "종목코드"], dtype={"종목코드": str}, encoding="utf-8-sig")
    s1["date"] = pd.to_datetime(s1["date"], errors="coerce")
    s1 = s1.dropna(subset=["date"])
    s1_calendar = sorted(s1["date"].dt.normalize().unique())

    # ---- Union calendar = candidate KRX trading calendar ----
    union_dates = set()
    for cal in (*panel_calendars.values(), *flow_calendars.values(), s1_calendar):
        union_dates.update(cal)
    union_calendar = pd.DatetimeIndex(sorted(union_dates))

    # ---- Within-period union (per-period coverage check) ----
    # Use market_flow as candidate trading-day reference because rows = 1 per day,
    # named "krx_trading_days" in the 2010-2017 file name.
    mkt2010 = set(flow_calendars["market_flow_2010_2017"])
    mkt2018 = set(flow_calendars["market_flow_2018_2026_integrated"])
    mkt2025 = set(flow_calendars["market_flow_2025_2026_krx"])

    # ---- Calendar source check ----
    src_check_lines = [
        "# KRX Calendar Source Check",
        "",
        "Date: 2026-05-23  ",
        "Scope: measurement-layer A0 only.",
        "",
        "## Question",
        "",
        "What is the authoritative KRX trading-calendar source available in this repo?",
        "",
        "## Candidate sources",
        "",
        "| candidate | file/method | nature | comment |",
        "|---|---|---|---|",
        "| **panel dates (union)** | 4 equity panels' `날짜` column | derived | not a calendar source; *follows* whatever trading days the panel rows cover; cannot be used to verify completeness |",
        "| **market_flow_2010_2017_krx_trading_days.csv** | file name claims `krx_trading_days` | semi-authoritative | 1 row per day; file name explicitly tagged with `krx_trading_days`; period 2010-01-04 to 2017-12-28 |",
        "| **market_flow_2018_2026_integrated.csv** | 1 row per day | semi-authoritative | period 2018-01-02 onwards; not file-name-tagged as calendar |",
        "| **market_flow_2025_2026_krx.csv** | 1 row per day, KRX-tagged | semi-authoritative | post-NXT, KRX-tagged |",
        "| **pykrx `get_market_ohlcv_by_date`** | pykrx API | external authoritative | requires KRX_ID/KRX_PW; used for S1 acquisition. Source = KRX official, but not committed to repo as a calendar file |",
        "| **KRX 공식 휴장일 리스트** | not in repo | authoritative | KRX 발표 휴장일 / 임시휴장 / 거래시간 변경 정보. Currently NOT acquired into repo. |",
        "",
        "## Finding",
        "",
        "Repo does **not** carry a standalone, named KRX trading-calendar file.",
        "The market_flow files implicitly act as a per-day trading-day index but only one of three",
        "(`kiwoom_market_flow_2010_2017_krx_trading_days.csv`) is explicitly tagged as a calendar.",
        "All other inputs (equity panels, S1 adjusted OHLC) are *consumers* of the calendar.",
        "",
        "## Per-Referee kill gate",
        "",
        "Referee verdict: **If KRX calendar source is unclear, execution simulation remains closed.**",
        "",
        "**Status: UNCLEAR.** Therefore execution simulation remains CLOSED (unchanged).",
        "",
        "## Working calendar used for this audit",
        "",
        "For the alignment check in this phase the executor uses the **union of dates that appear",
        "in at least one of**:",
        "- 4 equity panels (`날짜`)",
        "- 3 market_flow files (`date`)",
        "- S1 adjusted_ohlc_all_tickers_2018_2026.csv (`date`)",
        "",
        "This **union** is treated as a working KRX-trading-day candidate, not an authoritative calendar.",
        "It cannot validate KRX days the entire dataset universe missed.",
        "",
        "## Required for closure",
        "",
        "1. Acquisition of an authoritative KRX calendar (KRX `getJsonData.cmd` or pykrx `get_business_days`).",
        "2. Side-by-side reconciliation of:",
        "   - market_flow calendar",
        "   - panel-derived union calendar",
        "   - KRX official calendar",
        "3. Anomaly ledger of mismatches (휴장 / 임시휴장 / 거래시간단축).",
        "",
        "Until then, calendar source is **unclear** and execution-simulation gating remains closed.",
        "",
    ]
    (OUT / "krx_calendar_source_check.md").write_text("\n".join(src_check_lines), encoding="utf-8")

    # ---- Off-calendar rows: panel rows whose date is NOT in the corresponding period's flow calendar ----
    off_rows = []
    period_calendars = [
        ("kiwoom_2010_2016", mkt2010, "market_flow_2010_2017_krx_trading_days"),
        ("dynamic_top100_2017_2024", mkt2010 | mkt2018, "market_flow_2010_2017 ∪ 2018_2026"),
        ("dynamic_top100_2018_2024", mkt2018, "market_flow_2018_2026_integrated"),
        ("krx_2025_2026", mkt2018 | mkt2025, "market_flow_2018_2026 ∪ 2025_2026"),
    ]
    for tag, cal_set, cal_ref in period_calendars:
        df = panel_frames[tag]
        norm = df["date"].dt.normalize()
        mask = ~norm.isin(cal_set)
        bad = df[mask]
        if len(bad):
            dist = (bad.groupby(norm[mask]).size()
                      .reset_index(name="row_count")
                      .rename(columns={"date": "off_date"}))
            for _, r in dist.iterrows():
                off_rows.append({
                    "panel_id": tag,
                    "calendar_reference": cal_ref,
                    "off_date": r["off_date"].date().isoformat() if hasattr(r["off_date"], "date") else str(r["off_date"]),
                    "row_count": int(r["row_count"]),
                })
    off_df = pd.DataFrame(off_rows)
    off_df.to_csv(OUT / "off_calendar_rows.csv", index=False, encoding="utf-8")

    # ---- Missing calendar-panel days ----
    # For each panel period, find calendar days in the corresponding flow calendar
    # with ZERO panel rows.
    missing_rows = []
    for tag, cal_set, cal_ref in period_calendars:
        df = panel_frames[tag]
        df_min = df["date"].min()
        df_max = df["date"].max()
        cal_in_period = [d for d in cal_set if df_min <= d <= df_max]
        panel_dates = set(df["date"].dt.normalize())
        for d in cal_in_period:
            if d not in panel_dates:
                missing_rows.append({
                    "panel_id": tag,
                    "calendar_reference": cal_ref,
                    "missing_date": d.date().isoformat() if hasattr(d, "date") else str(d),
                })
    missing_df = pd.DataFrame(missing_rows)
    missing_df.to_csv(OUT / "missing_calendar_panel_days.csv", index=False, encoding="utf-8")

    # ---- Duplicate (ticker, date) rows ----
    dup_rows = []
    for tag, p in PANEL_PATHS.items():
        df = panel_frames[tag][["date", "ticker"]].copy()
        df["dup_count"] = df.groupby(["date", "ticker"])["ticker"].transform("size")
        dup = df[df["dup_count"] > 1].drop_duplicates(subset=["date", "ticker"])
        for _, r in dup.iterrows():
            dup_rows.append({
                "panel_id": tag,
                "date": r["date"].date().isoformat() if hasattr(r["date"], "date") else str(r["date"]),
                "ticker": r["ticker"],
                "occurrence_count": int(r["dup_count"]),
            })
    # also check W001 v2 tradable_state
    try:
        w = pd.read_csv(W001_V2_TRADABLE, usecols=["날짜", "종목코드"], dtype={"종목코드": str}, encoding="utf-8-sig")
        w["날짜"] = pd.to_datetime(w["날짜"], errors="coerce")
        w = w.dropna(subset=["날짜"]).copy()
        w["dup_count"] = w.groupby(["날짜", "종목코드"])["종목코드"].transform("size")
        dup = w[w["dup_count"] > 1].drop_duplicates(subset=["날짜", "종목코드"])
        for _, r in dup.iterrows():
            dup_rows.append({
                "panel_id": "w001_v2_panel_with_tradable_state",
                "date": r["날짜"].date().isoformat() if hasattr(r["날짜"], "date") else str(r["날짜"]),
                "ticker": r["종목코드"],
                "occurrence_count": int(r["dup_count"]),
            })
    except Exception as e:  # noqa: BLE001
        dup_rows.append({"panel_id": "w001_v2_panel_with_tradable_state", "date": "READ_ERROR", "ticker": "", "occurrence_count": -1})
    pd.DataFrame(dup_rows).to_csv(OUT / "duplicate_stock_date_rows.csv", index=False, encoding="utf-8")

    # ---- t+1 mapping reproducibility ----
    # Use the union calendar and check: for each panel period, can we map
    # signal_date → execution_date = next_trading_day reproducibly?
    union_calendar_sorted = pd.DatetimeIndex(sorted(union_dates))
    # Build next-day map on union calendar
    next_day_map = dict(zip(union_calendar_sorted[:-1], union_calendar_sorted[1:]))

    # For each panel, test reproducibility on a 100-sample of dates
    t1_lines = [
        "# T+1 Execution Mapping Reproducibility",
        "",
        "Date: 2026-05-23",
        "",
        "## Setup",
        "",
        "Union calendar (panel ∪ market_flow ∪ S1) = working-trading-day candidate.",
        "Next-day mapping = `next_day_map[d] = next d' in sorted(union)`.",
        "Reproducibility test = for each panel, sample N=200 rows and verify that the mapping",
        "produces a valid candidate execution date in the same calendar.",
        "",
        "## Results",
        "",
        "| panel | sample_n | mappable | unmappable_last_day | mappable_pct |",
        "|---|---:|---:|---:|---:|",
    ]
    rng = pd.Series([42, 137, 271, 433, 593, 757, 911, 1097, 1259, 1429,
                     1597, 1747, 1907, 2069, 2237, 2393, 2557, 2719, 2879, 3049])  # deterministic seeds
    repro_records = []
    for tag, df in panel_frames.items():
        sample_n = 200
        sample = df["date"].dt.normalize().drop_duplicates()
        sample = sample.iloc[::max(1, len(sample) // sample_n)].head(sample_n)
        mappable = sum(1 for d in sample if d in next_day_map)
        last_day = len(sample) - mappable
        pct = round(100.0 * mappable / max(1, len(sample)), 2)
        t1_lines.append(f"| `{tag}` | {len(sample)} | {mappable} | {last_day} | {pct}% |")
        repro_records.append({"panel": tag, "sample_n": len(sample), "mappable": mappable, "mappable_pct": pct})

    t1_lines += [
        "",
        "## Interpretation",
        "",
        "- A `mappable_pct < 100` means at least one sample date is the **last** date in the union",
        "  calendar (no next-day exists). This is expected on terminal dates only.",
        "- The mapping is **deterministic** given the same union calendar. Reproducibility is",
        "  therefore tied to the union-calendar definition above. If a new authoritative KRX",
        "  calendar source is acquired, the union calendar will change, and all t+1 mappings will",
        "  shift accordingly.",
        "",
        "## Per-Referee kill gate",
        "",
        "Referee verdict: **If t+1 mapping cannot be reproduced, execution simulation remains closed.**",
        "",
        "Mapping IS reproducible given a fixed union calendar. **But** the union calendar itself is",
        "not an authoritative KRX calendar (see `krx_calendar_source_check.md`). Therefore:",
        "",
        "- mapping reproducibility = `OK_relative_to_union_calendar`",
        "- absolute reproducibility against KRX official = **PENDING** (calendar source not acquired)",
        "",
        "Net: execution simulation remains **CLOSED** (unchanged).",
        "",
    ]
    (OUT / "t_plus_1_mapping_reproducibility.md").write_text("\n".join(t1_lines), encoding="utf-8")

    # ---- Summary ----
    summary_lines = [
        "# Calendar / Panel Alignment Summary — A0 Audit",
        "",
        "Date: 2026-05-23  ",
        "Scope: KR equity panel × KRX trading calendar.",
        "Output rule: measurement-layer only. No return / NAV / Sharpe.",
        "",
        "## Headline numbers",
        "",
        f"- Union working-calendar trading days (all sources): {len(union_calendar)} ({union_calendar.min().date()} → {union_calendar.max().date()})",
        f"- Off-calendar panel rows (date not in matching flow calendar): {len(off_df)} distinct (panel, date) pairs",
        f"- Missing calendar-panel days (flow-calendar days with zero panel rows): {len(missing_df)}",
        f"- Duplicate (ticker, date) rows across all panels + W001 v2 tradable: {len(dup_rows)}",
        "",
        "## Per-panel coverage",
        "",
        "| panel | row_count | first_date | last_date | n_distinct_dates | n_distinct_tickers |",
        "|---|---:|---|---|---:|---:|",
    ]
    for tag, df in panel_frames.items():
        summary_lines.append(
            f"| `{tag}` | {len(df)} | {df['date'].min().date()} | {df['date'].max().date()} | "
            f"{df['date'].dt.normalize().nunique()} | {df['ticker'].nunique()} |"
        )
    summary_lines += [
        "",
        "## Per-period off-calendar dates (top 10 by row count)",
        "",
        "| panel | calendar_ref | off_date | row_count |",
        "|---|---|---|---:|",
    ]
    if off_df.empty:
        summary_lines.append("| (none) | | | |")
    else:
        for _, r in off_df.sort_values("row_count", ascending=False).head(10).iterrows():
            summary_lines.append(f"| `{r['panel_id']}` | `{r['calendar_reference']}` | {r['off_date']} | {r['row_count']} |")

    summary_lines += [
        "",
        "## Missing-day counts per panel",
        "",
        "| panel | calendar_ref | missing_day_count |",
        "|---|---|---:|",
    ]
    if missing_df.empty:
        summary_lines.append("| (none) | | 0 |")
    else:
        agg = missing_df.groupby(["panel_id", "calendar_reference"]).size().reset_index(name="missing_day_count")
        for _, r in agg.iterrows():
            summary_lines.append(f"| `{r['panel_id']}` | `{r['calendar_reference']}` | {r['missing_day_count']} |")

    summary_lines += [
        "",
        "## Duplicate (ticker, date) summary per panel",
        "",
        "| panel | duplicate_pairs |",
        "|---|---:|",
    ]
    if not dup_rows:
        summary_lines.append("| (none) | 0 |")
    else:
        dup_agg = pd.DataFrame(dup_rows).groupby("panel_id").size().reset_index(name="duplicate_pairs")
        for _, r in dup_agg.iterrows():
            summary_lines.append(f"| `{r['panel_id']}` | {r['duplicate_pairs']} |")

    summary_lines += [
        "",
        "## Kill gates (Referee)",
        "",
        "- **Calendar source clear?** UNCLEAR → execution simulation remains CLOSED (see `krx_calendar_source_check.md`).",
        "- **T+1 mapping reproducible?** YES relative to union working calendar, PENDING against official KRX (see `t_plus_1_mapping_reproducibility.md`).",
        "- **Listed-universe certified survivorship-safe?** NO. Panel-only union cannot certify survivorship — that is the explicit purpose of `KR-LISTED-UNIVERSE-COVERAGE-BACKLOG-001` (P2 backlog).",
        "- **Executable status certified?** NO. Tradability flag / panel presence ≠ executable — `KR-EXECUTABLE-STATUS-BACKLOG-001` (P2 backlog) tracks the gap.",
        "",
        "## Cross references",
        "",
        "- `krx_calendar_source_check.md` (P0-2 artifact 2)",
        "- `off_calendar_rows.csv` (P0-2 artifact 3)",
        "- `missing_calendar_panel_days.csv` (P0-2 artifact 4)",
        "- `duplicate_stock_date_rows.csv` (P0-2 artifact 5)",
        "- `t_plus_1_mapping_reproducibility.md` (P0-2 artifact 6)",
        "- `../KR_FIELD_METADATA_CONTRACT_A0/` (P0-1 artifacts)",
        "- `../KR_LISTED_UNIVERSE_COVERAGE_BACKLOG/source_requirement_register.md`",
        "- `../KR_EXECUTABLE_STATUS_BACKLOG/source_requirement_register.md`",
        "",
        "## Hard locks",
        "",
        "- No return / NAV / CAGR / Sharpe / alpha / MDD anywhere.",
        "- No use of off-calendar rows as evidence of anything until the matching trading-day is verified.",
        "- No use of missing days as evidence of a halt or suspension (the missing day might be a vendor gap rather than a true non-trading day).",
        "- No executable assumption from panel presence.",
        "",
    ]
    (OUT / "calendar_panel_alignment_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")

    print(json.dumps({
        "union_calendar_days": len(union_calendar),
        "first_day": union_calendar.min().date().isoformat(),
        "last_day": union_calendar.max().date().isoformat(),
        "off_calendar_pairs": len(off_df),
        "missing_days": len(missing_df),
        "duplicate_pairs": len(dup_rows),
        "repro_records": repro_records,
    }, indent=2))


if __name__ == "__main__":
    main()
