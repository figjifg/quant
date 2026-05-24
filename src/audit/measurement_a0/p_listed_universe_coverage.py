"""KR-LISTED-UNIVERSE-COVERAGE-A0 builder.

Acquires monthly snapshots of KRX listed universe via pykrx
get_market_ticker_list(date, market). Reconciles against repo panels + W001 v2
lifecycle sources. Produces 12 outputs.

Audit + acquisition. No strategy testing. No execution simulation. No performance metric.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))

OUT = REPO / "reports/experiments/measurement_A0/KR_LISTED_UNIVERSE_COVERAGE_A0"
OUT.mkdir(parents=True, exist_ok=True)
ACQUIRED_DIR = REPO / "data/acquired/krx_listed_universe"
ACQUIRED_DIR.mkdir(parents=True, exist_ok=True)
MONTHLY_SNAPSHOTS = ACQUIRED_DIR / "krx_listed_monthly_snapshots_2010_2026.csv"


def load_env() -> None:
    env_path = REPO / "research_input_data/.env"
    if not env_path.exists():
        return
    text = env_path.read_text(encoding="utf-8-sig")
    for line in text.splitlines():
        line = line.strip().lstrip("﻿")
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ[k.strip()] = v.strip().strip('"').strip("'")


# ---------------------------------------------------------------------------
# Acquisition: monthly snapshots
# ---------------------------------------------------------------------------

def first_business_day_per_month(start: pd.Timestamp, end: pd.Timestamp,
                                 calendar_set: set[pd.Timestamp]) -> list[pd.Timestamp]:
    """For each month between start and end, pick the first calendar trading day."""
    months: list[pd.Timestamp] = []
    cursor = pd.Timestamp(year=start.year, month=start.month, day=1)
    while cursor <= end:
        # find first date in cursor's month that's in calendar_set
        in_month = [d for d in calendar_set if d.year == cursor.year and d.month == cursor.month]
        if in_month:
            months.append(min(in_month))
        cursor = (cursor + pd.offsets.MonthBegin(1)).normalize()
    return months


def load_official_calendar() -> set[pd.Timestamp]:
    """Load the official KRX calendar acquired in the prior phase."""
    cal_path = REPO / "data/acquired/krx_calendar/krx_official_calendar_2010_2026.csv"
    if not cal_path.exists():
        raise RuntimeError(f"missing calendar source: {cal_path}; run KR-KRX-CALENDAR phase first")
    df = pd.read_csv(cal_path, parse_dates=["date"])
    return set(df["date"].dt.normalize())


def acquire_monthly_snapshots() -> pd.DataFrame:
    """Acquire monthly first-business-day snapshots of KRX listed universe.

    Returns dataframe with: snapshot_date, ticker, market, name.
    """
    if MONTHLY_SNAPSHOTS.exists():
        print(f"[acquisition] reusing cached snapshots from {MONTHLY_SNAPSHOTS}")
        return pd.read_csv(MONTHLY_SNAPSHOTS, parse_dates=["snapshot_date"], dtype={"ticker": str})

    load_env()
    from pykrx import stock

    calendar = load_official_calendar()
    start = pd.Timestamp("2010-01-01")
    end = pd.Timestamp(datetime.now())
    snap_dates = first_business_day_per_month(start, end, calendar)
    print(f"[acquisition] will query {len(snap_dates)} monthly snapshots × 2 markets = {2 * len(snap_dates)} calls")

    rows: list[dict] = []
    for i, d in enumerate(snap_dates):
        d_str = d.strftime("%Y%m%d")
        for market in ("KOSPI", "KOSDAQ"):
            try:
                tickers = stock.get_market_ticker_list(d_str, market=market)
                # Get names per ticker — expensive; do it via a different call
                # stock.get_market_ticker_name returns a single name per ticker
                # To minimise calls, just record ticker + market here
                for t in tickers:
                    rows.append({
                        "snapshot_date": d.date().isoformat(),
                        "ticker": str(t).zfill(6),
                        "market": market,
                        "name": "",  # filled later if needed
                    })
            except Exception as e:
                print(f"[acquisition] {d_str} {market} ERROR: {e}")
        if (i + 1) % 12 == 0:
            print(f"[acquisition] progress: {i+1}/{len(snap_dates)} months ({d.date()})")
            time.sleep(0.5)
    df = pd.DataFrame(rows)
    df["snapshot_date"] = pd.to_datetime(df["snapshot_date"])
    df.to_csv(MONTHLY_SNAPSHOTS, index=False)
    print(f"[acquisition] wrote {len(df)} rows to {MONTHLY_SNAPSHOTS}")
    return df


# ---------------------------------------------------------------------------
# Source inventory
# ---------------------------------------------------------------------------

SOURCES = [
    {
        "source_id": "krx_monthly_snapshots_pykrx",
        "file_path": str(MONTHLY_SNAPSHOTS.relative_to(REPO)),
        "role": "official (monthly resolution)",
        "market_coverage": "KOSPI + KOSDAQ",
        "id_columns": "ticker, market, snapshot_date",
        "listing_date_field": "first_seen_in_snapshots (derived)",
        "delisting_field": "last_seen_in_snapshots (derived; precision = ±1 month)",
        "provenance": "pykrx stock.get_market_ticker_list with KRX_ID auth — acquired in this phase",
        "limitations": "monthly granularity; delisting/listing date precision ±1 month; KONEX not included",
    },
    {
        "source_id": "s4_krx_listed_companies_master",
        "file_path": "data/acquired/round4/s4_listed_companies/krx_listed_companies_master.csv",
        "role": "5-snapshot sample (partial)",
        "market_coverage": "KOSPI + KOSDAQ",
        "id_columns": "snapshot_date, ticker, market, name",
        "listing_date_field": "snapshot_date (not actual listing date)",
        "delisting_field": "absent",
        "provenance": "Round 4 S4 acquisition via pykrx (5 sample dates)",
        "limitations": "only 5 snapshot dates — too sparse to be a continuous source",
    },
    {
        "source_id": "s4_krx_ever_listed_table",
        "file_path": "data/acquired/round4/s4_listed_companies/krx_ever_listed_table.csv",
        "role": "5-snapshot union",
        "market_coverage": "KOSPI + KOSDAQ",
        "id_columns": "ticker",
        "listing_date_field": "first_snapshot (not actual listing date)",
        "delisting_field": "last_snapshot (not actual delisting date)",
        "provenance": "Round 4 S4 acquisition (5 sample union)",
        "limitations": "sample-only; first/last_snapshot dates are sample bookends, not real listing/delisting dates",
    },
    {
        "source_id": "w001_v2_permanent_id_master",
        "file_path": "data/processed/w001_v2/permanent_id_master.csv",
        "role": "derived identity resolution",
        "market_coverage": "panel tickers + DART corp_code matches",
        "id_columns": "ticker, permanent_id, permanent_id_source, corp_code_dart",
        "listing_date_field": "krx_first_snapshot (NOT actual listing date — sample bookend)",
        "delisting_field": "krx_last_snapshot (NOT actual delisting date — sample bookend)",
        "provenance": "W001 v2 derivation from S4 + DART corp_code mapping",
        "limitations": "lifecycle dates are sample bookends; KRX_TICKER_xxxxxx fallback IDs are temporary",
    },
    {
        "source_id": "w001_v2_listing_status_events",
        "file_path": "data/processed/w001_v2/listing_status_events.csv",
        "role": "DART-derived status events",
        "market_coverage": "tickers with DART events",
        "id_columns": "ticker, rcept_dt, category, rcept_no",
        "listing_date_field": "absent",
        "delisting_field": "category=delisting + rcept_dt",
        "provenance": "OPENDART pblntfty=I filtered (S3)",
        "limitations": "filtered from pblntfty=I disclosures; 53.1% coverage of disappeared tickers per ACQUISITION_SUMMARY.md",
    },
    {
        "source_id": "w001_v2_listing_status_terminal",
        "file_path": "data/processed/w001_v2/listing_status_terminal.csv",
        "role": "derived terminal status",
        "market_coverage": "panel tickers with terminal events",
        "id_columns": "ticker, terminal_status, terminal_date",
        "listing_date_field": "absent",
        "delisting_field": "terminal_date",
        "provenance": "W001 v2 derivation from listing_status_events",
        "limitations": "covers only DART-flagged terminal events; 47% of historic disappearances unresolved",
    },
    {
        "source_id": "equity_panel_kiwoom_2010_2016",
        "file_path": "research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv",
        "role": "vendor dynamic_top100 selection",
        "market_coverage": "Top 100 by liquidity per day; KOSPI+KOSDAQ mix",
        "id_columns": "날짜, 종목코드",
        "listing_date_field": "first row appearance (not actual listing date — selection-bias)",
        "delisting_field": "absent",
        "provenance": "Kiwoom vendor",
        "limitations": "selection bias; not survivorship-safe; current and prior top 100 only",
    },
    {
        "source_id": "equity_panel_dynamic_top100_2017_2024",
        "file_path": "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv",
        "role": "vendor dynamic_top100",
        "market_coverage": "Top 100 by liquidity per day",
        "id_columns": "날짜, 종목코드",
        "listing_date_field": "first appearance (selection-bias)",
        "delisting_field": "absent",
        "provenance": "Kiwoom vendor",
        "limitations": "selection bias; not survivorship-safe",
    },
    {
        "source_id": "equity_panel_dynamic_top100_2018_2024",
        "file_path": "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv",
        "role": "vendor dynamic_top100",
        "market_coverage": "Top 100 by liquidity per day",
        "id_columns": "날짜, 종목코드",
        "listing_date_field": "first appearance (selection-bias)",
        "delisting_field": "absent",
        "provenance": "Kiwoom vendor",
        "limitations": "selection bias",
    },
    {
        "source_id": "equity_panel_krx_2025_2026",
        "file_path": "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv",
        "role": "KRX-tagged dynamic_top100",
        "market_coverage": "Top 100 by liquidity per day; post-NXT",
        "id_columns": "날짜, 종목코드",
        "listing_date_field": "first appearance (selection-bias)",
        "delisting_field": "absent",
        "provenance": "KRX integrated panel",
        "limitations": "selection bias",
    },
]


def write_source_inventory() -> None:
    lines = [
        "# Listed-Universe Source Inventory",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-LISTED-UNIVERSE-COVERAGE-A0",
        "",
        "## Sources surveyed",
        "",
        "| source_id | role | market | id_cols | listing field | delisting field | provenance | limitations |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for s in SOURCES:
        lines.append(
            f"| `{s['source_id']}` | {s['role']} | {s['market_coverage']} | "
            f"{s['id_columns']} | {s['listing_date_field']} | {s['delisting_field']} | "
            f"{s['provenance']} | {s['limitations']} |"
        )
    lines += [
        "",
        "## Newly acquired in this phase",
        "",
        "- `krx_monthly_snapshots_pykrx` — monthly first-trading-day snapshots of",
        "  `pykrx.stock.get_market_ticker_list` for KOSPI + KOSDAQ, 2010-01 → 2026-05.",
        "  Requires KRX_ID/KRX_PW (user-owned credentials, loaded from local .env, NOT",
        "  committed). Monthly granularity is sufficient to detect listing/delisting",
        "  to within ±1 month; refinement to daily resolution is a future-phase option.",
        "",
        "## Sources NOT in this phase's scope",
        "",
        "- KONEX market (excluded from this audit).",
        "- ETF/ETN universe (separate inventory).",
        "- Pre-2010 listings (out of audit window).",
        "- Intraday halt / shortened session metadata (in `KR-EXECUTABLE-STATUS-BACKLOG`).",
        "",
    ]
    (OUT / "source_inventory.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Lifecycle coverage table
# ---------------------------------------------------------------------------

def build_lifecycle_coverage(snapshots: pd.DataFrame) -> pd.DataFrame:
    """Derive per-ticker first/last snapshot from acquired monthly data + join with W001 v2."""
    # Per ticker: market(s), first_snapshot, last_snapshot, n_snapshots
    grp = snapshots.groupby("ticker").agg(
        markets=("market", lambda s: ",".join(sorted(set(s)))),
        first_snapshot=("snapshot_date", "min"),
        last_snapshot=("snapshot_date", "max"),
        n_snapshots=("snapshot_date", "count"),
    ).reset_index()
    # Join with permanent_id_master
    pid_path = REPO / "data/processed/w001_v2/permanent_id_master.csv"
    if pid_path.exists():
        pid = pd.read_csv(pid_path, encoding="utf-8-sig", dtype={"ticker": str})
        pid["ticker"] = pid["ticker"].str.zfill(6)
        grp = grp.merge(
            pid[["ticker", "permanent_id", "permanent_id_source", "corp_code_dart",
                 "corp_name_dart", "name_krx"]],
            on="ticker", how="left",
        )
    # Join with terminal status
    term_path = REPO / "data/processed/w001_v2/listing_status_terminal.csv"
    if term_path.exists():
        term = pd.read_csv(term_path, encoding="utf-8-sig", dtype={"ticker": str})
        term["ticker"] = term["ticker"].str.zfill(6)
        grp = grp.merge(
            term[["ticker", "terminal_status", "terminal_date"]],
            on="ticker", how="left",
        )
    # Coverage flag
    today_month_end = pd.Timestamp(datetime.now()).normalize() - pd.offsets.MonthEnd(1)
    grp["confidence_flag"] = grp.apply(
        lambda r: (
            "delisted_with_terminal" if pd.notna(r.get("terminal_status", None)) and r.get("terminal_status") in ("delisted", "suspended_last_known")
            else "still_listed" if pd.to_datetime(r["last_snapshot"]) >= today_month_end - pd.offsets.MonthBegin(3)
            else "disappeared_no_terminal" if pd.isna(r.get("terminal_status", None))
            else "other"
        ),
        axis=1,
    )
    return grp


def write_lifecycle_coverage_table(lc: pd.DataFrame) -> None:
    cols = ["ticker", "markets", "first_snapshot", "last_snapshot", "n_snapshots",
            "permanent_id", "permanent_id_source", "corp_code_dart", "corp_name_dart",
            "name_krx", "terminal_status", "terminal_date", "confidence_flag"]
    # Ensure all cols exist
    for c in cols:
        if c not in lc.columns:
            lc[c] = ""
    lc[cols].to_csv(OUT / "listed_lifecycle_coverage_table.csv", index=False)


# ---------------------------------------------------------------------------
# Reconciliation: panels vs official
# ---------------------------------------------------------------------------

def load_panel_tickers() -> dict[str, set[str]]:
    paths = {
        "kiwoom_2010_2016": REPO / "research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv",
        "dynamic_top100_2017_2024": REPO / "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv",
        "dynamic_top100_2018_2024": REPO / "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv",
        "krx_2025_2026": REPO / "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv",
    }
    out = {}
    for k, p in paths.items():
        df = pd.read_csv(p, usecols=["종목코드"], dtype={"종목코드": str}, encoding="utf-8-sig")
        df["종목코드"] = df["종목코드"].str.zfill(6)
        out[k] = set(df["종목코드"].unique())
    return out


def build_reconciliation(snapshots: pd.DataFrame, panels: dict[str, set[str]]) -> tuple[list[dict], dict]:
    official_set = set(snapshots["ticker"].unique())
    union_panel = set()
    for s in panels.values():
        union_panel |= s

    all_tickers = sorted(official_set | union_panel)
    rows = []
    matched, panel_only, official_only = 0, 0, 0
    by_panel: dict[str, dict[str, int]] = {k: {"matched": 0, "panel_only_vs_official": 0} for k in panels}

    for t in all_tickers:
        in_off = t in official_set
        in_pan = t in union_panel
        if in_off and in_pan:
            cls = "matched_official_and_panel"
            matched += 1
        elif in_pan and not in_off:
            cls = "panel_only"
            panel_only += 1
        else:
            cls = "official_only"
            official_only += 1
        per_panel = {k: t in s for k, s in panels.items()}
        for k, has in per_panel.items():
            if has and in_off:
                by_panel[k]["matched"] += 1
            elif has and not in_off:
                by_panel[k]["panel_only_vs_official"] += 1
        rows.append({
            "ticker": t,
            "classification": cls,
            "in_official_universe": in_off,
            "in_union_panel": in_pan,
            **{f"in_{k}": per_panel[k] for k in panels},
        })

    summary = {
        "official_universe_size": len(official_set),
        "union_panel_size": len(union_panel),
        "matched": matched,
        "panel_only": panel_only,
        "official_only": official_only,
        "per_panel": by_panel,
    }
    return rows, summary


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)


def write_official_source_report(snapshots: pd.DataFrame) -> None:
    n_snaps = snapshots["snapshot_date"].nunique()
    n_tickers = snapshots["ticker"].nunique()
    first = snapshots["snapshot_date"].min()
    last = snapshots["snapshot_date"].max()
    by_market = snapshots.groupby("market")["ticker"].nunique().to_dict()
    lines = [
        "# Official Listed-Universe Source Report",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-LISTED-UNIVERSE-COVERAGE-A0",
        "",
        "## Acquired source",
        "",
        f"- Method: pykrx `get_market_ticker_list` per (date, market)",
        f"- Endpoint: KRX via pykrx with KRX_ID auth",
        f"- Granularity: **monthly** (first trading day of each month)",
        f"- Date range: **{first.date()} → {last.date()}**",
        f"- Snapshot count: **{n_snaps}**",
        f"- Markets: KOSPI + KOSDAQ",
        f"- Unique tickers ever seen: **{n_tickers}**",
        f"  - KOSPI: {by_market.get('KOSPI', 0)}",
        f"  - KOSDAQ: {by_market.get('KOSDAQ', 0)}",
        f"- Storage: `{MONTHLY_SNAPSHOTS.relative_to(REPO).as_posix()}` (gitignored)",
        "",
        "## Why this is the best available source",
        "",
        "- pykrx `get_market_ticker_list(date)` returns the exact list of tickers KRX",
        "  considered listed on that date. With KRX_ID auth this works back to 2010.",
        "- This is the **closest to authoritative** for daily listed-universe.",
        "- Monthly granularity is a conservative compromise (~204 snapshots vs ~4000",
        "  daily) — it detects listing/delisting to within ±1 month, which is",
        "  sufficient for survivorship-safety audit but NOT for execution-day",
        "  precision (separate executable-status phase).",
        "",
        "## Limitations",
        "",
        "- Monthly granularity (±1 month precision on listing/delisting dates).",
        "- KONEX excluded.",
        "- Does not include corporate-action linkage (merger/split target ticker),",
        "  rename history, or ticker reuse mapping.",
        "- Pre-2010 out of scope.",
        "- Intraday halts / shortened sessions not captured (separate phase).",
        "",
        "## Hard locks (preserved)",
        "",
        "- No credential committed.",
        "- No survivorship-safe claim made here — see `survivorship_safety_assessment.md`.",
        "- No execution simulation run.",
        "- No strategy testing.",
        "",
    ]
    (OUT / "official_listed_universe_source_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_reconciliation_summary(summary: dict) -> None:
    lines = [
        "# Panel vs Official Reconciliation Summary",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-LISTED-UNIVERSE-COVERAGE-A0",
        "",
        "## Headline",
        "",
        f"- Official universe (monthly snapshots): **{summary['official_universe_size']}** unique tickers ever listed",
        f"- Union of repo panel tickers: **{summary['union_panel_size']}** unique tickers",
        f"- Matched (in both): **{summary['matched']}**",
        f"- Panel-only (panel has ticker but official does NOT): **{summary['panel_only']}**",
        f"- Official-only (official has ticker but no panel covers): **{summary['official_only']}**",
        "",
        "## Per-panel reconciliation",
        "",
        "| panel | matched_to_official | panel_only_vs_official |",
        "|---|---:|---:|",
    ]
    for k, v in summary["per_panel"].items():
        lines.append(f"| `{k}` | {v['matched']} | {v['panel_only_vs_official']} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- `panel_only_vs_official > 0` indicates panel tickers that the monthly KRX",
        "  snapshots did NOT capture. Most likely causes:",
        "  1. Ticker listed AND delisted within a single calendar month (would miss",
        "     the monthly snapshot in both directions).",
        "  2. Vendor mis-coded ticker.",
        "  3. KONEX or other market-segment ticker (excluded from this scope).",
        "  4. Pre-2010 listing that delisted before first snapshot.",
        "- `official_only` indicates tickers KRX listed during the audit window but",
        "  the repo's dynamic_top100 selection never included them (low-liquidity",
        "  names). This is the survivorship blind spot.",
        "- The size of `official_only` is the headline indicator of how survivor-biased",
        "  the panel is.",
        "",
        "## Survivorship implication",
        "",
        "Repo panel = `union_panel_size` ≪ official `official_universe_size`. The",
        "dynamic_top100 panels include only liquid names; delisted small caps are",
        "absent. **Survivorship-safe claim cannot be made** from panel data alone.",
        "See `survivorship_safety_assessment.md` for the full assessment.",
        "",
        "## Hard locks (preserved)",
        "",
        "- No survivorship-safe claim authorised yet.",
        "- No strategy testing.",
        "- No execution simulation.",
        "",
    ]
    (OUT / "panel_vs_official_reconciliation_summary.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Survivorship assessment
# ---------------------------------------------------------------------------

def write_survivorship_assessment(summary: dict, lc: pd.DataFrame) -> None:
    n_official = summary["official_universe_size"]
    n_union = summary["union_panel_size"]
    n_official_only = summary["official_only"]
    n_terminal = int(lc["terminal_status"].notna().sum()) if "terminal_status" in lc.columns else 0
    n_disappeared_no_terminal = int((lc["confidence_flag"] == "disappeared_no_terminal").sum()) if "confidence_flag" in lc.columns else 0

    lines = [
        "# Survivorship Safety Assessment",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-LISTED-UNIVERSE-COVERAGE-A0",
        "",
        "## Headline verdict",
        "",
        "**NOT SURVIVORSHIP-SAFE — partial lifecycle coverage.**",
        "",
        f"- Official ever-listed universe: **{n_official}**",
        f"- Repo panel union: **{n_union}** (~{n_union/n_official*100:.1f}% of official)",
        f"- Tickers in official but NOT in any panel: **{n_official_only}** (~{n_official_only/n_official*100:.1f}% of official)",
        f"- Tickers in coverage table with terminal status: **{n_terminal}**",
        f"- Tickers in coverage table that disappeared without a terminal event: **{n_disappeared_no_terminal}**",
        "",
        "## Required checks (Referee-listed)",
        "",
        "| check | status | evidence |",
        "|---|---|---|",
        f"| delisted tickers represented? | PARTIAL | {n_terminal} have terminal status; {n_disappeared_no_terminal} disappeared without one |",
        f"| merged tickers represented? | NOT CERTIFIED | merger/split linkage not in scope; W001 v2 listing_status_events 47% disappearance unresolved |",
        f"| renamed tickers mapped? | PARTIAL | permanent_id_master maps via DART corp_code but rename HISTORY is not preserved |",
        f"| relisted / code-reused tickers separated? | NOT CERTIFIED | monthly snapshots cannot distinguish same-ticker-code reuse if relisting occurs in different month |",
        f"| panel disappearance explained? | PARTIAL | S3 covers 53.1% of 258 disappeared tickers per ACQUISITION_SUMMARY |",
        f"| dynamic_top100 historical members retained? | YES | all 4 panel files preserved in repo |",
        f"| current-only survivor universe avoided? | NO | panel selection is dynamic_top100 by liquidity — biased toward currently-liquid names |",
        f"| terminal event dates available and plausible? | PARTIAL | from W001 v2 listing_status_terminal — covers DART-flagged events only |",
        "",
        "## Why NOT survivorship-safe",
        "",
        f"1. The repo panel covers ~{n_union/n_official*100:.1f}% of the official",
        "   ever-listed universe. Roughly {0:.1f}% of historic listings are absent —",
        "   primarily delisted small caps and tickers that never entered dynamic_top100.".format(n_official_only/n_official*100),
        "",
        "2. Vendor dynamic_top100 selection is liquidity-biased. A backtest run only on",
        "   panel data would systematically exclude failures (delisted small caps),",
        "   producing survivorship-biased results.",
        "",
        "3. The W001 v2 terminal-status coverage is partial (47% of historic",
        f"   disappearances unresolved). {n_disappeared_no_terminal} tickers in the",
        "   coverage table disappeared without a terminal event — they may be",
        "   delisted, merged, or renamed; the audit cannot distinguish.",
        "",
        "4. Code reuse: monthly snapshots cannot detect ticker code reuse if",
        "   delisting + relisting occur in different months. Need daily-resolution",
        "   universe to disambiguate, which is a future-phase option.",
        "",
        "## What this means for future strategy work",
        "",
        "- No survivorship-safe claim is supported by this phase.",
        "- Any future strategy reopen requires:",
        "  - acquisition of a complete (daily-resolution) listed-universe with",
        "    explicit corporate-action linkage,",
        "  - resolution of the 47%-unresolved disappearance subset,",
        "  - explicit handling of code reuse,",
        "  - Round of dependent A0 audits (sector aggregator, universe builder, panel",
        "    loader) re-run with the corrected universe.",
        "",
        "## Hard locks (preserved)",
        "",
        "- No survivorship-safe claim made.",
        "- No strategy testing.",
        "- No execution simulation.",
        "- No production / paper / P08 / live readiness.",
        "",
    ]
    (OUT / "survivorship_safety_assessment.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Permanent ID coverage update
# ---------------------------------------------------------------------------

def write_permanent_id_update(lc: pd.DataFrame, snapshots: pd.DataFrame) -> None:
    pid_path = REPO / "data/processed/w001_v2/permanent_id_master.csv"
    if not pid_path.exists():
        return
    pid = pd.read_csv(pid_path, encoding="utf-8-sig", dtype={"ticker": str})
    pid["ticker"] = pid["ticker"].str.zfill(6)
    by_source = Counter(pid["permanent_id_source"].fillna("missing").tolist())

    # Cross-check fallback IDs against newly-acquired official universe
    fallback_tickers = pid[pid["permanent_id_source"] == "krx_ticker_fallback"]["ticker"].tolist()
    official_tickers = set(snapshots["ticker"].unique())
    fallback_in_official = sum(1 for t in fallback_tickers if t in official_tickers)
    fallback_not_in_official = len(fallback_tickers) - fallback_in_official

    lines = [
        "# Permanent ID Coverage Update",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-LISTED-UNIVERSE-COVERAGE-A0",
        "",
        "## Prior state (W001 v2 permanent_id_master.csv)",
        "",
        "| source | count |",
        "|---|---:|",
    ]
    for k, v in by_source.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        f"## Fallback IDs cross-checked against acquired official universe",
        "",
        f"- Total tickers in permanent_id_master with `krx_ticker_fallback` source: **{len(fallback_tickers)}**",
        f"- Of those, present in newly-acquired official monthly snapshots: **{fallback_in_official}**",
        f"- Of those, NOT present in official snapshots: **{fallback_not_in_official}**",
        "",
        "## Interpretation",
        "",
        "- `krx_ticker_fallback` IDs were assigned when no DART corp_code match was",
        "  found at the time of W001 v2 derivation. The newly-acquired official",
        "  universe lets us check whether these fallback tickers existed on KRX at",
        "  all.",
        "- Fallback tickers present in official snapshots = real KRX tickers without",
        "  a DART corp_code mapping (could be ETFs, REITs, or DART-unindexed names).",
        "- Fallback tickers absent from official snapshots = either out-of-window",
        "  delistings or panel typos.",
        "",
        "## Remaining issue",
        "",
        "- KRX_TICKER_xxxxxx fallback IDs remain **temporary** (ticker-based). They",
        "  are NOT stable across rename or code-reuse events.",
        "- Stable permanent IDs require:",
        "  - successful DART corp_code lookup, OR",
        "  - a KRX-stable issuer ID (not currently available in repo).",
        "- The fallback IDs are usable for current panel work but should be re-mapped",
        "  before any future strategy reopen.",
        "",
        "## Status",
        "",
        f"- {by_source.get('dart_corp_code', 0)} DART-corp-code IDs: **stable**",
        f"- {by_source.get('krx_ticker_fallback', 0)} KRX-ticker-fallback IDs: **temporary** (acceptable for measurement-layer audit; blocks full pass for strategy reopen)",
        "",
        "## Hard locks (preserved)",
        "",
        "- No strategy reopen authorised by this update.",
        "- No survivorship-safe claim.",
        "",
    ]
    (OUT / "permanent_id_coverage_update.md").write_text("\n".join(lines), encoding="utf-8")


def write_delisted_merged_renamed(lc: pd.DataFrame) -> None:
    n_delisted = int((lc.get("terminal_status", "") == "delisted").sum()) if "terminal_status" in lc.columns else 0
    n_suspended = int((lc.get("terminal_status", "") == "suspended_last_known").sum()) if "terminal_status" in lc.columns else 0
    lines = [
        "# Delisted / Merged / Renamed Coverage",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-LISTED-UNIVERSE-COVERAGE-A0",
        "",
        "## Coverage from existing sources",
        "",
        f"- Delisted tickers (W001 v2 listing_status_terminal `terminal_status='delisted'`): **{n_delisted}**",
        f"- Suspended-last-known tickers: **{n_suspended}**",
        "",
        "## Gaps",
        "",
        "- **Merger linkage**: NOT in repo. When ticker A is merged into ticker B,",
        "  the repo has no mapping A→B. This blocks survivorship-safe re-construction",
        "  of holdings histories.",
        "- **Rename history**: NOT in repo. Permanent_id_master captures *current*",
        "  name only.",
        "- **Relisting / code reuse**: NOT in repo. Same KRX ticker code can be reused",
        "  after a delisting; the repo cannot currently distinguish.",
        "- **Split / spin-off**: NOT in repo. Corporate-action overlay (S1 adjusted",
        "  OHLC) captures price effect but not identity remapping.",
        "",
        "## What would resolve these gaps",
        "",
        "- Per-ticker corporate-action ledger (merger / split / rename / relisting)",
        "  from a single authoritative source. Candidates: KRX corporate action API,",
        "  KOSCOM event feed, OPENDART body parse (which is CLOSED AS PARTIAL).",
        "- Until then, these gaps remain reopen blockers for any strategy work.",
        "",
        "## Hard locks (preserved)",
        "",
        "- No survivorship-safe claim.",
        "- No strategy reopen.",
        "",
    ]
    (OUT / "delisted_merged_renamed_coverage.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Defect ledger
# ---------------------------------------------------------------------------

def build_defect_ledger(recon_rows: list[dict], lc: pd.DataFrame, summary: dict) -> list[dict]:
    defects = []
    defect_id = 1

    # Panel-only tickers — defect (panel ticker not in official source)
    for r in recon_rows:
        if r["classification"] == "panel_only":
            defects.append({
                "defect_id": f"LUC_{defect_id:05d}",
                "severity": "medium",
                "defect_class": "panel_ticker_not_in_official_source",
                "ticker": r["ticker"],
                "detail": "panel contains this ticker but official monthly snapshots do not",
                "recommended_handling": (
                    "manual review: may be intra-month listing+delisting, "
                    "KONEX-segment ticker, or vendor typo"
                ),
            })
            defect_id += 1

    # Disappeared no terminal — defect
    if "confidence_flag" in lc.columns:
        for _, r in lc[lc["confidence_flag"] == "disappeared_no_terminal"].iterrows():
            defects.append({
                "defect_id": f"LUC_{defect_id:05d}",
                "severity": "high",
                "defect_class": "disappeared_no_terminal_event",
                "ticker": r["ticker"],
                "detail": (
                    f"last seen {r['last_snapshot']}; no terminal status in W001 v2 "
                    "listing_status_terminal — may be delisted/merged/renamed"
                ),
                "recommended_handling": "manual investigation; possible merger target",
            })
            defect_id += 1

    # Fallback IDs that aren't in official universe — defect
    pid_path = REPO / "data/processed/w001_v2/permanent_id_master.csv"
    if pid_path.exists():
        pid = pd.read_csv(pid_path, encoding="utf-8-sig", dtype={"ticker": str})
        pid["ticker"] = pid["ticker"].str.zfill(6)
        official_set = set(lc["ticker"].tolist())
        fallback_missing = pid[
            (pid["permanent_id_source"] == "krx_ticker_fallback") &
            (~pid["ticker"].isin(official_set))
        ]
        for _, r in fallback_missing.iterrows():
            defects.append({
                "defect_id": f"LUC_{defect_id:05d}",
                "severity": "medium",
                "defect_class": "fallback_id_not_in_official_universe",
                "ticker": r["ticker"],
                "detail": "krx_ticker_fallback ID has no match in newly-acquired official monthly snapshots",
                "recommended_handling": "verify whether real KRX ticker (out-of-window) or panel artifact",
            })
            defect_id += 1

    return defects


# ---------------------------------------------------------------------------
# Gate status + final summary
# ---------------------------------------------------------------------------

def write_gate_status(summary: dict, n_defects: int, n_disappeared: int) -> str:
    n_official_only = summary["official_only"]
    n_panel_only = summary["panel_only"]

    if n_official_only > 1000 or n_disappeared > 100:
        gate = "PARTIAL"
        rationale = (
            "official universe acquired (monthly resolution) and reconciled against repo panels, "
            "but coverage gaps are substantial: panel is materially survivor-biased "
            f"({n_official_only} official-only tickers absent from panel), and {n_disappeared} "
            "tickers disappeared without a terminal event. Strategy work remains CLOSED."
        )
    elif n_defects > 0:
        gate = "LISTED_UNIVERSE_RECONCILED_BUT_STRATEGY_STILL_CLOSED"
        rationale = (
            f"official universe reconciled with {n_defects} defects; strategy reopen "
            "still blocked by survivorship-safe-claim requirement"
        )
    else:
        gate = "LISTED_UNIVERSE_RECONCILED_BUT_STRATEGY_STILL_CLOSED"
        rationale = "official universe acquired and reconciled; strategy testing still closed"

    lines = [
        "# Listed-Universe Gate Status",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-LISTED-UNIVERSE-COVERAGE-A0",
        "",
        f"## Gate state: **{gate}**",
        "",
        "### Rationale",
        "",
        rationale,
        "",
        "## Permitted enum (Referee-fixed)",
        "",
        "- `DATA_SOURCE_FAIL`",
        "- `PARTIAL`",
        "- `OFFICIAL_SOURCE_ACQUIRED_BUT_NOT_FULLY_RECONCILED`",
        "- `LISTED_UNIVERSE_RECONCILED_BUT_STRATEGY_STILL_CLOSED`",
        "- `READY_FOR_NEXT_A0_REVIEW`",
        "",
        "## Numerical inputs",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| Official universe size | {summary['official_universe_size']} |",
        f"| Union panel size | {summary['union_panel_size']} |",
        f"| Matched | {summary['matched']} |",
        f"| Panel-only | {n_panel_only} |",
        f"| Official-only | {n_official_only} |",
        f"| Disappeared without terminal | {n_disappeared} |",
        f"| Total defects | {n_defects} |",
        "",
        "## Important boundary",
        "",
        "- Strategy testing is NOT opened.",
        "- Execution simulation is NOT opened.",
        "- Survivorship-safe claim is NOT made (see `survivorship_safety_assessment.md`).",
        "",
    ]
    (OUT / "listed_universe_gate_status.md").write_text("\n".join(lines), encoding="utf-8")
    return gate


def write_final_summary(snapshots: pd.DataFrame, summary: dict, lc: pd.DataFrame,
                        n_defects: int, gate: str) -> None:
    n_official = summary["official_universe_size"]
    n_union = summary["union_panel_size"]
    n_official_only = summary["official_only"]
    n_panel_only = summary["panel_only"]
    n_matched = summary["matched"]
    n_disappeared = int((lc.get("confidence_flag", "") == "disappeared_no_terminal").sum()) if "confidence_flag" in lc.columns else 0
    n_terminal = int(lc.get("terminal_status", "").notna().sum()) if "terminal_status" in lc.columns else 0
    first = snapshots["snapshot_date"].min()
    last = snapshots["snapshot_date"].max()

    lines = [
        "# KR-LISTED-UNIVERSE-COVERAGE-A0 — Final Summary",
        "",
        "Date: 2026-05-24  ",
        "Predecessor: KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0 CLOSED.",
        "",
        "## Scope respected",
        "",
        "- Measurement-layer listed-universe / lifecycle audit only.",
        "- No strategy testing.",
        "- No performance diagnostics.",
        "- No execution simulation.",
        "- No production / paper / P08 / live / shadow.",
        "",
        "## What was delivered",
        "",
        "Code artifacts:",
        "- `src/audit/measurement_a0/p_listed_universe_coverage.py`",
        "",
        "Data artifacts:",
        f"- `data/acquired/krx_listed_universe/krx_listed_monthly_snapshots_2010_2026.csv` "
        f"(gitignored; monthly first-trading-day KRX listed snapshots {first.date()} → {last.date()})",
        "",
        "Reports (this dir, 12 outputs):",
        "1. `listed_universe_referee_lock.md`",
        "2. `source_inventory.md`",
        "3. `official_listed_universe_source_report.md`",
        "4. `listed_lifecycle_coverage_table.csv`",
        "5. `panel_vs_official_reconciliation_summary.md`",
        "6. `panel_vs_official_reconciliation_ledger.csv`",
        "7. `permanent_id_coverage_update.md`",
        "8. `delisted_merged_renamed_coverage.md`",
        "9. `survivorship_safety_assessment.md`",
        "10. `listed_universe_defect_ledger.csv`",
        "11. `listed_universe_gate_status.md`",
        "12. `calendar_source_final_summary.md` (this file actually named `listed_universe_final_summary.md`)",
        "",
        "## Acquisition headline",
        "",
        "- Method: pykrx `get_market_ticker_list(date, market)` with KRX_ID auth.",
        "- Granularity: **monthly first-trading-day** across 2010-01 → 2026-05.",
        f"- Total unique tickers ever listed: **{n_official}**.",
        f"- Coverage: KOSPI + KOSDAQ.",
        "",
        "## Reconciliation headline",
        "",
        f"- Official universe: **{n_official}** tickers",
        f"- Union panel: **{n_union}** tickers ({n_union/n_official*100:.1f}% of official)",
        f"- Matched: **{n_matched}**",
        f"- Panel-only: **{n_panel_only}**",
        f"- Official-only: **{n_official_only}**",
        "",
        "## Lifecycle coverage",
        "",
        f"- Tickers with W001 v2 terminal status: **{n_terminal}**",
        f"- Tickers disappeared without terminal event: **{n_disappeared}**",
        "",
        "## Defect ledger",
        "",
        f"- Total defects: **{n_defects}**",
        "- Classes: `panel_ticker_not_in_official_source`, `disappeared_no_terminal_event`, `fallback_id_not_in_official_universe`",
        "",
        "## Survivorship-safety verdict",
        "",
        "**NOT SURVIVORSHIP-SAFE — partial lifecycle coverage.**",
        "",
        f"Repo panel covers ~{n_union/n_official*100:.1f}% of official ever-listed",
        f"universe. ~{n_official_only/n_official*100:.1f}% of historic listings are",
        "absent from panel — primarily delisted small caps. Merger linkage, rename",
        "history, and code reuse are not in repo. See `survivorship_safety_assessment.md`.",
        "",
        f"## Listed-universe gate state: **{gate}**",
        "",
        "## Pass criteria evaluation",
        "",
        "| criterion | status |",
        "|---|---|",
        "| Listed-universe source identified + documented | YES (best-available, monthly resolution) |",
        "| Source date range + market coverage stated | YES (2010-01 → 2026-05, KOSPI+KOSDAQ) |",
        "| Existing panel tickers reconciled against source | YES |",
        "| Delisted/merged/renamed/relisted/code-reuse risks assessed | PARTIAL (see `delisted_merged_renamed_coverage.md`) |",
        "| Permanent ID coverage updated | YES (see `permanent_id_coverage_update.md`) |",
        "| Defect ledger produced | YES |",
        "| Survivorship safety status stated | YES — explicitly NOT SURVIVORSHIP-SAFE |",
        "| No strategy test / execution sim / performance metric produced | YES |",
        "",
        "## Hard locks (preserved)",
        "",
        "- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / execution sim /",
        "  production / paper / P08 / live / shadow.",
        "- No survivorship-safe claim.",
        "- No card is strategy-ready.",
        "- No credential committed.",
        "",
        "## Awaiting Referee",
        "",
        "Per Referee-defined exit conditions, Referee will decide whether to:",
        "- A. close as listed-universe source reconciled,",
        "- B. require another lifecycle reconciliation pass,",
        "- C. open executable-status source acquisition,",
        "- D. open ops NAV blocker patch,",
        "- E. keep all strategy research closed.",
        "",
    ]
    (OUT / "listed_universe_final_summary.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("[start] KR-LISTED-UNIVERSE-COVERAGE-A0")
    snapshots = acquire_monthly_snapshots()
    print(f"[snapshots] {len(snapshots)} rows; "
          f"{snapshots['ticker'].nunique()} unique tickers; "
          f"{snapshots['snapshot_date'].nunique()} snapshot dates")

    write_source_inventory()

    lc = build_lifecycle_coverage(snapshots)
    write_lifecycle_coverage_table(lc)

    panels = load_panel_tickers()
    recon_rows, summary = build_reconciliation(snapshots, panels)
    write_csv(OUT / "panel_vs_official_reconciliation_ledger.csv", recon_rows)
    print(f"[reconciliation] {summary['matched']} matched / "
          f"{summary['panel_only']} panel-only / "
          f"{summary['official_only']} official-only")

    write_official_source_report(snapshots)
    write_reconciliation_summary(summary)
    write_survivorship_assessment(summary, lc)
    write_permanent_id_update(lc, snapshots)
    write_delisted_merged_renamed(lc)

    defects = build_defect_ledger(recon_rows, lc, summary)
    write_csv(OUT / "listed_universe_defect_ledger.csv", defects)
    print(f"[defects] {len(defects)} defects")

    n_disappeared = int((lc.get("confidence_flag", "") == "disappeared_no_terminal").sum()) if "confidence_flag" in lc.columns else 0
    gate = write_gate_status(summary, len(defects), n_disappeared)
    write_final_summary(snapshots, summary, lc, len(defects), gate)

    print(json.dumps({
        "n_snapshots": int(snapshots["snapshot_date"].nunique()),
        "n_official_tickers": int(snapshots["ticker"].nunique()),
        "reconciliation": {
            "official_universe_size": summary["official_universe_size"],
            "union_panel_size": summary["union_panel_size"],
            "matched": summary["matched"],
            "panel_only": summary["panel_only"],
            "official_only": summary["official_only"],
        },
        "n_disappeared_no_terminal": n_disappeared,
        "n_defects": len(defects),
        "gate": gate,
    }, indent=2))


if __name__ == "__main__":
    main()
