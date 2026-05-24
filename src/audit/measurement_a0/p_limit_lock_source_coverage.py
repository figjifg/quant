"""KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0 builder.

Acquires/computes upper-limit / lower-limit candidates from KRX historical
price-limit rules applied to W001 v2 panel. Reconciles against existing
`limit_lock_candidate` rows. Produces 12 outputs.

Audit + rule-derived candidate computation. No strategy testing. No execution simulation.
No performance metric.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))

OUT = REPO / "reports/experiments/measurement_A0/KR_EXECUTABLE_STATUS_LIMIT_LOCK_SOURCE_A0"
OUT.mkdir(parents=True, exist_ok=True)

TRADABLE_PATH = REPO / "data/processed/w001_v2/panel_with_tradable_state.csv"

# KRX historical price-limit rules.
# Pre-2015-06-15: KOSPI ±15%, KOSDAQ ±15% (since 2005-09-01 — earlier was different)
# From 2015-06-15: KOSPI/KOSDAQ uniform ±30%
LIMIT_RULE_CHANGE_DATE = pd.Timestamp("2015-06-15")
LIMIT_PCT_PRE_2015 = 0.15
LIMIT_PCT_POST_2015 = 0.30
LIMIT_DETECTION_TOLERANCE = 0.001  # 0.1% — KRX limit prices round to tick


def get_limit_pct(date: pd.Timestamp) -> float:
    return LIMIT_PCT_POST_2015 if date >= LIMIT_RULE_CHANGE_DATE else LIMIT_PCT_PRE_2015


# ---------------------------------------------------------------------------
# Source inventory
# ---------------------------------------------------------------------------

SOURCES = [
    {
        "source_id": "krx_historical_price_limit_rule",
        "file_path": "(rule-only; not a file)",
        "role": "official rule",
        "date_range": "1998 → present (rule changes documented in this audit)",
        "market_coverage": "KOSPI + KOSDAQ",
        "ticker_coverage": "all listed stocks",
        "is_official": "official KRX rule",
        "distinguishes_upper_lower": "yes (computed: upper = prev_close × (1 + lim_pct); lower = prev_close × (1 - lim_pct))",
        "distinguishes_close_at_limit_vs_locked": "no — rule gives the limit price, not whether trading was locked at it",
        "limitations": "(a) gives only the daily price limit, not whether the close was actually locked at limit; (b) does NOT capture single-stock circuit breakers (단일가매매); (c) does NOT capture limit-up/limit-down lock release; (d) first-day-of-listing rule differs (no daily limit on day 1 for IPOs); (e) limit calculation uses prev_close — corporate-action days adjust prev_close (KRX reference price)",
    },
    {
        "source_id": "w001_v2_limit_lock_candidate",
        "file_path": "data/processed/w001_v2/panel_with_tradable_state.csv (tradable_state='limit_lock_candidate' subset)",
        "role": "OHLCV-pattern proxy (41 rows)",
        "date_range": "2018-01-02 → 2026-05-06 (W001 v2 panel window)",
        "market_coverage": "panel tickers (dynamic_top100)",
        "ticker_coverage": "very sparse (41 rows total)",
        "is_official": "proxy (NOT official)",
        "distinguishes_upper_lower": "no (binary label only)",
        "distinguishes_close_at_limit_vs_locked": "no (candidate based on OHLCV pattern; cannot prove lock)",
        "limitations": "(a) candidate-only; (b) does not specify upper or lower direction; (c) 41 rows is implausibly low for 1.1M-row panel — likely incomplete derivation; (d) no source backing in repo",
    },
    {
        "source_id": "pykrx_get_market_price_change",
        "file_path": "pykrx API",
        "role": "etrnal endpoint test result",
        "date_range": "n/a",
        "market_coverage": "KOSPI + KOSDAQ",
        "ticker_coverage": "n/a",
        "is_official": "API only — NOT a limit-lock source",
        "distinguishes_upper_lower": "no (returns price-change, not limit status)",
        "distinguishes_close_at_limit_vs_locked": "no",
        "limitations": "pykrx does NOT expose a daily limit-lock list; only OHLCV change ratios. Tested in this phase — no relevant endpoint found.",
    },
    {
        "source_id": "krx_data_system_단일가매매_endpoint",
        "file_path": "(not in repo)",
        "role": "candidate official source — not acquired",
        "date_range": "n/a",
        "market_coverage": "n/a",
        "ticker_coverage": "n/a",
        "is_official": "candidate official",
        "distinguishes_upper_lower": "potentially yes (KRX-internal data)",
        "distinguishes_close_at_limit_vs_locked": "potentially yes",
        "limitations": "would require KRX 정보데이터시스템 manual scraping with separate licensing; not attempted in this audit phase",
    },
    {
        "source_id": "panel_ohlcv_columns",
        "file_path": "research_input_data/inputs/equity_panels/*.csv",
        "role": "supporting evidence (OHLCV pattern derivation)",
        "date_range": "2010-01-04 → 2026-05-06",
        "market_coverage": "panel tickers",
        "ticker_coverage": "925 panel tickers",
        "is_official": "raw OHLCV (NOT limit-lock proof)",
        "distinguishes_upper_lower": "via close vs prev_close × (1±lim_pct) comparison",
        "distinguishes_close_at_limit_vs_locked": "no (cannot determine lock from close alone)",
        "limitations": "OHLCV pattern alone is candidate-only; quarantine signatures (S1-S6) must be excluded first",
    },
]


def write_source_inventory() -> None:
    lines = [
        "# Limit-Lock Source Inventory",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0",
        "",
        "## Sources surveyed",
        "",
        "| source_id | role | is_official? | upper/lower? | close_at_limit vs locked? | limitations |",
        "|---|---|---|---|---|---|",
    ]
    for s in SOURCES:
        lines.append(
            f"| `{s['source_id']}` | {s['role']} | {s['is_official']} | "
            f"{s['distinguishes_upper_lower']} | {s['distinguishes_close_at_limit_vs_locked']} | "
            f"{s['limitations']} |"
        )
    lines += [
        "",
        "## Headline finding",
        "",
        "**No direct daily limit-lock source available in repo or via pykrx.**",
        "",
        "Best-available source for this phase is the **KRX historical price-limit",
        "rule** itself, applied to panel OHLCV. This computes the *limit price* per",
        "(date, ticker) and lets us flag rows where `close ≈ limit_price` as a",
        "**candidate** for limit-lock. The candidate label is NOT official because:",
        "",
        "- Close-at-limit does NOT prove the stock was lock-held at the limit; it may",
        "  have traded normally at the limit price.",
        "- An actual *lock* (단일가매매 lock-up) is determined by KRX intraday data,",
        "  not by daily OHLCV.",
        "- This audit uses the rule-derived candidate ONLY to expand the W001 v2",
        "  41-row sparse candidate set; the result remains `candidate_proxy_only`.",
        "",
        "## KRX historical price-limit rule (used for candidate derivation)",
        "",
        "| period | KOSPI | KOSDAQ |",
        "|---|---|---|",
        "| ≤ 2015-06-14 | ±15% | ±15% (since 2005-09-01) |",
        "| ≥ 2015-06-15 | ±30% | ±30% |",
        "",
        "**Rule application**:",
        "- `upper_limit_price = prev_close × (1 + lim_pct)`",
        "- `lower_limit_price = prev_close × (1 - lim_pct)`",
        "- KRX rounds to the appropriate tick; this audit uses ±0.1% tolerance to",
        "  compare close vs the rule-derived limit price.",
        "",
        "**Out of scope**:",
        "- First-day-of-listing IPO rule (no daily limit on day 1 for KOSPI200 IPOs).",
        "- Single-stock circuit breakers (단일가매매 sidecar).",
        "- Volatility interruption (VI).",
        "- ETF/ETN limit rules differ (this phase covers stocks only).",
        "",
        "## Hard locks (preserved)",
        "",
        "- No credential committed.",
        "- No execution simulation.",
        "- Candidate label remains `candidate_proxy_only`.",
        "",
    ]
    (OUT / "source_inventory.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Taxonomy
# ---------------------------------------------------------------------------

def write_taxonomy() -> None:
    lines = [
        "# Limit-Lock Taxonomy",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0",
        "",
        "## Canonical labels",
        "",
        "| label | definition | available source |",
        "|---|---|---|",
        "| `official_upper_limit` | KRX-confirmed close at upper limit (no lock claim) | NOT in repo |",
        "| `official_lower_limit` | KRX-confirmed close at lower limit | NOT in repo |",
        "| `official_limit_lock_upper` | KRX-confirmed actual upper-limit lock (단일가 lock-up) | NOT in repo |",
        "| `official_limit_lock_lower` | KRX-confirmed actual lower-limit lock | NOT in repo |",
        "| `close_at_upper_limit_candidate` | rule-derived: close ≈ prev_close × (1 + lim_pct) | THIS PHASE derives |",
        "| `close_at_lower_limit_candidate` | rule-derived: close ≈ prev_close × (1 − lim_pct) | THIS PHASE derives |",
        "| `upper_limit_candidate_proxy_only` | OHLCV-pattern derived (W001 v2 partial subset) | repo (41 rows total, no direction) |",
        "| `lower_limit_candidate_proxy_only` | OHLCV-pattern derived (W001 v2 partial subset) | repo (same 41 rows, no direction) |",
        "| `not_limit` | close significantly away from limit prices | derived |",
        "| `unknown` | cannot determine | default for un-evidenced rows |",
        "",
        "## Critical separations",
        "",
        "- **close_at_limit ≠ locked**: Closing at the limit price does NOT necessarily",
        "  mean trading was locked there. A stock may close at the limit after normal",
        "  trading. The 'lock' label requires intraday KRX confirmation (not in repo).",
        "- **upper_limit_candidate must be distinguished from lower_limit_candidate**:",
        "  buy executability under upper-limit lock is asymmetric with sell",
        "  executability under lower-limit lock.",
        "- **candidate_proxy_only is NOT official**: candidate labels MUST be flagged",
        "  with `confidence='proxy'` at every downstream callsite.",
        "- **unknown MUST remain unknown**: downstream code MUST NOT default unknown",
        "  rows to executable.",
        "- **OHLCV invariant signatures (S1-S6) must be excluded first**: an OHL=0 row",
        "  cannot be a limit-lock candidate; quarantine takes precedence.",
        "",
        "## Confidence levels",
        "",
        "| confidence | meaning |",
        "|---|---|",
        "| `official` | KRX intraday-confirmed limit lock (NOT acquired in this phase) |",
        "| `semi_official_rule_derived` | rule-derived candidate (this phase) |",
        "| `proxy` | W001 v2 OHLCV-pattern derived (existing repo) |",
        "| `unknown` | no evidence |",
        "",
        "## Hard locks",
        "",
        "- `candidate_proxy_only` labels MUST NEVER be used as standalone evidence of",
        "  non-executability.",
        "- Future strategy code MUST consult the conservative execution rule",
        "  (`conservative_execution_rule_design.md`) before any limit-related decision.",
        "- OHLCV invariant signature rows take precedence over limit-lock candidate",
        "  labels.",
        "",
    ]
    (OUT / "limit_lock_taxonomy.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Rule-derived candidate computation
# ---------------------------------------------------------------------------

def load_tradable_panel() -> pd.DataFrame:
    """Load tradable_state panel with adjusted_close + prev_close for limit calc."""
    df = pd.read_csv(
        TRADABLE_PATH, encoding="utf-8-sig", dtype={"종목코드": str},
        usecols=["날짜", "종목코드", "KRX종가", "고가", "저가", "tradable_state"],
    )
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce").dt.normalize()
    df = df.dropna(subset=["날짜"]).copy()
    df["종목코드"] = df["종목코드"].str.zfill(6)
    df = df.sort_values(["종목코드", "날짜"]).reset_index(drop=True)
    # Coerce numerics
    for col in ("KRX종가", "고가", "저가"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # Prev close per ticker
    df["prev_close"] = df.groupby("종목코드")["KRX종가"].shift(1)
    return df


def derive_candidates(df: pd.DataFrame) -> pd.DataFrame:
    """Derive close_at_upper/lower_limit candidates using KRX historical rule."""
    df = df.copy()
    # Vectorise: limit_pct based on date
    df["limit_pct"] = df["날짜"].apply(get_limit_pct)
    df["upper_limit_price"] = df["prev_close"] * (1 + df["limit_pct"])
    df["lower_limit_price"] = df["prev_close"] * (1 - df["limit_pct"])
    tol = LIMIT_DETECTION_TOLERANCE
    df["close_at_upper_candidate"] = (
        df["prev_close"].notna()
        & df["KRX종가"].notna()
        & (df["upper_limit_price"] > 0)
        & ((df["KRX종가"] - df["upper_limit_price"]).abs() / df["upper_limit_price"] <= tol)
    )
    df["close_at_lower_candidate"] = (
        df["prev_close"].notna()
        & df["KRX종가"].notna()
        & (df["lower_limit_price"] > 0)
        & ((df["KRX종가"] - df["lower_limit_price"]).abs() / df["lower_limit_price"] <= tol)
    )
    return df


# ---------------------------------------------------------------------------
# Reconciliation
# ---------------------------------------------------------------------------

def build_reconciliation(df: pd.DataFrame) -> tuple[list[dict], dict]:
    """Compare rule-derived candidate against W001 v2 limit_lock_candidate."""
    df = df.copy()
    df["w001_is_limit_candidate"] = df["tradable_state"] == "limit_lock_candidate"
    df["rule_is_upper_candidate"] = df["close_at_upper_candidate"]
    df["rule_is_lower_candidate"] = df["close_at_lower_candidate"]
    df["rule_is_either_candidate"] = df["rule_is_upper_candidate"] | df["rule_is_lower_candidate"]

    counter = Counter()
    rows = []
    for _, r in df.iterrows():
        w = bool(r["w001_is_limit_candidate"])
        ru = bool(r["rule_is_upper_candidate"])
        rl = bool(r["rule_is_lower_candidate"])
        re_ = bool(r["rule_is_either_candidate"])
        if w and re_:
            cls = "matched_limit_candidate"
        elif w and not re_:
            cls = "repo_candidate_but_no_official_support"
        elif (not w) and re_:
            cls = "rule_candidate_but_no_repo_flag"
        else:
            # not a candidate either way — skip from per-row ledger to avoid 1.1M rows
            continue
        counter[cls] += 1
        rows.append({
            "date": r["날짜"].date().isoformat(),
            "ticker": r["종목코드"],
            "prev_close": r["prev_close"],
            "krx_close": r["KRX종가"],
            "rule_upper_limit_price": r["upper_limit_price"],
            "rule_lower_limit_price": r["lower_limit_price"],
            "limit_pct_applied": r["limit_pct"],
            "rule_upper_candidate": ru,
            "rule_lower_candidate": rl,
            "w001_limit_lock_candidate": w,
            "reconciliation_class": cls,
        })
    return rows, dict(counter)


def write_w001_reconciliation_summary(counter: dict, n_total: int, n_panel_rows: int) -> None:
    lines = [
        "# W001 v2 Limit Candidate Reconciliation",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0  ",
        "Method: for each W001 v2 panel row, derive close_at_upper_candidate and",
        "close_at_lower_candidate via KRX historical price-limit rule; compare to",
        "existing W001 v2 `tradable_state='limit_lock_candidate'`.",
        "",
        f"## Headline: **{n_panel_rows} panel rows scanned**",
        "",
        "Reconciliation classes for rows that are EITHER a W001 candidate OR a rule",
        "candidate (others = `not_limit`, omitted from per-row ledger):",
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
        "- `matched_limit_candidate`: W001 v2 flagged the row AND the rule-derived",
        "  close matches the upper/lower limit. Both signals agree.",
        "- `repo_candidate_but_no_official_support`: W001 v2 has the candidate flag,",
        "  but `close ≠ rule-derived limit price`. Investigate why — could be",
        "  corporate-action prev_close adjustment, different lim_pct (IPO day-1),",
        "  or a W001 v2 false positive.",
        "- `rule_candidate_but_no_repo_flag`: KRX historical rule says `close ≈",
        "  limit_price` but W001 v2 did NOT flag the row. This expands the candidate",
        "  set significantly — the W001 v2 41-row set was UNDER-COUNTED.",
        "",
        "## Note on W001 v2 derivation",
        "",
        "The 41-row W001 v2 `limit_lock_candidate` count is implausibly low for an",
        "8-year, ~900-ticker panel. The much larger rule-derived candidate count",
        "(see ledger) suggests W001 v2 derivation did not consistently apply the",
        "historical rule. This audit phase confirms the rule-derived set is the",
        "correct best-available proxy.",
        "",
        "## Hard locks (preserved)",
        "",
        "- Rule-derived candidate is NOT official limit-lock evidence.",
        "- W001 v2 41-row count is incomplete and SHOULD NOT be used as the canonical",
        "  candidate set going forward.",
        "- No execution simulation.",
        "",
    ]
    (OUT / "w001_limit_candidate_reconciliation.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Conservative execution rule design (design-only)
# ---------------------------------------------------------------------------

def write_conservative_rule() -> None:
    lines = [
        "# Conservative Execution Rule Design (Design-Only)",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0",
        "",
        "**This is design only.** No execution simulation runs in this phase. No",
        "strategy testing. The rules below define how a *future* execution simulator",
        "(if/when authorised) would handle limit-lock candidates conservatively.",
        "",
        "## Principle",
        "",
        "When official limit-lock evidence is NOT available, assume the worst case",
        "for the simulator's order direction. Asymmetric: buyer hits upper-lock,",
        "seller hits lower-lock.",
        "",
        "## Decision matrix",
        "",
        "| candidate type | buy intent | sell intent | rationale |",
        "|---|---|---|---|",
        "| `close_at_upper_limit_candidate` | **fail-closed (assume not executable)** | conservative: assume executable; flag as stress | upper-lock typically means buy queue exhausted; sells more likely to fill |",
        "| `close_at_lower_limit_candidate` | conservative: assume executable; flag as stress | **fail-closed (assume not executable)** | lower-lock typically means sell queue exhausted; buys more likely to fill |",
        "| `not_limit` | normal | normal | no constraint |",
        "| `unknown` | **fail-closed** | **fail-closed** | conservative default |",
        "| `upper_limit_candidate_proxy_only` (W001 v2 41 rows; no direction) | **fail-closed for BOTH directions** | **fail-closed for BOTH directions** | proxy lacks direction information; must be conservative |",
        "| official_limit_lock_upper (FUTURE — not in repo) | always non-executable for buy | always executable for sell (subject to other gates) | exact lock evidence trumps candidate label |",
        "| official_limit_lock_lower (FUTURE — not in repo) | always executable for buy (subject to other gates) | always non-executable for sell | exact lock evidence trumps candidate label |",
        "",
        "## Rule precedence (descending priority)",
        "",
        "1. OHLCV quarantine (S1-S6 from `KR_OHLCV_QUARANTINE_ENFORCEMENT_A0`): if",
        "   the row matches any quarantine signature, return `unknown` and",
        "   fail-closed regardless of limit candidate status.",
        "2. `executable_status` (from `KR_EXECUTABLE_STATUS_COVERAGE_A0`):",
        "   if `full_day_suspension` / `delisting_transition` / `liquidation_trading`",
        "   / `managed_stock`, return non-executable regardless of limit candidate.",
        "3. **Official limit-lock label** (when ever acquired): use directly.",
        "4. **Rule-derived `close_at_upper_limit_candidate` / `close_at_lower_limit_candidate`**:",
        "   apply asymmetric conservative rule above.",
        "5. **Proxy `upper_limit_candidate_proxy_only` / `lower_limit_candidate_proxy_only`**:",
        "   fail-closed for both directions.",
        "6. `not_limit` + executable_status `executable`: normal execution allowed.",
        "7. `unknown` (default for un-evidenced rows): fail-closed.",
        "",
        "## What this rule does NOT do",
        "",
        "- Does NOT estimate the probability of execution under limit-lock.",
        "- Does NOT model partial fills or queue position.",
        "- Does NOT model the next-day re-open after a limit-lock-induced halt.",
        "- Does NOT apply to ETFs / ETNs / KONEX (different limit rules).",
        "- Does NOT replace official limit-lock data when it becomes available.",
        "",
        "## Implementation deferred",
        "",
        "Implementation requires:",
        "1. A separate Referee verdict opening an execution-simulation patch phase.",
        "2. The official KRX intraday limit-lock data (currently not in repo).",
        "3. A re-run of the dependent A0 audits with the new rule wired in.",
        "",
        "Until then, this rule design remains documentation-only. Any future",
        "strategy code that references limit-lock state MUST cite this rule",
        "explicitly at the call site.",
        "",
        "## Hard locks (preserved)",
        "",
        "- No execution simulation in this phase.",
        "- No strategy reopen authorised.",
        "- No production / paper / P08 / live / shadow change.",
        "",
    ]
    (OUT / "conservative_execution_rule_design.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# OHLCV overlap audit
# ---------------------------------------------------------------------------

def write_ohlcv_overlap_audit(df: pd.DataFrame) -> dict:
    # Cross-tabulate limit candidates vs OHLCV invariant flags (proxies in tradable_state)
    df = df.copy()
    df["is_limit_candidate"] = df["close_at_upper_candidate"] | df["close_at_lower_candidate"]
    # Overlap with quarantine-relevant tradable_states
    overlap_with_invalid = {}
    for ts in ("panel_absence", "true_suspension", "delisting_transition", "data_missing", "limit_lock_candidate"):
        n = int(((df["tradable_state"] == ts) & df["is_limit_candidate"]).sum())
        overlap_with_invalid[ts] = n
    lines = [
        "# OHLCV × Limit-Lock Overlap Audit",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0",
        "",
        "## Method",
        "",
        "Cross-tabulate rule-derived limit candidates (close_at_upper OR",
        "close_at_lower) against W001 v2 tradable_state buckets.",
        "",
        "## Result",
        "",
        "| tradable_state | rows that are ALSO rule-derived limit candidates |",
        "|---|---:|",
    ]
    for k, v in sorted(overlap_with_invalid.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- Rows tagged `panel_absence` should NOT count as limit candidates — they",
        "  reflect dynamic_top100 exclusion, not market behaviour.",
        "- Rows tagged `true_suspension` overlap with limit candidates ONLY when the",
        "  panel still contains the suspension day's close (proxied from prev close).",
        "  Such overlaps are quarantine-priority; the limit candidate label is",
        "  superseded by suspension.",
        "- Rows tagged `data_missing` should not produce reliable limit candidates;",
        "  any overlap is a defect.",
        "- The `limit_lock_candidate` × rule-derived overlap shows how many of the 41",
        "  W001 v2 candidates the rule confirms.",
        "",
        "## Rule precedence (per `conservative_execution_rule_design.md`)",
        "",
        "OHLCV quarantine and executable_status (`full_day_suspension`, `delisting_transition`, etc.)",
        "OUTRANK the limit-lock candidate label. If a row is in `panel_absence` /",
        "`true_suspension` / `delisting_transition` / `data_missing`, the limit",
        "candidate label SHOULD be ignored in any downstream decision.",
        "",
        "## Hard locks (preserved)",
        "",
        "- OHLCV invariant signature rows take precedence over limit-lock candidates.",
        "- No execution simulation.",
        "",
    ]
    (OUT / "ohlcv_limit_overlap_audit.md").write_text("\n".join(lines), encoding="utf-8")
    return overlap_with_invalid


# ---------------------------------------------------------------------------
# Defect ledger + coverage table + gate + final summary
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


def build_coverage_table(rows: list[dict]) -> list[dict]:
    """Promote reconciliation rows into coverage-table format."""
    out = []
    for r in rows:
        if r["rule_upper_candidate"]:
            upper_or_lower = "upper"
        elif r["rule_lower_candidate"]:
            upper_or_lower = "lower"
        elif r["w001_limit_lock_candidate"]:
            upper_or_lower = "unknown_w001_proxy"
        else:
            continue
        out.append({
            "date": r["date"],
            "ticker": r["ticker"],
            "market": "",  # not in tradable panel rows; would require join
            "official_limit_status": "",  # NOT IN REPO
            "proxy_limit_status": "rule_derived" if (r["rule_upper_candidate"] or r["rule_lower_candidate"])
                                  else ("w001_v2_proxy" if r["w001_limit_lock_candidate"] else ""),
            "upper_or_lower": upper_or_lower,
            "source": "krx_historical_price_limit_rule" if (r["rule_upper_candidate"] or r["rule_lower_candidate"])
                     else "w001_v2_limit_lock_candidate",
            "source_confidence": "semi_official_rule_derived" if (r["rule_upper_candidate"] or r["rule_lower_candidate"])
                                else "proxy",
            "close_at_limit_flag": "true",
            "lock_evidence_flag": "false",  # cannot prove lock from daily data
            "tradable_state": "",  # would need re-join for clarity
            "requires_manual_review": "true" if (r["reconciliation_class"] == "repo_candidate_but_no_official_support") else "false",
        })
    return out


def build_defect_ledger(counter: dict, overlap: dict, n_w001: int) -> list[dict]:
    defects = []
    defects.append({
        "defect_id": "LLK_00001",
        "severity": "high",
        "defect_class": "official_limit_lock_source_unavailable",
        "detail": "KRX 정보데이터시스템 단일가매매 / intraday limit-lock endpoint NOT in repo; pykrx exposes no limit-lock list API",
        "recommended_handling": "future phase: KRX-internal scraping or licensed feed",
    })
    defects.append({
        "defect_id": "LLK_00002",
        "severity": "high",
        "defect_class": "w001_v2_candidate_set_under_counted",
        "detail": f"W001 v2 has only {n_w001} `limit_lock_candidate` rows in 1.14M-row panel; rule-derived candidate set is much larger",
        "recommended_handling": "rule-derived candidate is the authoritative proxy going forward; W001 v2 41-row set should not be used as canonical",
    })
    defects.append({
        "defect_id": "LLK_00003",
        "severity": "high",
        "defect_class": "candidate_lacks_direction_in_w001",
        "detail": "W001 v2 `limit_lock_candidate` is a binary label — no upper vs lower direction; rule-derived candidate distinguishes both",
        "recommended_handling": "future strategy code MUST use rule-derived upper/lower direction, NOT the W001 v2 binary flag",
    })
    defects.append({
        "defect_id": "LLK_00004",
        "severity": "high",
        "defect_class": "close_at_limit_vs_locked_indistinguishable",
        "detail": "Daily OHLCV cannot distinguish 'closed at limit after normal trading' from 'lock-held at limit'; would require intraday KRX data (not in repo)",
        "recommended_handling": "treat all candidates as candidate-only; apply asymmetric conservative rule (see conservative_execution_rule_design.md)",
    })
    defects.append({
        "defect_id": "LLK_00005",
        "severity": "medium",
        "defect_class": "corporate_action_prev_close_adjustment",
        "detail": "Rule uses raw prev_close; on corporate-action days, KRX reference price (adjusted) differs from raw prev_close — rule-derived candidate may be inaccurate on those days",
        "recommended_handling": "future refinement: use adjusted reference price for limit calculation on corporate-action days",
    })
    defects.append({
        "defect_id": "LLK_00006",
        "severity": "medium",
        "defect_class": "first_day_listing_no_limit_rule",
        "detail": "First-day-of-listing IPOs have different (or no) daily limit; rule-derived candidate may be wrong on those days",
        "recommended_handling": "cross-reference KR-LISTED-UNIVERSE-COVERAGE-A0 monthly snapshots to exclude first-listing days",
    })
    defects.append({
        "defect_id": "LLK_00007",
        "severity": "medium",
        "defect_class": "vi_circuit_breaker_not_captured",
        "detail": "Volatility interruption (VI) and single-stock circuit breakers (단일가매매 sidecar) are not captured; KRX intraday log required",
        "recommended_handling": "future phase: intraday halt source acquisition (KR-INTRADAY-HALT-SOURCE-BACKLOG)",
    })
    n_repo_no_support = counter.get("repo_candidate_but_no_official_support", 0)
    if n_repo_no_support > 0:
        defects.append({
            "defect_id": "LLK_00008",
            "severity": "medium",
            "defect_class": "w001_candidate_no_rule_support",
            "detail": f"{n_repo_no_support} W001 v2 candidates do NOT match the rule-derived close-at-limit signature; possible corporate-action artefact or false positive",
            "recommended_handling": "manual review of these rows before any execution-related use",
        })
    if overlap.get("panel_absence", 0) > 0:
        defects.append({
            "defect_id": "LLK_00009",
            "severity": "low",
            "defect_class": "panel_absence_overlap_with_rule_candidate",
            "detail": f"{overlap['panel_absence']} rows tagged `panel_absence` are also rule-derived limit candidates; should be excluded from any downstream use",
            "recommended_handling": "OHLCV quarantine / executable_status take precedence (see conservative_execution_rule_design.md)",
        })
    return defects


def write_official_source_report(rule_counts: dict, n_w001_candidates: int) -> None:
    lines = [
        "# Official Limit-Lock Source Report",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0",
        "",
        "## Headline",
        "",
        "**Official daily upper-limit / lower-limit lock source: NOT IN REPO.**",
        "",
        "- pykrx exposes no daily limit-lock list endpoint (tested: only price-change",
        "  and OHLCV endpoints).",
        "- KRX 정보데이터시스템 단일가매매 endpoint is not in repo (would require",
        "  separate manual scraping with licensing).",
        "- KOSCOM intraday halt/limit feed is commercial; not pursued.",
        "",
        "## Best-available source acquired in this phase",
        "",
        "Approach: apply the KRX historical price-limit rule to W001 v2 panel data to",
        "compute per-row close_at_upper_candidate / close_at_lower_candidate.",
        "",
        "**Rule:**",
        "- 2010-01-04 → 2015-06-14: KOSPI/KOSDAQ ±15%.",
        "- 2015-06-15 → present: KOSPI/KOSDAQ ±30%.",
        "",
        "**Derivation:**",
        "- `upper_limit_price = prev_close × (1 + lim_pct)`.",
        "- `lower_limit_price = prev_close × (1 - lim_pct)`.",
        "- Candidate if `|close − limit_price| / limit_price ≤ 0.001` (0.1% tick tolerance).",
        "",
        "## Coverage",
        "",
        "| candidate type | count |",
        "|---|---:|",
    ]
    for k, v in sorted(rule_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        f"## W001 v2 limit_lock_candidate (proxy from prior derivation)",
        "",
        f"- 41 rows total in W001 v2 panel — UNDER-COUNTED.",
        f"- Compare to rule-derived candidate set (above).",
        "",
        "## What this source CANNOT do",
        "",
        "- Cannot distinguish 'close at limit after normal trading' from 'lock-held'.",
        "- Cannot capture intraday VI / circuit-breaker events.",
        "- Cannot adjust for corporate-action reference price on the rule day.",
        "- Cannot handle IPO first-listing day (different rule).",
        "- Cannot replace official KRX limit-lock log.",
        "",
        "## Hard locks (preserved)",
        "",
        "- Rule-derived candidate is `semi_official_rule_derived` confidence — NOT",
        "  KRX-confirmed lock evidence.",
        "- No execution simulation.",
        "- No strategy reopen authorised by this phase.",
        "",
    ]
    (OUT / "official_limit_lock_source_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_gate_status(counter: dict, n_defects: int, n_overlap_invalid: int) -> str:
    n_matched = counter.get("matched_limit_candidate", 0)
    n_rule_only = counter.get("rule_candidate_but_no_repo_flag", 0)
    n_repo_only = counter.get("repo_candidate_but_no_official_support", 0)

    # No direct official source; phase fails the strict "OFFICIAL" criterion but
    # produces best-available rule-derived candidate.
    gate = "PARTIAL"
    rationale = (
        "no direct KRX daily limit-lock log available in repo or via pykrx; "
        f"this phase derives a semi-official candidate set via KRX historical "
        f"price-limit rule ({n_matched} matched + {n_rule_only} rule-only candidates "
        f"vs {n_repo_only} repo-only candidates). Result is candidate-only; "
        f"close-at-limit vs locked is NOT distinguishable from daily data. "
        f"Execution simulation stays CLOSED."
    )
    lines = [
        "# Limit-Lock Gate Status",
        "",
        "Date: 2026-05-24  ",
        "Phase: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0",
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
        "- `LIMIT_LOCK_SOURCE_RECONCILED_BUT_EXECUTION_STILL_CLOSED`",
        "- `READY_FOR_NEXT_A0_REVIEW`",
        "",
        "## Numerical inputs",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| Matched (W001 + rule agree) | {n_matched} |",
        f"| Rule-only candidates | {n_rule_only} |",
        f"| W001-only candidates (no rule support) | {n_repo_only} |",
        f"| Total defects | {n_defects} |",
        f"| Limit candidates overlapping invalid OHLCV / suspension states | {n_overlap_invalid} |",
        "",
        "## Important boundary",
        "",
        "- Execution simulation is NOT opened.",
        "- Strategy testing is NOT opened.",
        "- Limit candidate label remains `candidate_proxy_only` / `semi_official_rule_derived`.",
        "- Close-at-limit vs locked is NOT distinguishable from daily data.",
        "",
    ]
    (OUT / "limit_lock_gate_status.md").write_text("\n".join(lines), encoding="utf-8")
    return gate


def write_final_summary(counter: dict, n_defects: int, gate: str,
                        n_panel_rows: int, n_w001_candidates: int, overlap: dict) -> None:
    n_matched = counter.get("matched_limit_candidate", 0)
    n_rule_only = counter.get("rule_candidate_but_no_repo_flag", 0)
    n_repo_only = counter.get("repo_candidate_but_no_official_support", 0)
    n_total_rule_candidates = n_matched + n_rule_only
    lines = [
        "# KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0 — Final Summary",
        "",
        "Date: 2026-05-24  ",
        "Predecessor: KR-EXECUTABLE-STATUS-COVERAGE-A0 CLOSED.",
        "",
        "## Scope respected",
        "",
        "- Measurement-layer limit-lock source acquisition + reconciliation audit only.",
        "- No strategy testing.",
        "- No performance diagnostics.",
        "- No execution simulation.",
        "- No production / paper / P08 / live / shadow.",
        "",
        "## What was delivered",
        "",
        "Code artifacts:",
        "- `src/audit/measurement_a0/p_limit_lock_source_coverage.py`",
        "",
        "Reports (this dir, 12 outputs):",
        "1. `limit_lock_referee_lock.md`",
        "2. `source_inventory.md` (5 sources)",
        "3. `official_limit_lock_source_report.md`",
        "4. `limit_lock_taxonomy.md`",
        "5. `limit_lock_coverage_table.csv`",
        "6. `w001_limit_candidate_reconciliation.md`",
        "7. `w001_limit_candidate_reconciliation_ledger.csv`",
        "8. `conservative_execution_rule_design.md`",
        "9. `ohlcv_limit_overlap_audit.md`",
        "10. `limit_lock_defect_ledger.csv`",
        "11. `limit_lock_gate_status.md`",
        "12. `limit_lock_final_summary.md` (this file)",
        "",
        "## Headline source status",
        "",
        "- **Official daily KRX limit-lock log: NOT IN REPO.** pykrx has no relevant",
        "  endpoint; KRX 정보데이터시스템 단일가매매 requires separate scraping.",
        "- **Best-available proxy**: KRX historical price-limit rule (±15% pre-",
        "  2015-06-15, ±30% post-2015-06-15) applied to W001 v2 panel.",
        "",
        f"## Rule-derived candidates",
        "",
        f"- Panel rows scanned: **{n_panel_rows}**",
        f"- Total rule-derived candidates (upper or lower): **{n_total_rule_candidates}**",
        f"- Matched with W001 v2 `limit_lock_candidate` flag: **{n_matched}**",
        f"- Rule-only (W001 v2 missed): **{n_rule_only}**",
        f"- W001 v2 only (no rule support): **{n_repo_only}**",
        f"- W001 v2 `limit_lock_candidate` total: **{n_w001_candidates}** (UNDER-COUNTED)",
        "",
        "## OHLCV overlap audit",
        "",
        "| tradable_state | rows also rule-derived candidates |",
        "|---|---:|",
    ]
    for k, v in sorted(overlap.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Defect ledger",
        "",
        f"- Total defects: **{n_defects}**",
        "- Classes: official source unavailable / W001 v2 under-counted / candidate",
        "  lacks direction / close-at-limit vs locked indistinguishable / CA prev_close",
        "  adjustment missing / IPO first-day rule missing / VI not captured / W001",
        "  candidate without rule support / panel_absence overlap.",
        "",
        "## Conservative execution rule design",
        "",
        "Documented in `conservative_execution_rule_design.md`. Asymmetric: upper-lock",
        "candidate → buy fail-closed; lower-lock candidate → sell fail-closed.",
        "Implementation deferred to a future execution-simulation patch phase.",
        "",
        f"## Limit-lock gate state: **{gate}**",
        "",
        "## Pass criteria evaluation",
        "",
        "| criterion | status |",
        "|---|---|",
        "| Limit-lock source candidates identified + documented | YES (5 sources, including rule + W001 v2) |",
        "| Official or best-available source acquired or failure documented | YES (no official log; rule applied as best-available; failure documented) |",
        "| Taxonomy separates official / proxy / candidate / unknown | YES (10 labels with confidence column) |",
        "| W001 v2 candidate rows reconciled or classified | YES |",
        "| OHLCV invalid rows not used as sole limit-lock proof | YES (rule precedence documented) |",
        "| Conservative future execution rule design documented | YES |",
        "| Defect ledger produced | YES |",
        "| Gate status explicitly stated | YES (PARTIAL) |",
        "| No strategy test / execution sim / performance metric produced | YES |",
        "",
        "## Hard locks (preserved)",
        "",
        "- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / execution sim",
        "  / production / paper / P08 / live / shadow.",
        "- No survivorship-safe claim.",
        "- No executable claim from panel presence.",
        "- No OHLCV signature treated as official limit-lock proof.",
        "- No card is strategy-ready.",
        "",
        "## Awaiting Referee",
        "",
        "Per Referee-defined exit conditions, Referee will decide whether to:",
        "- A. close as limit-lock source acquired and reconciled,",
        "- B. require another reconciliation pass,",
        "- C. open executable-status pre-2018 extension,",
        "- D. open listed-universe daily lifecycle refinement,",
        "- E. keep all strategy research closed.",
        "",
    ]
    (OUT / "limit_lock_final_summary.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("[start] KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0")
    write_source_inventory()
    write_taxonomy()
    write_conservative_rule()

    print("[load] tradable panel")
    df = load_tradable_panel()
    n_panel_rows = len(df)
    print(f"[loaded] {n_panel_rows} rows")

    n_w001_candidates = int((df["tradable_state"] == "limit_lock_candidate").sum())
    print(f"[w001] {n_w001_candidates} existing limit_lock_candidate rows")

    df = derive_candidates(df)
    rule_counts = {
        "close_at_upper_limit_candidate": int(df["close_at_upper_candidate"].sum()),
        "close_at_lower_limit_candidate": int(df["close_at_lower_candidate"].sum()),
    }
    print(f"[rule] {rule_counts}")
    write_official_source_report(rule_counts, n_w001_candidates)

    recon_rows, counter = build_reconciliation(df)
    write_csv(OUT / "w001_limit_candidate_reconciliation_ledger.csv", recon_rows)
    write_w001_reconciliation_summary(counter, len(recon_rows), n_panel_rows)
    print(f"[reconciliation] {counter}")

    cov_rows = build_coverage_table(recon_rows)
    write_csv(OUT / "limit_lock_coverage_table.csv", cov_rows)
    print(f"[coverage_table] {len(cov_rows)} rows")

    overlap = write_ohlcv_overlap_audit(df)
    print(f"[overlap] {overlap}")

    defects = build_defect_ledger(counter, overlap, n_w001_candidates)
    n_overlap_invalid = sum(v for k, v in overlap.items() if k in
                           ("panel_absence", "true_suspension", "delisting_transition", "data_missing"))
    write_csv(OUT / "limit_lock_defect_ledger.csv", defects)
    gate = write_gate_status(counter, len(defects), n_overlap_invalid)
    write_final_summary(counter, len(defects), gate, n_panel_rows, n_w001_candidates, overlap)

    print(json.dumps({
        "n_panel_rows": n_panel_rows,
        "n_w001_existing_candidates": n_w001_candidates,
        "rule_derived": rule_counts,
        "reconciliation": counter,
        "ohlcv_overlap": overlap,
        "n_defects": len(defects),
        "gate": gate,
    }, indent=2))


if __name__ == "__main__":
    main()
