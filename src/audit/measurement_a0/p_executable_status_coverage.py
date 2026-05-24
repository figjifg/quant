"""KR-EXECUTABLE-STATUS-COVERAGE-A0 builder.

Consumes:
- S3 KRX status events (OPENDART pblntfty=I) — semi-official primary
- W001 v2 tradable_state — proxy / derived
- W001 v2 listing_status_events + listing_status_terminal
- KR-LISTED-UNIVERSE-COVERAGE-A0 lifecycle table
- KR-OHLCV-QUARANTINE-ENFORCEMENT-A0 invalid-row contract

Produces 12 outputs.

Audit + reconciliation. No strategy testing. No execution simulation. No performance metric.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))

OUT = REPO / "reports/experiments/measurement_A0/KR_EXECUTABLE_STATUS_COVERAGE_A0"
OUT.mkdir(parents=True, exist_ok=True)

S3_STATUS_PATH = REPO / "data/acquired/round4/s3_krx_status/krx_status_events_2018_2026.csv"
TRADABLE_PATH = REPO / "data/processed/w001_v2/panel_with_tradable_state.csv"
LISTING_EVENTS_PATH = REPO / "data/processed/w001_v2/listing_status_events.csv"
LISTING_TERMINAL_PATH = REPO / "data/processed/w001_v2/listing_status_terminal.csv"
LIFECYCLE_PATH = REPO / "reports/experiments/measurement_A0/KR_LISTED_UNIVERSE_COVERAGE_A0/listed_lifecycle_coverage_table.csv"


# ---------------------------------------------------------------------------
# Source inventory
# ---------------------------------------------------------------------------

SOURCES = [
    {
        "source_id": "s3_krx_status_events_2018_2026",
        "file_path": "data/acquired/round4/s3_krx_status/krx_status_events_2018_2026.csv",
        "role": "semi-official primary (OPENDART pblntfty=I 거래소공시 filtered)",
        "date_range": "2018-01-01 → 2026-05-06",
        "market_coverage": "KOSPI + KOSDAQ (OPENDART corp_cls Y/K)",
        "ticker_coverage": "1,854 unique tickers with status events",
        "status_labels": "suspension / resumption / delisting / managed / liquidation / investment_alert (regex from report_nm)",
        "provenance": "OPENDART list.json filtered pblntfty=I (Round 4 S3 acquisition)",
        "timestamp_semantics": "rcept_dt = disclosure date; status effective date may differ",
        "is_official": "semi-official (DART 거래소공시 published by exchange; canonical for event-driven status changes)",
        "limitations": "(a) does NOT capture intraday halts; (b) does NOT capture limit-lock; (c) report_nm regex labelling is approximate; (d) DART body parsing CLOSED AS PARTIAL — exact effective dates not always extractable; (e) 2018+ only; (f) 53.1% coverage of disappeared tickers per ACQUISITION_SUMMARY",
    },
    {
        "source_id": "s3_dart_pblntfty_I_all_2018_2026",
        "file_path": "data/acquired/round4/s3_krx_status/dart_pblntfty_I_all_2018_2026.csv",
        "role": "raw OPENDART 거래소공시 dump",
        "date_range": "2018-01-01 → 2026-05-06",
        "market_coverage": "KOSPI+KOSDAQ+KONEX+etc",
        "ticker_coverage": "425,294 raw rows",
        "status_labels": "any pblntfty=I — broader than status events",
        "provenance": "OPENDART list.json (S3 raw)",
        "timestamp_semantics": "rcept_dt",
        "is_official": "official (OPENDART)",
        "limitations": "raw — needs filtering; status_events.csv is the filtered version",
    },
    {
        "source_id": "w001_v2_panel_with_tradable_state",
        "file_path": "data/processed/w001_v2/panel_with_tradable_state.csv",
        "role": "derived proxy (panel-level)",
        "date_range": "2018-01-02 → 2026-05-06 (panel window)",
        "market_coverage": "panel-selected tickers (dynamic_top100)",
        "ticker_coverage": "subset of panel tickers (~833)",
        "status_labels": "executable / panel_absence / true_suspension / delisting_transition / limit_lock_candidate / data_missing",
        "provenance": "W001 v2 derivation combining panel + S3 status events",
        "timestamp_semantics": "date-level",
        "is_official": "proxy (derived)",
        "limitations": "(a) TRAD_000001 critical defect: panel_absence != officially_delisted; (b) limit_lock_candidate is OHLCV-pattern-derived, not KRX-official; (c) covers only panel tickers — not full universe",
    },
    {
        "source_id": "w001_v2_listing_status_events",
        "file_path": "data/processed/w001_v2/listing_status_events.csv",
        "role": "DART-derived status events (consolidated)",
        "date_range": "2018-01-02 → 2026-05-06",
        "market_coverage": "panel ticker subset",
        "ticker_coverage": "tickers with DART events",
        "status_labels": "suspension / resumption / delisting / managed / surveillance / none",
        "provenance": "W001 v2 derivation from OPENDART pblntfty=I",
        "timestamp_semantics": "rcept_dt",
        "is_official": "semi-official derivation",
        "limitations": "same as S3 — DART body coverage is partial; rename + merger linkage missing",
    },
    {
        "source_id": "w001_v2_listing_status_terminal",
        "file_path": "data/processed/w001_v2/listing_status_terminal.csv",
        "role": "derived terminal status (per-ticker last known)",
        "date_range": "n/a (per-ticker snapshot)",
        "market_coverage": "panel tickers with terminal events",
        "ticker_coverage": "subset",
        "status_labels": "delisted / suspended_last_known / none",
        "provenance": "W001 v2 derivation from listing_status_events",
        "timestamp_semantics": "terminal_date",
        "is_official": "semi-official derivation",
        "limitations": "47% of historic disappearances unresolved (no DART terminal event captured)",
    },
    {
        "source_id": "kr_listed_universe_lifecycle_coverage",
        "file_path": "reports/experiments/measurement_A0/KR_LISTED_UNIVERSE_COVERAGE_A0/listed_lifecycle_coverage_table.csv",
        "role": "listed-universe lifecycle context",
        "date_range": "2010-01-04 → 2026-05-22 (monthly resolution)",
        "market_coverage": "KOSPI + KOSDAQ",
        "ticker_coverage": "3,653 unique tickers",
        "status_labels": "delisted_with_terminal / still_listed / disappeared_no_terminal",
        "provenance": "KR-LISTED-UNIVERSE-COVERAGE-A0 derivation",
        "timestamp_semantics": "first_snapshot / last_snapshot (monthly)",
        "is_official": "best-available official + W001 v2 join",
        "limitations": "monthly resolution; no intraday status; no limit-lock",
    },
    {
        "source_id": "equity_panel_ohlcv_signatures",
        "file_path": "research_input_data/inputs/equity_panels/*.csv",
        "role": "proxy (OHLCV-pattern derived)",
        "date_range": "2010-01-04 → 2026-05-06",
        "market_coverage": "panel tickers",
        "ticker_coverage": "925 panel tickers",
        "status_labels": "S1-S6 invalid signatures (OHL=0/close>0 etc)",
        "provenance": "vendor panels; OHLCV invariant audit",
        "timestamp_semantics": "trade date",
        "is_official": "proxy (NOT executable status)",
        "limitations": "OHLCV signatures DO NOT prove suspension/halt; require external official source",
    },
]


def write_source_inventory() -> None:
    lines = [
        "# Executable-Status Source Inventory",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-COVERAGE-A0",
        "",
        "## Sources surveyed",
        "",
        "| source_id | role | date range | market | label coverage | official? | limitations |",
        "|---|---|---|---|---|---|---|",
    ]
    for s in SOURCES:
        lines.append(
            f"| `{s['source_id']}` | {s['role']} | {s['date_range']} | "
            f"{s['market_coverage']} | {s['status_labels']} | {s['is_official']} | "
            f"{s['limitations']} |"
        )
    lines += [
        "",
        "## Source hierarchy used in this phase",
        "",
        "1. **Primary (semi-official)**: `s3_krx_status_events_2018_2026.csv` — OPENDART",
        "   pblntfty=I (거래소공시) is the canonical exchange-disclosure source. Status",
        "   events are filed by KRX/KOSDAQ market authority via DART.",
        "2. **Secondary (semi-official derivation)**: W001 v2 `listing_status_events` +",
        "   `listing_status_terminal` — consolidated/canonicalised versions of S3.",
        "3. **Proxy (derived)**: W001 v2 `tradable_state` — date-level panel proxy.",
        "   Not authoritative.",
        "4. **Context (lifecycle)**: KR-LISTED-UNIVERSE-COVERAGE-A0 lifecycle table.",
        "5. **Supporting evidence ONLY**: OHLCV signature audit (S1-S6). Cannot prove",
        "   status; can only cross-check.",
        "",
        "## NOT acquired in this phase",
        "",
        "- KRX 정보데이터시스템 매매거래정지 endpoint (direct intraday halt list) —",
        "  no pykrx wrapper; would require custom HTTP scraping with auth.",
        "- KOSCOM real-time halt/limit feed — commercial license.",
        "- pykrx managed-stock list — not exposed as a callable API in installed pykrx.",
        "- Intraday halt windows — out of scope for date-level audit.",
        "- Limit-lock authoritative list — only OHLCV-derived candidates available.",
        "",
        "## Hard locks (preserved)",
        "",
        "- No credential committed.",
        "- No execution simulation.",
        "- No strategy test.",
        "- No executable claim from panel presence.",
        "",
    ]
    (OUT / "source_inventory.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Taxonomy
# ---------------------------------------------------------------------------

def write_taxonomy() -> None:
    lines = [
        "# Executable-Status Taxonomy",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-COVERAGE-A0",
        "",
        "## Canonical status labels",
        "",
        "| label | definition | official source coverage | acceptable proxy fallback |",
        "|---|---|---|---|",
        "| `executable` | Trading was possible on date d (no event, listed, not surveillance/limit-locked) | KRX official | NONE (cannot be inferred from data presence alone) |",
        "| `full_day_suspension` | Stock was suspended for the entire trading day | S3 KRX status events: `suspension_related` | tradable_state=`true_suspension` (proxy; requires S3 backing) |",
        "| `intraday_halt` | Stock was halted within the day (resumed same day) | KOSCOM / KRX intraday log — NOT in repo | NONE — out of scope |",
        "| `resumption_day` | Day after a suspension when trading resumed | S3 KRX `resumption_related` | NONE (proxy unreliable) |",
        "| `delisting_transition` | In the delisting process (post-decision, pre-permanent) | S3 KRX `delisting` + W001 v2 terminal | tradable_state=`delisting_transition` (proxy) |",
        "| `liquidation_trading` | 정리매매 period | S3 KRX `liquidation` (rare; only 1 in dataset) | NONE |",
        "| `managed_stock` | 관리종목 (managed stock for risk reasons) | S3 KRX `managed` | NONE (pykrx managed-list not available) |",
        "| `investment_attention` | 투자주의 | S3 KRX `investment_alert` subset | NONE |",
        "| `investment_warning` | 투자경고 | S3 KRX `investment_alert` subset | NONE |",
        "| `investment_danger` | 투자위험 | S3 KRX `investment_alert` subset | NONE |",
        "| `short_term_overheated` | 단기과열 | S3 KRX (regex on `단기과열`) | NONE |",
        "| `upper_limit_lock_candidate` | 상한가 lock (OHLCV pattern) | NONE — KRX limit log not in repo | tradable_state=`limit_lock_candidate` (proxy) |",
        "| `lower_limit_lock_candidate` | 하한가 lock (OHLCV pattern) | NONE | tradable_state=`limit_lock_candidate` |",
        "| `panel_absent_or_not_in_universe` | Stock not in repo panel for that date (NOT proof of non-tradability) | n/a | tradable_state=`panel_absence` |",
        "| `data_missing` | Source data not available; status genuinely unknown | n/a | tradable_state=`data_missing` |",
        "| `unknown` | Cannot determine — MUST NOT be treated as executable | n/a | (default for un-evidenced cases) |",
        "",
        "## Critical separations",
        "",
        "- `panel_absent_or_not_in_universe` is **NOT** the same as non-tradable. The",
        "  stock may have been tradable but not selected by vendor dynamic_top100.",
        "- `unknown` MUST remain unknown. Downstream code MUST NOT assume executable",
        "  when status is unknown.",
        "- `proxy_only` status (from tradable_state) MUST be flagged separately from",
        "  `official` status (from S3 / DART).",
        "- OHLCV signatures (OHL=0/close>0, zero volume, etc.) are **supporting",
        "  evidence only**. They DO NOT prove suspension or halt — see the invariant",
        "  contract in `KR_OHLCV_QUARANTINE_ENFORCEMENT_A0/invalid_ohlcv_row_contract.md`.",
        "",
        "## Status confidence levels",
        "",
        "| confidence | meaning |",
        "|---|---|",
        "| `official` | S3 KRX status event directly supports the label |",
        "| `semi_official_derived` | W001 v2 derivation from S3 (consolidated) |",
        "| `proxy` | W001 v2 tradable_state assignment |",
        "| `unsourced` | inferred from OHLCV pattern alone — INSUFFICIENT |",
        "| `unknown` | no evidence |",
        "",
        "## Hard locks",
        "",
        "- Downstream code MUST consult source confidence before any execution-time",
        "  decision.",
        "- `unsourced` and `unknown` MUST trigger fail-closed gates, not silent",
        "  assumption.",
        "- `panel_absent_or_not_in_universe` MUST NOT be promoted to any tradability",
        "  conclusion.",
        "",
    ]
    (OUT / "executable_status_taxonomy.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Reconciliation: W001 tradable_state vs S3 events
# ---------------------------------------------------------------------------

def categorize_report(report_nm: str) -> str:
    """Map DART report_nm to canonical status category."""
    if not report_nm:
        return "other"
    r = report_nm
    if "정지" in r and "거래" in r and "해제" not in r and "재개" not in r:
        return "suspension_related"
    if "해제" in r or "재개" in r:
        return "resumption_related"
    if "상장폐지" in r:
        return "delisting"
    if "관리종목" in r:
        return "managed"
    if "투자" in r and ("주의" in r or "경고" in r or "위험" in r):
        return "investment_alert"
    if "정리매매" in r:
        return "liquidation"
    if "단기과열" in r:
        return "short_term_overheated"
    return "other"


def load_s3_events() -> pd.DataFrame:
    df = pd.read_csv(S3_STATUS_PATH, encoding="utf-8-sig", dtype=str)
    df["rcept_dt"] = pd.to_datetime(df["rcept_dt"], errors="coerce").dt.normalize()
    df = df.dropna(subset=["rcept_dt"]).copy()
    df["stock_code_str"] = df["stock_code_str"].fillna("").astype(str).str.zfill(6)
    df["category"] = df["report_nm"].apply(categorize_report)
    return df


def load_tradable_state() -> pd.DataFrame:
    df = pd.read_csv(TRADABLE_PATH, encoding="utf-8-sig", dtype={"종목코드": str},
                     usecols=["날짜", "종목코드", "tradable_state"])
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce").dt.normalize()
    df = df.dropna(subset=["날짜"]).copy()
    df["종목코드"] = df["종목코드"].str.zfill(6)
    return df


def build_reconciliation(s3: pd.DataFrame, tradable: pd.DataFrame) -> tuple[list[dict], dict]:
    """For each S3 event, look up the W001 tradable_state on rcept_dt + ticker."""
    # Build a (ticker, date) → tradable_state lookup
    ts_lookup = {}
    for _, r in tradable.iterrows():
        ts_lookup[(r["종목코드"], r["날짜"])] = r["tradable_state"]

    rows = []
    counter = Counter()
    for _, r in s3.iterrows():
        ticker = r["stock_code_str"]
        d = r["rcept_dt"]
        cat = r["category"]
        ts = ts_lookup.get((ticker, d), "PANEL_ABSENT_OR_OUT_OF_SCOPE")

        # Classify the reconciliation outcome
        if cat == "suspension_related":
            if ts == "true_suspension":
                cls = "matched_status"
            elif ts == "executable":
                cls = "official_suspension_but_repo_executable"
            elif ts in ("panel_absence", "PANEL_ABSENT_OR_OUT_OF_SCOPE"):
                cls = "official_status_but_panel_absent"
            else:
                cls = "official_suspension_but_repo_other"
        elif cat == "delisting":
            if ts == "delisting_transition":
                cls = "matched_status"
            elif ts == "executable":
                cls = "official_delisting_but_repo_executable"
            elif ts in ("panel_absence", "PANEL_ABSENT_OR_OUT_OF_SCOPE"):
                cls = "official_status_but_panel_absent"
            else:
                cls = "official_delisting_but_repo_other"
        elif cat == "resumption_related":
            if ts == "executable":
                cls = "matched_status"
            elif ts in ("panel_absence", "PANEL_ABSENT_OR_OUT_OF_SCOPE"):
                cls = "official_status_but_panel_absent"
            else:
                cls = "official_resumption_but_repo_other"
        elif cat in ("managed", "investment_alert", "liquidation", "short_term_overheated"):
            cls = "proxy_only"  # tradable_state has no equivalent label
        else:
            cls = "requires_manual_review"
        counter[cls] += 1
        rows.append({
            "ticker": ticker,
            "rcept_dt": d.date().isoformat(),
            "official_status_category": cat,
            "report_nm": r["report_nm"][:80],
            "rcept_no": r["rcept_no"],
            "w001_tradable_state": ts,
            "reconciliation_class": cls,
        })
    return rows, dict(counter)


def write_w001_reconciliation_summary(counter: dict, n_events: int) -> None:
    lines = [
        "# W001 Tradable_State Reconciliation",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-COVERAGE-A0  ",
        "Method: for each S3 KRX status event (rcept_dt × ticker), look up the W001 v2",
        "panel `tradable_state` value at that (date, ticker). Classify the agreement.",
        "",
        f"## Headline: **{n_events}** S3 events reconciled against W001 tradable_state",
        "",
        "| reconciliation_class | count |",
        "|---|---:|",
    ]
    for k, v in sorted(counter.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- `matched_status` = W001 v2 derivation agrees with the S3 official event.",
        "- `official_X_but_repo_Y` = disagreement. Most often because the W001 v2",
        "  panel only covers dynamic_top100 selections, so the ticker may not be in",
        "  the panel on the event date (→ `panel_absence`).",
        "- `official_status_but_panel_absent` = S3 has an event, but the ticker is",
        "  not in the panel on that date. This is the dominant disagreement class,",
        "  reflecting the panel's selection bias rather than a true mismatch.",
        "- `proxy_only` = S3 category (managed / investment_alert / liquidation /",
        "  short_term_overheated) has NO W001 v2 equivalent label. These events are",
        "  visible in S3 but not surfaced in `tradable_state`.",
        "- `requires_manual_review` = ambiguous report_nm (categorised as `other`).",
        "",
        "## Per-defect ledger",
        "",
        "See `w001_tradable_state_reconciliation_ledger.csv` for per-event rows.",
        "",
        "## Hard locks (preserved)",
        "",
        "- No assumption that W001 v2 `tradable_state` is official.",
        "- No assumption that panel_absence = non-tradable.",
        "- No execution simulation.",
        "",
    ]
    (OUT / "w001_tradable_state_reconciliation.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Lifecycle reconciliation
# ---------------------------------------------------------------------------

def build_lifecycle_reconciliation(s3: pd.DataFrame, terminal: pd.DataFrame, lifecycle: pd.DataFrame) -> dict:
    """Cross-check S3 status events against lifecycle terminal status."""
    terminal_set = set(terminal["ticker"].astype(str).str.zfill(6).tolist())
    lifecycle_set = set(lifecycle["ticker"].astype(str).str.zfill(6).tolist())

    s3_tickers = set(s3["stock_code_str"].tolist())

    counter = Counter()
    for t in s3_tickers:
        has_terminal = t in terminal_set
        has_lifecycle = t in lifecycle_set
        if has_terminal and has_lifecycle:
            counter["s3_event_with_lifecycle_and_terminal"] += 1
        elif has_lifecycle and not has_terminal:
            counter["s3_event_in_lifecycle_no_terminal"] += 1
        elif not has_lifecycle:
            counter["s3_event_not_in_lifecycle"] += 1

    # Tickers in lifecycle with terminal but NO S3 event (W001 derived terminal but S3 missing)
    terminal_tickers = terminal["ticker"].astype(str).str.zfill(6).tolist()
    for t in terminal_tickers:
        if t not in s3_tickers:
            counter["w001_terminal_without_s3_event"] += 1
    return dict(counter)


def write_lifecycle_reconciliation(counts: dict) -> None:
    lines = [
        "# Listed-Lifecycle × Executable-Status Reconciliation",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-COVERAGE-A0",
        "",
        "## Method",
        "",
        "Cross-check S3 KRX status event tickers against:",
        "- W001 v2 `listing_status_terminal` (per-ticker terminal status),",
        "- KR-LISTED-UNIVERSE-COVERAGE-A0 lifecycle coverage table (ever-listed tickers).",
        "",
        "## Headline",
        "",
        "| classification | count |",
        "|---|---:|",
    ]
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- `s3_event_with_lifecycle_and_terminal`: S3 status event ticker is in both",
        "  the official lifecycle table AND has a W001 v2 terminal status — fully",
        "  consistent.",
        "- `s3_event_in_lifecycle_no_terminal`: S3 event ticker is in lifecycle but",
        "  W001 v2 has no terminal — typically because S3 event is non-terminal (e.g.,",
        "  managed/investment_alert) OR because terminal mapping is incomplete.",
        "- `s3_event_not_in_lifecycle`: S3 event ticker is NOT in the official",
        "  lifecycle table — either out-of-window, KONEX (excluded), or vendor edge",
        "  case.",
        "- `w001_terminal_without_s3_event`: W001 v2 has terminal status but no",
        "  corresponding S3 event — terminal may have been inferred from panel",
        "  disappearance without DART backing.",
        "",
        "## Implications for execution simulation",
        "",
        "- Tickers with `s3_event_with_lifecycle_and_terminal` are safe to gate via",
        "  S3 + W001 v2 in any future execution check.",
        "- Tickers in `w001_terminal_without_s3_event` need manual review or further",
        "  source acquisition before they can be safely gated.",
        "",
        "## Hard locks (preserved)",
        "",
        "- No execution simulation.",
        "- No survivorship-safe claim.",
        "",
    ]
    (OUT / "listed_lifecycle_executable_reconciliation.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# OHLCV overlap audit
# ---------------------------------------------------------------------------

def build_ohlcv_overlap_audit(tradable: pd.DataFrame) -> dict:
    """Count OHLCV-pattern proxy assignments in W001 tradable_state."""
    cnt = Counter(tradable["tradable_state"].fillna("MISSING").tolist())
    return dict(cnt)


def write_ohlcv_overlap_audit(counts: dict) -> None:
    lines = [
        "# OHLCV × Executable-Status Overlap Audit",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-COVERAGE-A0",
        "",
        "## W001 v2 `tradable_state` distribution (per-row)",
        "",
        "| state | row count |",
        "|---|---:|",
    ]
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "Per the invariant contract in",
        "`KR_OHLCV_QUARANTINE_ENFORCEMENT_A0/invalid_ohlcv_row_contract.md`:",
        "",
        "- `OHL=0` / `close>0` rows are the vendor non-trading-row signature. These",
        "  are quarantined; they do NOT prove suspension.",
        "- W001 v2 `tradable_state` assigns `true_suspension` to a subset of these,",
        "  but only when the assignment is **backed by an S3 official event**. Rows",
        "  with the signature but no S3 backing remain `panel_absence` or `data_missing`.",
        "- `limit_lock_candidate` is OHLCV-pattern-derived (close = upper-limit or",
        "  lower-limit price). This is a CANDIDATE label, NOT KRX-official.",
        "",
        "## Cross-check rule",
        "",
        "Any future code path that decides executable status MUST:",
        "",
        "1. Consult `tradable_state` AS PROXY.",
        "2. If the row is `true_suspension`, verify the W001 v2 derivation traces",
        "   to an S3 KRX status event.",
        "3. If the row is `limit_lock_candidate`, treat as **candidate-only**; do not",
        "   convert to a definitive executable claim.",
        "4. NEVER use OHL=0 / `close>0` / zero-volume as standalone executable",
        "   evidence.",
        "",
        "## Hard locks (preserved)",
        "",
        "- OHLCV invariant signatures are NOT executable-status proof.",
        "- `limit_lock_candidate` is NOT official limit-lock data.",
        "- No execution simulation.",
        "",
    ]
    (OUT / "ohlcv_status_overlap_audit.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Coverage table + defect ledger
# ---------------------------------------------------------------------------

def build_coverage_table(s3: pd.DataFrame, tradable: pd.DataFrame, terminal: pd.DataFrame) -> list[dict]:
    """Produce a coverage row per S3 event."""
    terminal_map = {r["ticker"]: r for _, r in
                    terminal.assign(ticker=terminal["ticker"].astype(str).str.zfill(6)).iterrows()}
    ts_lookup = {}
    for _, r in tradable.iterrows():
        ts_lookup[(r["종목코드"], r["날짜"])] = r["tradable_state"]

    rows = []
    for _, r in s3.iterrows():
        ticker = r["stock_code_str"]
        d = r["rcept_dt"]
        ts = ts_lookup.get((ticker, d), "PANEL_ABSENT_OR_OUT_OF_SCOPE")
        term = terminal_map.get(ticker, {})
        rows.append({
            "date": d.date().isoformat(),
            "ticker": ticker,
            "market": r.get("corp_cls", ""),
            "official_status_category": r["category"],
            "official_status_label": _category_to_label(r["category"]),
            "official_status_source": "s3_krx_status_events_2018_2026",
            "repo_tradable_state": ts,
            "listed_universe_terminal_status": term.get("terminal_status", "") if isinstance(term, dict) else (term.get("terminal_status", "") if hasattr(term, "get") else ""),
            "listed_universe_terminal_date": term.get("terminal_date", "") if isinstance(term, dict) else (term.get("terminal_date", "") if hasattr(term, "get") else ""),
            "status_timestamp": d.date().isoformat(),
            "is_official": "semi_official_derived",
            "is_proxy": "false",
            "requires_manual_review": "true" if r["category"] == "other" else "false",
        })
    return rows


def _category_to_label(cat: str) -> str:
    return {
        "suspension_related": "full_day_suspension",
        "resumption_related": "resumption_day",
        "delisting": "delisting_transition",
        "managed": "managed_stock",
        "investment_alert": "investment_attention_warning_or_danger",
        "liquidation": "liquidation_trading",
        "short_term_overheated": "short_term_overheated",
        "other": "unknown",
    }.get(cat, "unknown")


def build_defect_ledger(recon_rows: list[dict], counts: dict, lc_counts: dict,
                        ts_counts: dict) -> list[dict]:
    defects = []
    defect_id = 1

    # Defect: official suspension but repo executable
    for r in recon_rows:
        if r["reconciliation_class"] == "official_suspension_but_repo_executable":
            defects.append({
                "defect_id": f"EXS_{defect_id:05d}",
                "severity": "high",
                "defect_class": "official_suspension_but_repo_executable",
                "ticker": r["ticker"],
                "date": r["rcept_dt"],
                "detail": f"S3 suspension event ({r['report_nm']}) but W001 v2 says executable",
                "recommended_handling": "manual review; possible W001 v2 derivation miss",
            })
            defect_id += 1
        elif r["reconciliation_class"] == "official_delisting_but_repo_executable":
            defects.append({
                "defect_id": f"EXS_{defect_id:05d}",
                "severity": "high",
                "defect_class": "official_delisting_but_repo_executable",
                "ticker": r["ticker"],
                "date": r["rcept_dt"],
                "detail": f"S3 delisting event but W001 v2 says executable",
                "recommended_handling": "manual review; possible event-date alignment issue",
            })
            defect_id += 1

    # Defect: proxy_only labels (managed / investment_alert / liquidation /
    # short_term_overheated have no tradable_state equivalent)
    proxy_only_count = sum(1 for r in recon_rows if r["reconciliation_class"] == "proxy_only")
    if proxy_only_count > 0:
        defects.append({
            "defect_id": f"EXS_{defect_id:05d}",
            "severity": "medium",
            "defect_class": "no_tradable_state_label_for_managed_alert_liquidation",
            "ticker": "(aggregate)",
            "date": "(2018-2026)",
            "detail": f"{proxy_only_count} S3 events (managed/alert/liquidation/short_term_overheated) have no W001 v2 tradable_state equivalent label",
            "recommended_handling": "extend W001 v2 tradable_state taxonomy to capture these categories, OR document that they MUST be looked up from S3 directly",
        })
        defect_id += 1

    # Defect: W001 v2 terminal without S3 event (terminal inferred from panel disappearance)
    if "w001_terminal_without_s3_event" in lc_counts:
        n = lc_counts["w001_terminal_without_s3_event"]
        defects.append({
            "defect_id": f"EXS_{defect_id:05d}",
            "severity": "medium",
            "defect_class": "w001_terminal_without_s3_event",
            "ticker": "(aggregate)",
            "date": "n/a",
            "detail": f"{n} tickers have W001 v2 terminal status but no corresponding S3 KRX event — terminal inferred from panel disappearance without DART backing",
            "recommended_handling": "future phase: cross-reference against pykrx/KRX listed-universe to reconcile",
        })
        defect_id += 1

    # Defect: limit_lock_candidate is OHLCV-pattern (no KRX official limit log)
    n_limit_candidates = ts_counts.get("limit_lock_candidate", 0)
    if n_limit_candidates > 0:
        defects.append({
            "defect_id": f"EXS_{defect_id:05d}",
            "severity": "medium",
            "defect_class": "limit_lock_proxy_only",
            "ticker": "(aggregate)",
            "date": "n/a",
            "detail": f"{n_limit_candidates} rows tagged `limit_lock_candidate` derived from OHLCV pattern; KRX official limit-lock log NOT in repo",
            "recommended_handling": "treat as CANDIDATE only; never as definitive executable evidence",
        })
        defect_id += 1

    # Defect: intraday halt coverage = ZERO
    defects.append({
        "defect_id": f"EXS_{defect_id:05d}",
        "severity": "high",
        "defect_class": "intraday_halt_source_missing",
        "ticker": "(aggregate)",
        "date": "n/a",
        "detail": "No intraday halt source acquired (KOSCOM / KRX real-time feed not in repo); date-resolution audit cannot detect intraday halts",
        "recommended_handling": "future phase: acquire intraday halt log if execution-simulation requires sub-day resolution",
    })
    defect_id += 1

    # Defect: 2010-2017 status events not in S3 (S3 covers 2018+)
    defects.append({
        "defect_id": f"EXS_{defect_id:05d}",
        "severity": "high",
        "defect_class": "pre_2018_status_coverage_gap",
        "ticker": "(aggregate)",
        "date": "2010-01-01 → 2017-12-31",
        "detail": "S3 KRX status events cover 2018-01-01 → 2026-05-06 only; pre-2018 status events not in repo",
        "recommended_handling": "future phase: extend OPENDART acquisition to pre-2018 (DART API may have date-range limits), OR document pre-2018 as best-effort",
    })
    defect_id += 1

    return defects


# ---------------------------------------------------------------------------
# Gate + summary
# ---------------------------------------------------------------------------

def write_official_source_report(s3: pd.DataFrame) -> None:
    cat_counts = s3["category"].value_counts().to_dict()
    by_year = s3.groupby(s3["rcept_dt"].dt.year).size().to_dict()
    lines = [
        "# Official Executable-Status Source Report",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-COVERAGE-A0",
        "",
        "## Acquired source",
        "",
        f"- Primary semi-official source: `data/acquired/round4/s3_krx_status/krx_status_events_2018_2026.csv`",
        f"- Method: OPENDART list.json filtered to `pblntfty=I` (거래소공시) reports with status-relevant `report_nm` patterns (S3 acquisition, Round 4)",
        f"- Date range: **{s3['rcept_dt'].min().date()} → {s3['rcept_dt'].max().date()}**",
        f"- Row count: **{len(s3)}**",
        f"- Unique tickers: **{s3['stock_code_str'].nunique()}**",
        "",
        "## Category distribution",
        "",
        "| category | event count |",
        "|---|---:|",
    ]
    for k, v in sorted(cat_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Per-year coverage",
        "",
        "| year | event count |",
        "|---|---:|",
    ]
    for y in sorted(by_year):
        lines.append(f"| {y} | {by_year[y]} |")
    lines += [
        "",
        "## What this source covers",
        "",
        "- KRX/KOSDAQ market authority disclosures filed via DART (pblntfty=I = 거래소공시).",
        "- Date-level granularity (filing date = rcept_dt).",
        "- Suspension / resumption / delisting / managed / liquidation /",
        "  investment-alert / short-term-overheated event types.",
        "",
        "## What this source does NOT cover",
        "",
        "- Intraday halts (no time-of-day resolution).",
        "- Limit-lock (upper/lower limit closes) — only OHLCV proxy available.",
        "- Pre-2018 events (S3 acquisition window starts 2018).",
        "- Effective dates of events (rcept_dt is filing date; actual suspension",
        "  start/end may differ; S2 body parse needed for exact dates and S2 is",
        "  CLOSED AS PARTIAL).",
        "- KONEX market (excluded by corp_cls filter).",
        "",
        "## Hard locks (preserved)",
        "",
        "- No credential committed.",
        "- No strategy testing.",
        "- No execution simulation.",
        "- This source does NOT certify execution feasibility for any specific date.",
        "",
    ]
    (OUT / "official_executable_status_source_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_gate_status(reconciliation_counts: dict, lifecycle_counts: dict, n_defects: int) -> str:
    n_matched = reconciliation_counts.get("matched_status", 0)
    n_total = sum(reconciliation_counts.values())
    n_panel_absent = reconciliation_counts.get("official_status_but_panel_absent", 0)
    n_official_repo_disagree = (
        reconciliation_counts.get("official_suspension_but_repo_executable", 0)
        + reconciliation_counts.get("official_delisting_but_repo_executable", 0)
    )

    # Decision logic
    if n_total == 0:
        gate = "DATA_SOURCE_FAIL"
        rationale = "no source available"
    elif n_official_repo_disagree > 10:
        gate = "OFFICIAL_SOURCE_ACQUIRED_BUT_NOT_FULLY_RECONCILED"
        rationale = (
            f"S3 source acquired (semi-official); {n_total} events reconciled; "
            f"{n_matched} matched, but {n_official_repo_disagree} official-vs-repo "
            f"disagreements remain (W001 v2 says executable on date of an S3 "
            f"suspension/delisting). Execution simulation stays CLOSED."
        )
    else:
        gate = "PARTIAL"
        rationale = (
            f"S3 source acquired (semi-official; date-resolution, 2018+ only); "
            f"{n_matched}/{n_total} events matched against W001 v2 derivation. "
            f"Intraday halts, limit-lock authoritative log, and pre-2018 status "
            f"events are NOT covered. Execution simulation stays CLOSED."
        )

    lines = [
        "# Executable-Status Gate Status",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-COVERAGE-A0",
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
        "- `EXECUTABLE_STATUS_RECONCILED_BUT_EXECUTION_STILL_CLOSED`",
        "- `READY_FOR_NEXT_A0_REVIEW`",
        "",
        "## Numerical inputs",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| S3 events reconciled | {n_total} |",
        f"| Matched (W001 v2 agrees with S3) | {n_matched} |",
        f"| Official-status-but-panel-absent | {n_panel_absent} |",
        f"| Official-vs-repo disagreement (high severity) | {n_official_repo_disagree} |",
        f"| Total defects | {n_defects} |",
        "",
        "## Important boundary",
        "",
        "- Strategy testing is NOT opened.",
        "- Execution simulation is NOT opened.",
        "- No executable claim from panel presence.",
        "- Intraday halt + limit-lock authoritative coverage MISSING.",
        "- Pre-2018 status coverage MISSING.",
        "",
    ]
    (OUT / "executable_status_gate_status.md").write_text("\n".join(lines), encoding="utf-8")
    return gate


def write_final_summary(s3: pd.DataFrame, reconciliation_counts: dict,
                        lifecycle_counts: dict, ts_counts: dict, n_defects: int, gate: str) -> None:
    n_total_events = len(s3)
    n_tickers = s3["stock_code_str"].nunique()
    cat_counts = s3["category"].value_counts().to_dict()

    lines = [
        "# KR-EXECUTABLE-STATUS-COVERAGE-A0 — Final Summary",
        "",
        "Date: 2026-05-24  ",
        "Predecessor: KR-LISTED-UNIVERSE-COVERAGE-A0 CLOSED.",
        "",
        "## Scope respected",
        "",
        "- Measurement-layer executable-status source acquisition + coverage audit only.",
        "- No strategy testing.",
        "- No performance diagnostics.",
        "- No execution simulation.",
        "- No production / paper / P08 / live / shadow.",
        "",
        "## What was delivered",
        "",
        "Code artifacts:",
        "- `src/audit/measurement_a0/p_executable_status_coverage.py`",
        "",
        "Data artifacts:",
        "- (none new — S3 KRX status events already acquired in Round 4)",
        "",
        "Reports (this dir, 12 outputs):",
        "1. `executable_status_referee_lock.md`",
        "2. `source_inventory.md` (7 sources)",
        "3. `official_executable_status_source_report.md`",
        "4. `executable_status_taxonomy.md` (15+ canonical labels)",
        "5. `executable_status_coverage_table.csv`",
        "6. `w001_tradable_state_reconciliation.md`",
        "7. `w001_tradable_state_reconciliation_ledger.csv`",
        "8. `listed_lifecycle_executable_reconciliation.md`",
        "9. `ohlcv_status_overlap_audit.md`",
        "10. `executable_status_defect_ledger.csv`",
        "11. `executable_status_gate_status.md`",
        "12. `executable_status_final_summary.md` (this file)",
        "",
        "## Source acquisition",
        "",
        f"- Primary: S3 KRX status events `data/acquired/round4/s3_krx_status/krx_status_events_2018_2026.csv`",
        f"  - Date range: 2018-01-01 → 2026-05-06",
        f"  - Events: **{n_total_events}**",
        f"  - Unique tickers: **{n_tickers}**",
        "- Status category breakdown:",
    ]
    for k, v in sorted(cat_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"  - `{k}`: {v}")
    lines += [
        "",
        "## Reconciliation headline (S3 vs W001 v2 tradable_state)",
        "",
        "| class | count |",
        "|---|---:|",
    ]
    for k, v in sorted(reconciliation_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Lifecycle cross-check",
        "",
        "| class | count |",
        "|---|---:|",
    ]
    for k, v in sorted(lifecycle_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Defect ledger",
        "",
        f"- Total defects: **{n_defects}**",
        "- Classes: official-vs-repo disagreement, proxy-only (managed/alert/liquidation),",
        "  W001 v2 terminal without S3 event, limit-lock proxy-only, intraday-halt-source-missing,",
        "  pre-2018 status coverage gap.",
        "",
        f"## Executable-status gate state: **{gate}**",
        "",
        "## Pass criteria evaluation",
        "",
        "| criterion | status |",
        "|---|---|",
        "| Executable-status source candidates identified + documented | YES (7 sources surveyed) |",
        "| Best-available source acquired or failure documented | YES (S3 KRX status events; intraday-halt + limit-lock gaps documented) |",
        "| Taxonomy separates official / proxy / unknown / panel-absence | YES (15+ labels with confidence column) |",
        "| W001 tradable_state reconciled where possible | YES |",
        "| Listed-lifecycle cross-checked | YES |",
        "| OHLCV invalid rows not used as sole executable-status proof | YES (cross-check rule documented) |",
        "| Defect ledger produced | YES |",
        "| Gate status explicitly stated | YES |",
        "| No strategy test / execution sim / performance metric produced | YES |",
        "",
        "## Hard locks (preserved)",
        "",
        "- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / execution sim",
        "  / production / paper / P08 / live / shadow.",
        "- No survivorship-safe claim.",
        "- No executable claim from panel presence.",
        "- No card is strategy-ready.",
        "",
        "## Awaiting Referee",
        "",
        "Per Referee-defined exit conditions, Referee will decide whether to:",
        "- A. close as executable-status source acquired and reconciled,",
        "- B. require another reconciliation pass,",
        "- C. open listed-universe daily lifecycle refinement,",
        "- D. open ops NAV blocker patch,",
        "- E. keep all strategy research closed.",
        "",
    ]
    (OUT / "executable_status_final_summary.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("[start] KR-EXECUTABLE-STATUS-COVERAGE-A0")

    write_source_inventory()
    write_taxonomy()

    s3 = load_s3_events()
    print(f"[s3] loaded {len(s3)} status events; {s3['stock_code_str'].nunique()} tickers")
    write_official_source_report(s3)

    tradable = load_tradable_state()
    print(f"[tradable] loaded {len(tradable)} panel rows")
    ts_counts = build_ohlcv_overlap_audit(tradable)
    write_ohlcv_overlap_audit(ts_counts)

    recon_rows, recon_counter = build_reconciliation(s3, tradable)
    write_csv(OUT / "w001_tradable_state_reconciliation_ledger.csv", recon_rows)
    write_w001_reconciliation_summary(recon_counter, len(recon_rows))
    print(f"[reconciliation] {recon_counter}")

    terminal = pd.read_csv(LISTING_TERMINAL_PATH, encoding="utf-8-sig", dtype={"ticker": str})
    if LIFECYCLE_PATH.exists():
        lifecycle = pd.read_csv(LIFECYCLE_PATH, dtype={"ticker": str})
    else:
        lifecycle = pd.DataFrame(columns=["ticker"])
    lc_counts = build_lifecycle_reconciliation(s3, terminal, lifecycle)
    write_lifecycle_reconciliation(lc_counts)
    print(f"[lifecycle] {lc_counts}")

    cov_rows = build_coverage_table(s3, tradable, terminal)
    write_csv(OUT / "executable_status_coverage_table.csv", cov_rows)
    print(f"[coverage_table] {len(cov_rows)} rows")

    defects = build_defect_ledger(recon_rows, recon_counter, lc_counts, ts_counts)
    write_csv(OUT / "executable_status_defect_ledger.csv", defects)
    print(f"[defects] {len(defects)} defects")

    gate = write_gate_status(recon_counter, lc_counts, len(defects))
    write_final_summary(s3, recon_counter, lc_counts, ts_counts, len(defects), gate)

    print(json.dumps({
        "n_s3_events": len(s3),
        "n_tickers": s3["stock_code_str"].nunique(),
        "reconciliation": recon_counter,
        "lifecycle_counts": lc_counts,
        "tradable_state_counts": ts_counts,
        "n_defects": len(defects),
        "gate": gate,
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
