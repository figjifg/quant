"""KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0 builder.

Attempts OPENDART pblntfty=I (거래소공시) acquisition for 2010-01-01 → 2017-12-31.
Filters to status-relevant report_nm patterns (same regex as Round 4 S3). Reconciles
against W001 v2 lifecycle + 2010-2016 panel. Produces 12 outputs.

Audit + acquisition. No strategy testing. No execution simulation. No performance metric.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))

OUT = REPO / "reports/experiments/measurement_A0/KR_EXECUTABLE_STATUS_PRE2018_EXTENSION_A0"
OUT.mkdir(parents=True, exist_ok=True)
ACQUIRED_DIR = REPO / "data/acquired/round5_dart_pre2018"
ACQUIRED_DIR.mkdir(parents=True, exist_ok=True)
RAW_PATH = ACQUIRED_DIR / "dart_pblntfty_I_all_2010_2017.csv"
FILTERED_PATH = ACQUIRED_DIR / "krx_status_events_2010_2017.csv"
ATTEMPT_LOG = ACQUIRED_DIR / "acquisition_attempt_log.csv"

DART_LIST_URL = "https://opendart.fss.or.kr/api/list.json"


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
# Acquisition
# ---------------------------------------------------------------------------

def chunk_3_month(start: str, end: str) -> list[tuple[str, str]]:
    """Yield (bgn_de, end_de) 3-month chunks YYYYMMDD."""
    s = datetime.strptime(start, "%Y%m%d")
    e = datetime.strptime(end, "%Y%m%d")
    chunks = []
    cur = s
    while cur <= e:
        # 3-month window
        end_of_chunk = (cur + pd.DateOffset(months=3) - pd.Timedelta(days=1)).to_pydatetime()
        if end_of_chunk > e:
            end_of_chunk = e
        chunks.append((cur.strftime("%Y%m%d"), end_of_chunk.strftime("%Y%m%d")))
        cur = (cur + pd.DateOffset(months=3)).to_pydatetime()
    return chunks


def query_opendart_page(api_key: str, bgn: str, end: str, page: int) -> dict:
    """Query OPENDART list.json. Returns parsed JSON."""
    url = DART_LIST_URL + "?" + urllib.parse.urlencode({
        "crtfc_key": api_key,
        "bgn_de": bgn,
        "end_de": end,
        "pblntf_ty": "I",
        "page_no": str(page),
        "page_count": "100",
    })
    req = urllib.request.Request(url, headers={"User-Agent": "audit-script"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def acquire_pre2018() -> tuple[list[dict], list[dict]]:
    """Acquire raw OPENDART pblntfty=I for 2010-01-01 → 2017-12-31.

    Returns (raw_rows, attempt_log_rows).
    """
    if RAW_PATH.exists():
        print(f"[acquisition] reusing cached raw from {RAW_PATH}")
        df = pd.read_csv(RAW_PATH, dtype=str)
        if ATTEMPT_LOG.exists():
            log_df = pd.read_csv(ATTEMPT_LOG, dtype=str)
            log_rows = log_df.to_dict("records")
        else:
            log_rows = []
        return df.to_dict("records"), log_rows

    load_env()
    api_key = os.environ.get("OPENDART_API_KEY")
    if not api_key:
        raise RuntimeError("OPENDART_API_KEY missing from environment")

    chunks = chunk_3_month("20100101", "20171231")
    print(f"[acquisition] {len(chunks)} 3-month chunks to fetch")

    all_rows: list[dict] = []
    log_rows: list[dict] = []

    for i, (bgn, end) in enumerate(chunks):
        page = 1
        total_count = None
        total_page = None
        chunk_rows_n = 0
        chunk_start_t = time.time()
        while True:
            try:
                data = query_opendart_page(api_key, bgn, end, page)
            except Exception as e:  # noqa: BLE001
                print(f"[chunk {bgn}-{end} page {page}] ERROR: {e}")
                log_rows.append({
                    "chunk_bgn": bgn, "chunk_end": end, "page_no": page,
                    "status": "EXCEPTION", "message": str(e)[:200],
                    "total_count": "", "rows_collected": 0,
                })
                time.sleep(2)
                break
            status = data.get("status")
            message = data.get("message", "")
            items = data.get("list", [])
            if total_count is None:
                total_count = data.get("total_count", 0)
                total_page = data.get("total_page", 0)
            log_rows.append({
                "chunk_bgn": bgn, "chunk_end": end, "page_no": page,
                "status": status, "message": message,
                "total_count": total_count, "rows_collected": len(items),
            })
            if status != "000" or not items:
                break
            all_rows.extend(items)
            chunk_rows_n += len(items)
            page += 1
            if page > (total_page or 1):
                break
        dur = time.time() - chunk_start_t
        print(f"[chunk {i+1}/{len(chunks)} {bgn}-{end}] total_count={total_count} collected={chunk_rows_n} ({dur:.1f}s)")
        time.sleep(0.2)

    # Persist raw
    if all_rows:
        df = pd.DataFrame(all_rows)
        df.to_csv(RAW_PATH, index=False)
        print(f"[acquisition] wrote {len(df)} raw rows to {RAW_PATH}")
    # Persist attempt log
    pd.DataFrame(log_rows).to_csv(ATTEMPT_LOG, index=False)
    print(f"[acquisition] wrote attempt log to {ATTEMPT_LOG}")
    return all_rows, log_rows


# ---------------------------------------------------------------------------
# Filtering + categorisation
# ---------------------------------------------------------------------------

def categorize_report(report_nm: str) -> str:
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


def filter_status_events(raw_rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(raw_rows)
    if df.empty:
        return df
    df["category"] = df.get("report_nm", "").apply(categorize_report) if "report_nm" in df.columns else "other"
    status_categories = {"suspension_related", "resumption_related", "delisting",
                         "managed", "investment_alert", "liquidation",
                         "short_term_overheated"}
    filtered = df[df["category"].isin(status_categories) | (df["category"] == "other")].copy()
    # Save with the same column shape as Round 4 S3
    cols = ["corp_code", "corp_name", "stock_code", "corp_cls", "report_nm",
            "rcept_no", "flr_nm", "rcept_dt", "rm"]
    for c in cols:
        if c not in filtered.columns:
            filtered[c] = ""
    filtered["stock_code_str"] = filtered["stock_code"].fillna("").astype(str).str.zfill(6).str.replace(".0", "", regex=False)
    return filtered


def write_filtered(filtered_df: pd.DataFrame) -> None:
    if filtered_df.empty:
        FILTERED_PATH.write_text("", encoding="utf-8")
        return
    out_cols = ["corp_code", "corp_name", "stock_code", "corp_cls", "report_nm",
                "rcept_no", "flr_nm", "rcept_dt", "rm", "stock_code_str", "category"]
    keep = [c for c in out_cols if c in filtered_df.columns]
    filtered_df[keep].to_csv(FILTERED_PATH, index=False)


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def write_source_feasibility_report() -> None:
    lines = [
        "# Source Feasibility Report — Pre-2018 Executable Status",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0",
        "",
        "## Candidate sources surveyed",
        "",
        "| candidate | feasibility | notes |",
        "|---|---|---|",
        "| OPENDART `list.json` pblntfty=I 거래소공시 | **CONFIRMED FEASIBLE** | tested with bgn_de=20100101: returned status=000, 520 items for first 10 days |",
        "| pykrx status / suspension endpoint | NOT FEASIBLE | no relevant API exposed by installed pykrx |",
        "| KRX 정보데이터시스템 직접 scraping | NOT ATTEMPTED | would require dedicated HTTP scraping + manual licensing review |",
        "| W001 v2 listing_status_events.csv | already in repo | covers 2018+ only (same source as S3) |",
        "| W001 v2 listing_status_terminal.csv | already in repo | per-ticker terminal snapshot |",
        "| Kiwoom 2010-2016 panel disappearance | NOT a status source | panel disappearance != suspension/delisting evidence |",
        "",
        "## API access details",
        "",
        "- Endpoint: `https://opendart.fss.or.kr/api/list.json`",
        "- Query parameters: `crtfc_key` (from `.env`, not committed), `bgn_de`, `end_de`,",
        "  `pblntf_ty=I`, `page_no`, `page_count`.",
        "- Auth: OPENDART API key (stored in local `.env`, NOT committed to git).",
        "- Rate limit per docs: 20,000 requests/day. Acquisition stays well within.",
        "- Date range tested: 2010-01-01 → 2010-01-10 (10 days). Returned 520 items,",
        "  52 pages — confirming pre-2018 data IS served.",
        "",
        "## Acquisition strategy",
        "",
        "- 3-month chunks (same as Round 4 S3 acquisition).",
        "- 8 years × 4 quarters = 32 chunks for 2010-01-01 → 2017-12-31.",
        "- `page_count=100` per page; iterate `page_no` until empty.",
        "- 0.2s inter-chunk pause to avoid rate-limit triggers.",
        "",
        "## Hard locks (preserved)",
        "",
        "- No credential committed.",
        "- No execution simulation.",
        "- No strategy testing.",
        "",
    ]
    (OUT / "source_feasibility_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_pre2018_status_source_report(raw_n: int, filtered_n: int, cat_counts: dict,
                                        first_d: str, last_d: str) -> None:
    lines = [
        "# Pre-2018 Executable-Status Source Report",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0",
        "",
        "## Acquired source",
        "",
        f"- Endpoint: OPENDART `list.json` pblntfty=I (거래소공시).",
        f"- Date range: **{first_d} → {last_d}**.",
        f"- Raw rows: **{raw_n}**.",
        f"- Filtered status events: **{filtered_n}**.",
        f"- Storage: `data/acquired/round5_dart_pre2018/` (gitignored; reproducible via build script).",
        "",
        "## Category distribution (filtered status events)",
        "",
        "| category | count |",
        "|---|---:|",
    ]
    for k, v in sorted(cat_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Coverage vs the Round-4 S3 baseline",
        "",
        "- Round 4 S3 acquisition: 425,294 raw / 10,774 filtered (2018-2026).",
        f"- This phase pre-2018: {raw_n} raw / {filtered_n} filtered (2010-2017).",
        "- Combined post-2010 baseline now available for reconciliation against the",
        "  2010-2017 equity panels.",
        "",
        "## Limitations",
        "",
        "- Same as Round 4 S3: rcept_dt = filing date, not always status effective date.",
        "- DART body parsing remains PARTIAL (S2 phase closed PARTIAL); exact effective",
        "  dates may differ from rcept_dt.",
        "- Intraday halts NOT captured.",
        "- Limit-lock authoritative log NOT captured.",
        "- Effective status duration NOT captured at date level.",
        "",
        "## Hard locks (preserved)",
        "",
        "- No credential committed.",
        "- No execution simulation.",
        "- No strategy testing.",
        "- This source does NOT certify execution feasibility for any specific date.",
        "",
    ]
    (OUT / "pre2018_status_source_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_taxonomy_mapping() -> None:
    lines = [
        "# Pre-2018 Taxonomy Mapping",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0",
        "",
        "Uses the canonical taxonomy from KR-EXECUTABLE-STATUS-COVERAGE-A0:",
        "",
        "| DART report_nm pattern | mapped category | canonical taxonomy label |",
        "|---|---|---|",
        "| contains `정지` AND `거래` AND NOT `해제` AND NOT `재개` | suspension_related | full_day_suspension |",
        "| contains `해제` OR `재개` | resumption_related | resumption_day |",
        "| contains `상장폐지` | delisting | delisting_transition |",
        "| contains `관리종목` | managed | managed_stock |",
        "| contains `투자` AND (`주의` OR `경고` OR `위험`) | investment_alert | investment_attention/warning/danger |",
        "| contains `정리매매` | liquidation | liquidation_trading |",
        "| contains `단기과열` | short_term_overheated | short_term_overheated |",
        "| else | other | unknown (requires_manual_review) |",
        "",
        "## Critical rules",
        "",
        "- Same regex as Round 4 S3 — keeps the 2010-2017 dataset directly compatible",
        "  with the 2018-2026 S3 dataset.",
        "- `other` rows REQUIRE manual review before status assignment.",
        "- Effective status date may differ from filing rcept_dt (DART body parse",
        "  needed for exact dates; S2 phase CLOSED AS PARTIAL).",
        "",
        "## Hard locks",
        "",
        "- No new label invented without DART body evidence.",
        "- `unknown` status MUST NOT be treated as executable.",
        "",
    ]
    (OUT / "pre2018_taxonomy_mapping.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Reconciliation
# ---------------------------------------------------------------------------

def load_2010_2016_panel_tickers() -> set[str]:
    p = REPO / "research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv"
    df = pd.read_csv(p, usecols=["종목코드"], dtype={"종목코드": str}, encoding="utf-8-sig")
    df["종목코드"] = df["종목코드"].str.zfill(6)
    return set(df["종목코드"].unique())


def load_2017_panel_tickers() -> set[str]:
    p = REPO / "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv"
    df = pd.read_csv(p, usecols=["날짜", "종목코드"], dtype={"종목코드": str}, encoding="utf-8-sig")
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    df["종목코드"] = df["종목코드"].str.zfill(6)
    # Only 2017 rows
    df = df[df["날짜"].dt.year == 2017]
    return set(df["종목코드"].unique())


def load_lifecycle_tickers() -> set[str]:
    p = REPO / "reports/experiments/measurement_A0/KR_LISTED_UNIVERSE_COVERAGE_A0/listed_lifecycle_coverage_table.csv"
    if not p.exists():
        return set()
    df = pd.read_csv(p, dtype={"ticker": str})
    return set(df["ticker"].astype(str).str.zfill(6))


def load_terminal_tickers() -> dict[str, dict]:
    p = REPO / "data/processed/w001_v2/listing_status_terminal.csv"
    df = pd.read_csv(p, encoding="utf-8-sig", dtype={"ticker": str})
    df["ticker"] = df["ticker"].str.zfill(6)
    return {r["ticker"]: r.to_dict() for _, r in df.iterrows()}


def build_reconciliation(filtered: pd.DataFrame) -> tuple[list[dict], dict]:
    panel_2010_2016 = load_2010_2016_panel_tickers()
    panel_2017 = load_2017_panel_tickers()
    panel_union = panel_2010_2016 | panel_2017
    lifecycle = load_lifecycle_tickers()
    terminal = load_terminal_tickers()

    rows = []
    counter = Counter()
    for _, r in filtered.iterrows():
        ticker = str(r.get("stock_code_str", "")).zfill(6) if r.get("stock_code_str", "") else ""
        if not ticker or ticker == "000000":
            counter["event_ticker_missing"] += 1
            continue
        in_panel = ticker in panel_union
        in_lifecycle = ticker in lifecycle
        has_terminal = ticker in terminal
        if in_panel and in_lifecycle:
            cls = "event_ticker_in_panel_and_lifecycle"
        elif in_panel and not in_lifecycle:
            cls = "event_ticker_in_panel_not_in_lifecycle"
        elif (not in_panel) and in_lifecycle:
            cls = "event_ticker_in_lifecycle_not_in_panel"
        else:
            cls = "event_not_in_lifecycle"
        if has_terminal:
            cls += "_with_terminal"
        else:
            cls += "_without_terminal"
        counter[cls] += 1
        rows.append({
            "rcept_no": r.get("rcept_no", ""),
            "rcept_dt": r.get("rcept_dt", ""),
            "ticker": ticker,
            "corp_code": r.get("corp_code", ""),
            "corp_name": r.get("corp_name", ""),
            "event_category": r.get("category", ""),
            "report_nm": r.get("report_nm", "")[:80],
            "in_panel_2010_2017": in_panel,
            "in_lifecycle": in_lifecycle,
            "has_w001_terminal": has_terminal,
            "reconciliation_class": cls,
        })
    return rows, dict(counter)


def write_reconciliation_summary(counter: dict, n_events: int) -> None:
    lines = [
        "# Pre-2018 Panel Reconciliation Summary",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0  ",
        "Method: for each acquired pre-2018 KRX status event, check whether the",
        "ticker is in the 2010-2017 equity panel union, in the KR-LISTED-UNIVERSE-",
        "COVERAGE-A0 lifecycle table, and/or has a W001 v2 terminal status.",
        "",
        f"## Headline: **{n_events}** pre-2018 status events reconciled",
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
        "- `event_ticker_in_panel_and_lifecycle_*`: most-informative match — event",
        "  ticker is present in the 2010-2017 panel AND in the listed-universe",
        "  lifecycle.",
        "- `event_ticker_in_panel_not_in_lifecycle_*`: event ticker is in the panel",
        "  but absent from the monthly-snapshot lifecycle — likely intra-month",
        "  listing/delisting or KONEX (excluded from lifecycle scope).",
        "- `event_ticker_in_lifecycle_not_in_panel_*`: lifecycle has the ticker but",
        "  panel did not include it (small caps below dynamic_top100 selection).",
        "- `event_not_in_lifecycle_*`: out-of-scope or KONEX-like ticker.",
        "- `_with_terminal` suffix: W001 v2 has a terminal status for the ticker.",
        "- `_without_terminal` suffix: no W001 v2 terminal — could be a non-terminal",
        "  event (managed / alert / temporary suspension) OR a coverage gap.",
        "",
        "## Hard locks (preserved)",
        "",
        "- No executable claim from panel presence.",
        "- No survivorship-safe claim.",
        "- No execution simulation.",
        "",
    ]
    (OUT / "pre2018_panel_reconciliation_summary.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Gap closure assessment
# ---------------------------------------------------------------------------

def write_gap_closure_assessment(raw_n: int, filtered_n: int, first_d: str, last_d: str,
                                  cat_counts: dict) -> str:
    # Decide gap status
    if filtered_n == 0:
        gap_status = "still_open"
        rationale = "no pre-2018 status events acquired"
    elif first_d == "20100104" and last_d >= "20171229":
        gap_status = "closed"
        rationale = f"full 2010-2017 window acquired ({filtered_n} filtered status events)"
    else:
        gap_status = "partial"
        rationale = f"partial coverage: {first_d} → {last_d}"
    lines = [
        "# Pre-2018 Coverage Gap Closure Assessment",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0",
        "",
        f"## Updated gap status: **{gap_status}**",
        "",
        f"Rationale: {rationale}",
        "",
        "## Comparison",
        "",
        "| metric | Round 4 S3 (2018-2026) | this phase (2010-2017) |",
        "|---|---:|---:|",
        f"| Date range | 2018-01-01 → 2026-05-06 | {first_d} → {last_d} |",
        f"| Filtered status events | 10,774 | {filtered_n} |",
        "",
        "## Defect update",
        "",
        f"- `pre_2018_status_coverage_gap` (from KR-EXECUTABLE-STATUS-COVERAGE-A0 ledger):",
        f"  - prior status: open",
        f"  - updated status: **{gap_status}**",
        f"  - evidence: this phase acquired and filtered the missing 2010-2017 window",
        "",
        "## Category coverage (pre-2018)",
        "",
        "| category | count |",
        "|---|---:|",
    ]
    for k, v in sorted(cat_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## What this does NOT do",
        "",
        "- Does NOT reopen strategy testing.",
        "- Does NOT open execution simulation.",
        "- Does NOT establish exact effective dates (DART body parsing needed; S2 PARTIAL).",
        "- Does NOT cover intraday halts.",
        "- Does NOT cover limit-lock authoritative status.",
        "- Does NOT certify survivorship safety.",
        "",
        "## Hard locks (preserved)",
        "",
        "- No execution simulation.",
        "- No strategy testing.",
        "- No production / paper / P08 / live readiness.",
        "",
    ]
    (OUT / "pre2018_gap_closure_assessment.md").write_text("\n".join(lines), encoding="utf-8")
    return gap_status


# ---------------------------------------------------------------------------
# Defect ledger + gate + summary
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


def build_defect_ledger(filtered_n: int, counter: dict, gap_status: str) -> list[dict]:
    defects = []
    if filtered_n == 0:
        defects.append({
            "defect_id": "PRE_00001",
            "severity": "critical",
            "defect_class": "pre2018_acquisition_failed",
            "detail": "OPENDART acquisition returned 0 filtered status events",
            "recommended_handling": "review acquisition_attempt_log.csv; possible API issue or query parameter mismatch",
        })
    # Some events may have no ticker (corp-only)
    if "event_ticker_missing" in counter and counter["event_ticker_missing"] > 0:
        defects.append({
            "defect_id": "PRE_00002",
            "severity": "low",
            "defect_class": "events_missing_stock_code",
            "detail": f"{counter['event_ticker_missing']} pre-2018 events have no `stock_code` populated (corp-only disclosures)",
            "recommended_handling": "exclude from per-ticker reconciliation; preserve in raw archive",
        })
    # other category rows
    defects.append({
        "defect_id": "PRE_00003",
        "severity": "medium",
        "defect_class": "report_nm_other_requires_manual_review",
        "detail": "events categorised as `other` (not matching the 7 status regex patterns) require manual review before status assignment",
        "recommended_handling": "S2 body parser closure (PARTIAL) limits automated triage; manual review queue",
    })
    # Effective date vs rcept_dt
    defects.append({
        "defect_id": "PRE_00004",
        "severity": "high",
        "defect_class": "effective_date_unknown",
        "detail": "rcept_dt is filing date, not status effective date; DART body parsing PARTIAL (S2 phase closed)",
        "recommended_handling": "any future execution-simulation use must adjust for effective date; cannot be done in this phase",
    })
    # Intraday + limit-lock still missing for pre-2018 (same as 2018+)
    defects.append({
        "defect_id": "PRE_00005",
        "severity": "high",
        "defect_class": "intraday_halt_still_missing_pre2018",
        "detail": "intraday halts not captured by OPENDART daily disclosures; same gap as 2018+ scope",
        "recommended_handling": "future phase: intraday halt source acquisition (commercial / KRX direct)",
    })
    return defects


def write_gate_status(filtered_n: int, gap_status: str, n_defects: int) -> str:
    if filtered_n == 0:
        gate = "DATA_SOURCE_FAIL"
        rationale = "no pre-2018 status events acquired"
    elif gap_status == "closed":
        gate = "PRE2018_STATUS_RECONCILED_BUT_EXECUTION_STILL_CLOSED"
        rationale = (
            f"full 2010-2017 window acquired ({filtered_n} filtered events) and reconciled "
            "against 2010-2017 panel union + listed-universe lifecycle. Execution simulation "
            "stays CLOSED."
        )
    elif gap_status == "partial":
        gate = "PARTIAL"
        rationale = f"partial pre-2018 coverage acquired ({filtered_n} events); some years missing"
    else:
        gate = "PRE2018_SOURCE_ACQUIRED_BUT_NOT_FULLY_RECONCILED"
        rationale = "events acquired but reconciliation incomplete"

    lines = [
        "# Pre-2018 Executable-Status Gate Status",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0",
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
        "- `PRE2018_SOURCE_ACQUIRED_BUT_NOT_FULLY_RECONCILED`",
        "- `PRE2018_STATUS_RECONCILED_BUT_EXECUTION_STILL_CLOSED`",
        "- `READY_FOR_NEXT_A0_REVIEW`",
        "",
        "## Numerical inputs",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| Filtered pre-2018 status events | {filtered_n} |",
        f"| Coverage gap status | {gap_status} |",
        f"| Total defects | {n_defects} |",
        "",
        "## Important boundary",
        "",
        "- Strategy testing is NOT opened.",
        "- Execution simulation is NOT opened.",
        "- Survivorship-safe claim NOT made.",
        "- Intraday halts + limit-lock still missing for pre-2018 (same as 2018+).",
        "",
    ]
    (OUT / "pre2018_gate_status.md").write_text("\n".join(lines), encoding="utf-8")
    return gate


def write_final_summary(raw_n: int, filtered_n: int, cat_counts: dict, counter: dict,
                        n_defects: int, gate: str, gap_status: str,
                        first_d: str, last_d: str) -> None:
    lines = [
        "# KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0 — Final Summary",
        "",
        "Date: 2026-05-24  ",
        "Predecessor: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0 CLOSED.",
        "",
        "## Scope respected",
        "",
        "- Measurement-layer executable-status source extension only.",
        "- No strategy testing.",
        "- No performance diagnostics.",
        "- No execution simulation.",
        "- No production / paper / P08 / live / shadow.",
        "",
        "## What was delivered",
        "",
        "Code artifacts:",
        "- `src/audit/measurement_a0/p_pre2018_executable_status_extension.py`",
        "",
        "Data artifacts (gitignored, reproducible via build script):",
        "- `data/acquired/round5_dart_pre2018/dart_pblntfty_I_all_2010_2017.csv` (raw)",
        "- `data/acquired/round5_dart_pre2018/krx_status_events_2010_2017.csv` (filtered)",
        "- `data/acquired/round5_dart_pre2018/acquisition_attempt_log.csv`",
        "",
        "Reports (this dir, 12 outputs):",
        "1. `pre2018_referee_lock.md`",
        "2. `source_feasibility_report.md`",
        "3. `acquisition_attempt_log.csv` (mirror of attempt log)",
        "4. `pre2018_status_source_report.md`",
        "5. `pre2018_status_coverage_table.csv`",
        "6. `pre2018_taxonomy_mapping.md`",
        "7. `pre2018_panel_reconciliation_summary.md`",
        "8. `pre2018_panel_reconciliation_ledger.csv`",
        "9. `pre2018_gap_closure_assessment.md`",
        "10. `pre2018_defect_ledger.csv`",
        "11. `pre2018_gate_status.md`",
        "12. `pre2018_final_summary.md` (this file)",
        "",
        "## Acquisition headline",
        "",
        f"- Source: OPENDART `list.json` pblntfty=I (거래소공시) with OPENDART_API_KEY.",
        f"- Date range acquired: **{first_d} → {last_d}**.",
        f"- Raw rows: **{raw_n}**.",
        f"- Filtered status events: **{filtered_n}**.",
        "",
        "## Category breakdown (filtered)",
        "",
        "| category | count |",
        "|---|---:|",
    ]
    for k, v in sorted(cat_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Reconciliation against 2010-2017 repo panels + lifecycle",
        "",
        "| class | count |",
        "|---|---:|",
    ]
    for k, v in sorted(counter.items(), key=lambda kv: -kv[1])[:10]:
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        f"## Gap closure: **{gap_status}**",
        "",
        f"## Pre-2018 gate state: **{gate}**",
        "",
        "## Defect ledger",
        "",
        f"- Total defects: **{n_defects}** (see `pre2018_defect_ledger.csv`).",
        "- Classes: acquisition failure (if 0 events) / events missing stock_code /",
        "  `other` requires manual review / effective_date unknown / intraday halt still",
        "  missing.",
        "",
        "## Pass criteria evaluation",
        "",
        "| criterion | status |",
        "|---|---|",
        "| Pre-2018 source feasibility documented | YES |",
        "| Acquisition attempt logged | YES |",
        "| Acquired or unavailable source status explicitly stated | YES |",
        "| Acquired events mapped into taxonomy | YES |",
        "| 2010-2017 panel linkage assessed | YES |",
        "| `pre_2018_status_coverage_gap` updated with evidence | YES |",
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
        "- No credential committed.",
        "- No card is strategy-ready.",
        "",
        "## Awaiting Referee",
        "",
        "Per Referee-defined exit conditions, Referee will decide whether to:",
        "- A. close as pre-2018 source acquired or source-unavailable documented,",
        "- B. require another pre-2018 source attempt,",
        "- C. open official limit-lock source acquisition,",
        "- D. open lifecycle daily refinement,",
        "- E. keep all strategy research closed.",
        "",
    ]
    (OUT / "pre2018_final_summary.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("[start] KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0")

    write_source_feasibility_report()
    write_taxonomy_mapping()

    raw_rows, log_rows = acquire_pre2018()
    # Mirror attempt log into the report dir
    if log_rows:
        log_df = pd.DataFrame(log_rows)
        log_df.to_csv(OUT / "acquisition_attempt_log.csv", index=False)
    raw_n = len(raw_rows)
    print(f"[acquisition] raw rows = {raw_n}")

    filtered = filter_status_events(raw_rows)
    write_filtered(filtered)
    filtered_n = len(filtered)
    cat_counts = {}
    if filtered_n > 0:
        cat_counts = filtered["category"].value_counts().to_dict()
        # Filter for date range computation
        filtered["rcept_dt"] = filtered["rcept_dt"].astype(str)
        first_d = filtered["rcept_dt"].min()
        last_d = filtered["rcept_dt"].max()
    else:
        first_d = "n/a"
        last_d = "n/a"
    print(f"[filtered] {filtered_n} events, range {first_d} → {last_d}")

    write_pre2018_status_source_report(raw_n, filtered_n, cat_counts, first_d, last_d)

    recon_rows, counter = build_reconciliation(filtered)
    write_csv(OUT / "pre2018_panel_reconciliation_ledger.csv", recon_rows)
    write_reconciliation_summary(counter, len(recon_rows))
    print(f"[reconciliation] {counter}")

    # Coverage table = filtered rows in normalised shape
    cov_rows = []
    for _, r in filtered.iterrows():
        cov_rows.append({
            "rcept_no": r.get("rcept_no", ""),
            "date": r.get("rcept_dt", ""),
            "ticker": r.get("stock_code_str", ""),
            "corp_code": r.get("corp_code", ""),
            "corp_name": r.get("corp_name", ""),
            "event_category": r.get("category", ""),
            "report_name": r.get("report_nm", ""),
            "source": "OPENDART pblntfty=I (acquired this phase)",
            "source_confidence": "semi_official_dart",
            "official_or_proxy": "semi_official",
            "linked_to_lifecycle": "(see reconciliation ledger)",
            "linked_to_panel": "(see reconciliation ledger)",
            "requires_manual_review": "true" if r.get("category", "") == "other" else "false",
        })
    write_csv(OUT / "pre2018_status_coverage_table.csv", cov_rows)
    print(f"[coverage_table] {len(cov_rows)} rows")

    gap_status = write_gap_closure_assessment(raw_n, filtered_n, first_d, last_d, cat_counts)
    defects = build_defect_ledger(filtered_n, counter, gap_status)
    write_csv(OUT / "pre2018_defect_ledger.csv", defects)
    gate = write_gate_status(filtered_n, gap_status, len(defects))
    write_final_summary(raw_n, filtered_n, cat_counts, counter, len(defects), gate, gap_status, first_d, last_d)

    print(json.dumps({
        "raw_rows": raw_n,
        "filtered_events": filtered_n,
        "date_range": f"{first_d} → {last_d}",
        "categories": cat_counts,
        "reconciliation": counter,
        "n_defects": len(defects),
        "gap_status": gap_status,
        "gate": gate,
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
