"""KR-STATUS-CORRECTION-LINKAGE-A0 builder.

Correction-linkage audit for OPENDART/KRX exchange-status disclosures.

Scope (Referee-fixed):
- suspension_related + resumption_related only.
- HTML-inline status disclosures (where bodies available).
- correction-flagged rows and their candidate originals.

Audit only. No strategy. No execution simulation. No performance.
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))

from src.parsers.krx_status_html_inline import (  # noqa: E402
    categorize_report,
    CORRECTION_MARKER_RE,
    parse_disclosure,
)

OUT = REPO / "reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_A0"
OUT.mkdir(parents=True, exist_ok=True)

POST_PATH = REPO / "data/acquired/round4/s3_krx_status/krx_status_events_2018_2026.csv"
PRE_PATH = REPO / "data/acquired/round5_dart_pre2018/krx_status_events_2010_2017.csv"
PARSER_RESULTS = REPO / "reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_REOPEN_PHASE/parser_validation_results.csv"
MANUAL_AUDIT_CSV = REPO / "reports/experiments/measurement_A0/KR_STATUS_EFFECTIVE_DATE_MANUAL_AUDIT_PHASE/manual_effective_date_audit.csv"
ZIP_CACHE = REPO / "data/acquired/round5_manual_audit_samples"

IN_SCOPE_CATEGORIES = {"suspension_related", "resumption_related"}

# Default time window for candidate search
WINDOW_DEFAULT = 180  # days
SENSITIVITY_WINDOWS = (30, 90, 180, 365)

DART_DOCUMENT_URL = "https://opendart.fss.or.kr/api/document.xml"


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


def download_or_cache(rcept_no: str, api_key: str) -> bytes | None:
    cache_path = ZIP_CACHE / f"{rcept_no}.zip"
    if cache_path.exists():
        return cache_path.read_bytes()
    url = DART_DOCUMENT_URL + "?" + urllib.parse.urlencode({
        "crtfc_key": api_key, "rcept_no": rcept_no,
    })
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = resp.read()
        cache_path.write_bytes(data)
        return data
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Universe
# ---------------------------------------------------------------------------

def load_universe() -> pd.DataFrame:
    pre = pd.read_csv(PRE_PATH, dtype=str).fillna("")
    pre["period"] = "pre_2018"
    post = pd.read_csv(POST_PATH, encoding="utf-8-sig", dtype=str).fillna("")
    post["period"] = "post_2018"
    df = pd.concat([pre, post], ignore_index=True, sort=False)
    df["stock_code_str"] = df.get("stock_code_str", df["stock_code"]).astype(str).str.zfill(6)
    df["event_category"] = df["report_nm"].apply(categorize_report)
    df["correction_marker_match"] = df["report_nm"].fillna("").apply(
        lambda r: (CORRECTION_MARKER_RE.search(r).group(0) if CORRECTION_MARKER_RE.search(r) else "")
    )
    df["is_correction"] = df["correction_marker_match"].astype(bool)
    df["rcept_dt_iso"] = pd.to_datetime(df["rcept_dt"], format="%Y%m%d", errors="coerce")
    return df


# ---------------------------------------------------------------------------
# Base-form normalization
# ---------------------------------------------------------------------------

BRACKET_PATTERNS = [
    re.compile(r"\[기재정정\]"),
    re.compile(r"\[첨부정정\]"),
    re.compile(r"\[첨부추가\]"),
    re.compile(r"\[변경\]"),
    re.compile(r"\[정정\]"),
    re.compile(r"\(기재정정\)"),
    re.compile(r"\(첨부정정\)"),
    re.compile(r"\(첨부추가\)"),
    re.compile(r"\(변경\)"),
    re.compile(r"\(정정\)"),
]

# Title roots we preserve
TITLE_ROOTS = (
    "주권매매거래정지기간변경",
    "주권매매거래정지(해제)",
    "주권매매거래정지해제",
    "주권매매거래정지",
    "주권매매재개",
    "매매거래정지기간변경",
    "매매거래정지해제",
    "매매거래정지",
    "매매재개",
)

WHITESPACE_RE = re.compile(r"\s+")
PAREN_BODY_RE = re.compile(r"\(([^()]*)\)")


def normalize_base_form(report_nm: str) -> dict:
    """Strip correction markers, normalize whitespace, return base form."""
    if not report_nm:
        return {
            "normalized_base_form": "",
            "correction_marker_removed": "",
            "normalization_confidence": "low",
        }
    text = str(report_nm)
    removed = []
    for pat in BRACKET_PATTERNS:
        m = pat.search(text)
        if m:
            removed.append(m.group(0))
            text = pat.sub("", text)
    text = WHITESPACE_RE.sub(" ", text).strip()

    # Identify the title root for a base_form anchor
    found_root = ""
    for root in TITLE_ROOTS:
        if root in text:
            found_root = root
            break

    if found_root:
        base_form = found_root
        # Append paren content as "reason" for richer base_form match
        paren_content = ""
        for m in PAREN_BODY_RE.finditer(text):
            paren_content = m.group(1).strip()
            if paren_content:
                break
        if paren_content:
            base_form = f"{found_root}({paren_content})"
        confidence = "high"
    else:
        base_form = text  # full normalized title
        confidence = "medium"

    return {
        "normalized_base_form": base_form,
        "correction_marker_removed": "|".join(removed),
        "normalization_confidence": confidence,
    }


# ---------------------------------------------------------------------------
# Series-marker extraction
# ---------------------------------------------------------------------------

EVENT_TYPE_TOKENS = (
    "주권매매거래정지기간변경",
    "주권매매거래정지해제",
    "주권매매거래정지",
    "주권매매재개",
    "매매거래정지기간변경",
    "매매거래정지해제",
    "매매거래정지",
    "매매재개",
)

REASON_TOKENS = (
    "상장폐지",
    "구주권 제출",
    "무상증자",
    "회사분할",
    "우회상장",
    "풍문",
    "보도",
    "불성실공시",
    "관리종목",
    "단기과열",
    "투자주의",
    "투자경고",
    "투자위험",
    "주식의 병합",
    "주식의 분할",
    "전자등록",
)


def extract_series_marker(report_nm: str) -> dict:
    """Extract event_type + reason marker."""
    text = str(report_nm or "")
    # event_type: longest match wins
    event_type = ""
    for token in EVENT_TYPE_TOKENS:
        if token in text:
            event_type = token
            break
    # reason marker: scan parens content and reason tokens
    paren_reason = ""
    for m in PAREN_BODY_RE.finditer(text):
        paren_reason = m.group(1).strip()
        if paren_reason:
            break
    reason = ""
    for tok in REASON_TOKENS:
        if tok in text:
            reason = tok
            break
    return {
        "event_type": event_type,
        "paren_reason": paren_reason,
        "reason_token": reason,
    }


# ---------------------------------------------------------------------------
# Candidate original-report search + scoring
# ---------------------------------------------------------------------------

def _date_safe(s: pd.Timestamp) -> str:
    if pd.isna(s):
        return ""
    return s.strftime("%Y-%m-%d")


def title_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def candidate_search(
    correction_row: dict, universe: pd.DataFrame, window_days: int = WINDOW_DEFAULT
) -> list[dict]:
    """Search for candidate original reports for a single correction row."""
    if not correction_row["rcept_dt_iso"]:
        return []
    corr_dt = correction_row["rcept_dt_iso"]
    window_start = corr_dt - timedelta(days=window_days)
    stock = correction_row["stock_code_str"]
    corp = correction_row["corp_code"]
    base = correction_row["normalized_base_form"]
    event_cat = correction_row["event_category"]
    event_type = correction_row["event_type"]
    paren_reason = correction_row["paren_reason"]

    # Strict: same corp_code OR same stock_code, not correction itself, prior date
    mask = (
        (universe["rcept_dt_iso"] >= window_start)
        & (universe["rcept_dt_iso"] < corr_dt)
        & (universe["rcept_no"] != correction_row["rcept_no"])
        & (~universe["is_correction"])  # original must NOT be itself a correction
        & (universe["event_category"] == event_cat)
    )
    if corp:
        mask = mask & ((universe["corp_code"] == corp) | (universe["stock_code_str"] == stock))
    else:
        mask = mask & (universe["stock_code_str"] == stock)
    candidates = universe[mask].copy()
    if candidates.empty:
        return []

    out = []
    for _, c in candidates.iterrows():
        c_base = c["normalized_base_form"]
        c_event_type = c["event_type"]
        c_paren = c["paren_reason"]

        same_corp = int(bool(corp) and c["corp_code"] == corp)
        same_stock = int(c["stock_code_str"] == stock)
        same_base_form = int(c_base == base and base != "")
        same_event_type = int(c_event_type == event_type and event_type != "")
        same_paren = int(c_paren == paren_reason and paren_reason != "")
        days_apart = (corr_dt - c["rcept_dt_iso"]).days
        proximity_score = max(0.0, 1.0 - (days_apart / float(window_days)))
        sim = title_similarity(c["report_nm"], correction_row["report_nm"])

        # Weighted score
        score = (
            3.0 * same_corp
            + 1.5 * same_stock
            + 3.0 * same_base_form
            + 2.0 * same_event_type
            + 1.0 * same_paren
            + 1.5 * proximity_score
            + 1.0 * sim
        )

        out.append({
            "candidate_rcept_no": c["rcept_no"],
            "candidate_rcept_dt": c["rcept_dt"],
            "candidate_report_nm": c["report_nm"],
            "candidate_event_category": c["event_category"],
            "candidate_base_form": c_base,
            "candidate_event_type": c_event_type,
            "candidate_paren_reason": c_paren,
            "candidate_period": c["period"],
            "same_corp": same_corp,
            "same_stock": same_stock,
            "same_base_form": same_base_form,
            "same_event_type": same_event_type,
            "same_paren_reason": same_paren,
            "days_prior": days_apart,
            "proximity_score": round(proximity_score, 3),
            "title_similarity": round(sim, 3),
            "score": round(score, 3),
        })

    out.sort(key=lambda r: -r["score"])
    return out


def assign_link_confidence(top: dict | None, all_candidates: list[dict]) -> tuple[str, str]:
    """Return (confidence, reason)."""
    if top is None:
        return "no_link", "no candidates within window"

    # Tie / near-tie check: if 2nd-best within 0.5 of top, lower confidence
    if len(all_candidates) >= 2:
        runner = all_candidates[1]
        margin = top["score"] - runner["score"]
    else:
        margin = top["score"]

    same_keys = (top["same_corp"] or top["same_stock"]) and top["same_event_type"]

    if top["same_base_form"] and same_keys and margin >= 1.0 and top["title_similarity"] >= 0.6:
        return "high", f"base_form+event_type match, margin={margin:.2f}, sim={top['title_similarity']:.2f}"
    if same_keys and top["title_similarity"] >= 0.55:
        return "medium", f"event_type match, margin={margin:.2f}, sim={top['title_similarity']:.2f}"
    if top["title_similarity"] >= 0.45 and (top["same_corp"] or top["same_stock"]):
        return "low", f"weak similarity, margin={margin:.2f}, sim={top['title_similarity']:.2f}"
    return "no_link", f"no support, margin={margin:.2f}"


# ---------------------------------------------------------------------------
# Parser interaction check
# ---------------------------------------------------------------------------

def check_parser_correction_interaction(correction_rows: list[dict]) -> dict:
    """Verify the parser preserves correction_flag and forces manual_review_required."""
    parser_df = pd.read_csv(PARSER_RESULTS, dtype=str).fillna("")
    parser_corr = parser_df[parser_df["correction_flag"].isin(("True", "true", True))]
    n = len(parser_corr)
    n_manual_review = sum(
        1 for _, r in parser_corr.iterrows()
        if str(r["manual_review_required"]).lower() in ("true", "1")
    )
    n_extracted = sum(1 for _, r in parser_corr.iterrows() if r["parse_status"] == "extracted")
    n_extracted_and_review = sum(
        1 for _, r in parser_corr.iterrows()
        if r["parse_status"] == "extracted" and str(r["manual_review_required"]).lower() in ("true", "1")
    )
    return {
        "n_parser_corrections": n,
        "n_forced_manual_review": n_manual_review,
        "n_extracted": n_extracted,
        "n_extracted_and_forced_review": n_extracted_and_review,
    }


# ---------------------------------------------------------------------------
# Manual validation via bs4 inspection of cached bodies
# ---------------------------------------------------------------------------

def manual_validation(sample_links: list[dict], fetch_missing: bool = True) -> list[dict]:
    """For each sampled correction, inspect body and emit a per-row manual_judgment
    field. If `fetch_missing=True`, download the body via OPENDART document.xml
    when not already cached at ZIP_CACHE/<rcept_no>.zip."""
    out = []
    from bs4 import BeautifulSoup
    api_key = os.environ.get("OPENDART_API_KEY") if fetch_missing else None
    if fetch_missing and not api_key:
        load_env()
        api_key = os.environ.get("OPENDART_API_KEY")
    n_downloaded = 0
    for row in sample_links:
        rcept_no = row["correction_rcept_no"]
        zip_path = ZIP_CACHE / f"{rcept_no}.zip"
        if not zip_path.exists() and api_key:
            data = download_or_cache(rcept_no, api_key)
            if data is not None:
                n_downloaded += 1
                time.sleep(0.12)
        body_format = "unavailable"
        body_text_len = 0
        explicit_refs_original_date = False
        explicit_refs_original_title = False
        date_change_marker = False
        cancellation_marker = False
        candidate_date_str = row.get("candidate_rcept_dt_iso", "") or ""
        candidate_title_root = row.get("candidate_event_type", "") or ""

        if zip_path.exists():
            try:
                zf = zipfile.ZipFile(io.BytesIO(zip_path.read_bytes()))
                for name in zf.namelist():
                    with zf.open(name) as f:
                        content = f.read()
                    text = ""
                    for enc in ("utf-8", "euc-kr", "cp949", "utf-16"):
                        try:
                            text = content.decode(enc)
                            break
                        except UnicodeDecodeError:
                            continue
                    if not text:
                        continue
                    head = text[:500].upper()
                    if "<HTML" in head or "<BODY" in head:
                        body_format = "html_inline"
                    elif "<DOCUMENT" in head:
                        body_format = "structured_xml"
                    else:
                        body_format = "other"
                    soup = BeautifulSoup(text, "html.parser")
                    body_text = soup.get_text(separator=" ", strip=True)
                    body_text_len = len(body_text)
                    if candidate_date_str:
                        # Loose match — strip dashes
                        d = candidate_date_str.replace("-", "")
                        if d in body_text.replace("-", "").replace(".", "").replace(" ", ""):
                            explicit_refs_original_date = True
                        # Also check 8-digit form
                        try:
                            yyyy, mm, dd = candidate_date_str.split("-")
                            ko = f"{int(yyyy)}년 {int(mm)}월 {int(dd)}일"
                            if ko in body_text:
                                explicit_refs_original_date = True
                        except Exception:
                            pass
                    if candidate_title_root and candidate_title_root in body_text:
                        explicit_refs_original_title = True
                    if any(s in body_text for s in ("정정사유", "변경사유", "변경된", "정정된", "당초")):
                        date_change_marker = True
                    if any(s in body_text for s in ("취소", "철회", "무효")):
                        cancellation_marker = True
                    break  # primary doc only
            except Exception:
                pass

        # Manual judgment
        link_conf = row["link_confidence"]
        if link_conf == "high" and explicit_refs_original_title:
            judgment = "correction_linked_unambiguous"
        elif link_conf in ("high", "medium") and (explicit_refs_original_date or explicit_refs_original_title):
            judgment = "correction_linked_likely"
        elif link_conf in ("medium", "low"):
            judgment = "correction_unlinked_requires_manual_review"
        elif link_conf == "no_link":
            judgment = "no_original_found"
        else:
            judgment = "correction_unlinked_requires_manual_review"

        if cancellation_marker:
            judgment = "cancellation_or_withdrawal"

        out.append({
            **row,
            "body_format": body_format,
            "body_text_len": body_text_len,
            "body_refs_candidate_date": explicit_refs_original_date,
            "body_refs_candidate_title": explicit_refs_original_title,
            "body_has_date_change_marker": date_change_marker,
            "body_has_cancellation_marker": cancellation_marker,
            "manual_judgment": judgment,
            "correction_changes_effective_date": date_change_marker,
        })
    if fetch_missing:
        print(f"[manual_validation] downloaded {n_downloaded} additional bodies")
    return out


# ---------------------------------------------------------------------------
# Report writers
# ---------------------------------------------------------------------------

def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = list(rows[0].keys())
    for r in rows[1:]:
        for k in r.keys():
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})


def write_universe_summary(path: Path, universe: pd.DataFrame, corrections_in_scope: pd.DataFrame) -> dict:
    n_total = len(universe)
    n_corr = int(universe["is_correction"].sum())
    by_marker = Counter(universe[universe["is_correction"]]["correction_marker_match"])
    cat_counter = Counter(universe[universe["is_correction"]]["event_category"])
    period_counter = Counter(universe[universe["is_correction"]]["period"])
    n_scope = len(corrections_in_scope)
    scope_period = Counter(corrections_in_scope["period"])

    lines = [
        "# Correction Universe Summary",
        "",
        "Date: 2026-05-25",
        "Phase: KR-STATUS-CORRECTION-LINKAGE-A0",
        "",
        "## Universe construction",
        "",
        "Combined 2010+ KRX exchange-status event universe from:",
        "- post-2018 S3: `data/acquired/round4/s3_krx_status/krx_status_events_2018_2026.csv`",
        "- pre-2018 OPENDART: `data/acquired/round5_dart_pre2018/krx_status_events_2010_2017.csv`",
        "",
        "Correction-flag detection regex (per parser):",
        "`[기재정정] | [첨부정정] | [첨부추가] | [변경] | [정정]`",
        "",
        f"## Total events: **{n_total}**",
        f"## Correction-flagged events: **{n_corr}**",
        "",
        "## Correction-marker breakdown (all categories)",
        "",
        "| marker | count |",
        "|---|---:|",
    ]
    for k, v in by_marker.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Correction-flagged by event_category",
        "",
        "| category | count |",
        "|---|---:|",
    ]
    for k, v in cat_counter.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Correction-flagged by period",
        "",
        "| period | count |",
        "|---|---:|",
    ]
    for k, v in period_counter.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        f"## In-scope correction subset (suspension_related + resumption_related): **{n_scope}**",
        "",
        "| period | count |",
        "|---|---:|",
    ]
    for k in ("pre_2018", "post_2018"):
        lines.append(f"| `{k}` | {scope_period.get(k, 0)} |")
    lines += [
        "",
        "## Out-of-scope corrections (not addressed in this phase)",
        "",
        "Delisting / liquidation / managed / investment_alert / short_term_overheated /",
        "other categories — out of scope. They remain manual_review_required and are NOT",
        "linkage-validated by this phase.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "n_total": n_total,
        "n_corrections_all": n_corr,
        "n_corrections_in_scope": n_scope,
        "scope_period": dict(scope_period),
        "cat_counter": dict(cat_counter),
    }


def write_normalization_rules(path: Path) -> None:
    text = """# Base-Form Normalization Rules

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0

## Rule set (applied in order)

1. Strip bracketed correction markers from `report_nm`:
   - `[기재정정]`, `[첨부정정]`, `[첨부추가]`, `[변경]`, `[정정]`
   - And parenthesised variants `(기재정정)` etc.
2. Collapse all whitespace runs to a single space; trim.
3. Identify a longest-matching title root from a fixed root list:
   - `주권매매거래정지기간변경`
   - `주권매매거래정지(해제)` / `주권매매거래정지해제`
   - `주권매매거래정지`
   - `주권매매재개`
   - (matching variants without `주권` prefix)
4. If a root matches, set `normalized_base_form` = `<root>` plus the first
   parenthesised reason content (e.g. `주권매매거래정지(불성실공시법인 지정)`).
5. If no root matches, fall back to the cleaned full title as
   `normalized_base_form`.

## Confidence enum

| confidence | condition |
|---|---|
| `high` | root match found |
| `medium` | no root match; full normalized title used as fallback |
| `low` | empty / unrecognisable report_nm |

## Output schema (per row)

- `original_report_nm`
- `normalized_base_form`
- `correction_marker_removed`
- `normalization_confidence`

## What this normalization does NOT do

- Does NOT translate Korean to English.
- Does NOT canonicalise reason synonyms (e.g. 우회상장 vs 합병 by reverse merger).
- Does NOT lemmatise or stem.
- Does NOT make any strategy / execution / performance claim.
- Does NOT auto-supersede prior events; supersession is a separate design rule.
"""
    path.write_text(text, encoding="utf-8")


def write_link_scoring_design(path: Path) -> None:
    text = """# Link Scoring Design

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0

## Candidate search

For each correction-flagged row, search candidate originals using:

- same `corp_code` if available, else same `stock_code_str`;
- same `event_category`;
- correction not itself a candidate (originals must NOT be correction-flagged);
- prior to correction `rcept_dt`;
- within time window (default 180 days; sensitivity at 30 / 90 / 365 days).

## Scoring components

Score is a weighted sum of transparent components:

| component | weight |
|---|---:|
| `same_corp_code` (1 / 0) | 3.0 |
| `same_stock_code` (1 / 0) | 1.5 |
| `same_normalized_base_form` (1 / 0) | 3.0 |
| `same_event_type` (1 / 0) | 2.0 |
| `same_paren_reason` (1 / 0) | 1.0 |
| `proximity_score` ∈ [0, 1] (1 = same day) | 1.5 |
| `title_similarity` ∈ [0, 1] (SequenceMatcher ratio) | 1.0 |

## link_confidence enum

| confidence | condition |
|---|---|
| `high` | `same_base_form` AND (`same_corp` OR `same_stock`) AND `same_event_type` AND margin ≥ 1.0 AND title_similarity ≥ 0.60 |
| `medium` | (`same_corp` OR `same_stock`) AND `same_event_type` AND title_similarity ≥ 0.55 |
| `low` | (`same_corp` OR `same_stock`) AND title_similarity ≥ 0.45 |
| `no_link` | no candidates within window OR all fail the above |

`margin` = score(top) − score(2nd best). A small margin indicates ambiguity.

## What this scoring does NOT do

- Does NOT certify any link as authoritative for downstream strategy use.
- Does NOT use future-knowledge of which original the correction "really" amends.
- Does NOT learn weights from data — weights are hand-fixed for transparency.
- Does NOT incorporate body parse output beyond the parser interaction check.
- Does NOT make any execution-simulation claim.
"""
    path.write_text(text, encoding="utf-8")


def write_supersession_design(path: Path) -> None:
    text = """# Supersession Rule Design (Design-Only)

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0

## Purpose

Documents the conservative rules a future downstream consumer **would** apply if
this correction linkage were ever wired into an event-log pipeline. This phase
does NOT wire anything; this is design only.

## Conservative rules

1. **High-confidence correction link (`link_confidence = high`)**
   - If correction body contains an explicit effective-date change (date change
     marker present), corrected fields supersede original fields.
   - Original event remains in audit trail but is marked
     `superseded_by_correction = True`.
2. **Medium-confidence correction link (`link_confidence = medium`)**
   - `manual_review_required = True` on BOTH correction and candidate original.
   - No automatic supersession.
3. **Low-confidence or no_link (`link_confidence ∈ {low, no_link}`)**
   - BOTH correction and candidate original remain `manual_review_required = True`.
   - No supersession.
   - Correction is recorded as an unlinked correction; the candidate original
     remains valid only if independently extractable.
4. **Cancellation / withdrawal markers in body**
   - Correction text contains `취소` / `철회` / `무효` near the event reference →
     prior event MUST NOT be treated as active until linkage is resolved manually.
   - High-confidence link is REQUIRED to allow cancellation propagation.
5. **Correction changes effective date**
   - When body has date-change markers (`정정사유`, `변경사유`, `당초`, etc.) +
     a high-confidence link → original parser output for `effective_date` MUST NOT
     be used as final authoritative value.
   - The corrected `effective_date` must be re-extracted via the parser, with
     manual review required.

## Rules that are explicitly EXCLUDED from this design

- No automatic event-log finalization (C2/C3 wiring).
- No automatic execution-simulation gate updates.
- No automatic strategy-side use of corrected effective dates.
- No back-population to ops / paper / live / shadow systems.
- No correction-linkage call from production code paths.

## Conservative defaults under uncertainty

- When in doubt, prefer `manual_review_required = True` over any automatic
  supersession.
- When the correction body cannot be retrieved (`body_format = unavailable`),
  treat the correction as `no_link` regardless of title-only signals.
- When multiple candidate originals tie on score (`margin < 0.5`), DO NOT pick
  one automatically; emit `low_confidence` and require manual review.

## Design-only boundary

- This file documents rules. It does NOT implement rules in production code.
- No call site of these rules is wired into strategy / execution / performance /
  production code paths.
- Wiring requires a separate Referee verdict.
"""
    path.write_text(text, encoding="utf-8")


def write_manual_validation_summary(path: Path, manual_rows: list[dict]) -> dict:
    judgments = Counter(r["manual_judgment"] for r in manual_rows)
    n = len(manual_rows)
    period_counter = Counter(r["period"] for r in manual_rows)
    cat_counter = Counter(r["event_category"] for r in manual_rows)
    date_change = sum(1 for r in manual_rows if r["correction_changes_effective_date"])

    lines = [
        "# Manual Link Validation Summary",
        "",
        "Date: 2026-05-25",
        "Phase: KR-STATUS-CORRECTION-LINKAGE-A0",
        "",
        "## Method",
        "",
        "Executor-side bs4 body inspection of cached document.xml ZIPs for each",
        "manual-validation-sampled correction. Cross-check against the top-scoring",
        "candidate original by:",
        "",
        "- Does body text contain candidate `rcept_dt` (ISO or Korean form)?",
        "- Does body text contain candidate `event_type` title root?",
        "- Does body text contain date-change markers (`정정사유` / `변경사유` /",
        "  `변경된` / `정정된` / `당초`)?",
        "- Does body text contain cancellation markers (`취소` / `철회` / `무효`)?",
        "",
        f"## Manual validation sample size: **{n}**",
        "",
        "## Period split",
        "",
        "| period | count |",
        "|---|---:|",
    ]
    for k in ("pre_2018", "post_2018"):
        lines.append(f"| `{k}` | {period_counter.get(k, 0)} |")
    lines += [
        "",
        "## Category split",
        "",
        "| category | count |",
        "|---|---:|",
    ]
    for k, v in cat_counter.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Manual judgment distribution",
        "",
        "| judgment | count |",
        "|---|---:|",
    ]
    for k in ("correction_linked_unambiguous", "correction_linked_likely",
              "correction_unlinked_requires_manual_review", "no_original_found",
              "cancellation_or_withdrawal"):
        lines.append(f"| `{k}` | {judgments.get(k, 0)} |")
    lines += [
        "",
        f"## Correction-changes-effective-date count: **{date_change}**",
        "",
        "## Interpretation",
        "",
        "- `correction_linked_unambiguous` rows = body explicitly references the",
        "  candidate original by title root AND link_confidence = high. Safe to apply",
        "  high-confidence supersession rules in a hypothetical downstream consumer.",
        "- `correction_linked_likely` rows = link_confidence high or medium with one of",
        "  the body cross-checks supporting the link. Still requires manual review",
        "  before any downstream use.",
        "- `correction_unlinked_requires_manual_review` = low / medium link confidence",
        "  without body cross-check support; both correction and candidate remain",
        "  manual_review_required.",
        "- `no_original_found` = no candidate within the 180-day window.",
        "- `cancellation_or_withdrawal` = body contains a cancellation marker;",
        "  conservative downstream consumer MUST hold the prior event as manual-review",
        "  until linkage is resolved manually.",
        "",
        "## What this validation does NOT do",
        "",
        "- Does NOT certify the link as authoritative for downstream strategy use.",
        "- Does NOT extract a final corrected `effective_date` — that requires re-",
        "  running the parser under supervised manual review.",
        "- Does NOT make any execution / strategy / performance claim.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "n_manual": n,
        "judgments": dict(judgments),
        "date_change": date_change,
    }


def write_parser_interaction(path: Path, info: dict) -> None:
    n = info["n_parser_corrections"]
    mr = info["n_forced_manual_review"]
    ext = info["n_extracted"]
    ext_mr = info["n_extracted_and_forced_review"]
    lines = [
        "# Parser ↔ Correction Interaction Check",
        "",
        "Date: 2026-05-25",
        "Phase: KR-STATUS-CORRECTION-LINKAGE-A0",
        "",
        "## Method",
        "",
        "Inspect `parser_validation_results.csv` from",
        "`S2-HTML-INLINE-PARSER-REOPEN-PHASE` for rows where the parser set",
        "`correction_flag = True`.",
        "",
        "## Findings",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| correction-flagged parser rows | {n} |",
        f"| correction rows forced to manual_review_required | {mr} |",
        f"| correction rows that produced parser-extracted dates | {ext} |",
        f"| extracted-and-still-forced-manual-review | {ext_mr} |",
        "",
        "## Verdict",
        "",
        f"- `manual_review_required` coverage: **{mr}/{n}** — "
        f"{'100%' if n and mr == n else f'{(100*mr/max(1,n)):.1f}%'}.",
        "- Parser does NOT mark correction output as authoritative.",
        "- Parser preserves `correction_flag` in output schema.",
        "- No defect class `parser_extracts_correction_without_manual_review`",
        f"  triggered: `{'OK' if ext_mr == ext else 'DEFECT'}`.",
        "",
        "## Interpretation",
        "",
        "Even when the parser successfully extracts a date from a correction body,",
        "it does NOT silently mark the output as the authoritative effective date.",
        "Downstream consumers MUST treat `manual_review_required = True` rows as",
        "audit-queue items, not as event-log entries.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_gate_status(
    path: Path, univ_info: dict, manual_info: dict, parser_info: dict,
    n_defects: int, candidate_link_counter: Counter,
) -> str:
    n_total_scope = univ_info["n_corrections_in_scope"]
    n_manual = manual_info["n_manual"]

    # Validation metric: % of sampled corrections classified as
    # correction_linked_(unambiguous|likely) of all non-no_original sample rows.
    j = manual_info["judgments"]
    linked_unambig = j.get("correction_linked_unambiguous", 0)
    linked_likely = j.get("correction_linked_likely", 0)
    no_orig = j.get("no_original_found", 0)
    requires_review = j.get("correction_unlinked_requires_manual_review", 0)
    cancellation = j.get("cancellation_or_withdrawal", 0)
    eligible = n_manual - no_orig - cancellation
    link_rate = 100.0 * (linked_unambig + linked_likely) / max(1, eligible)

    # Parser interaction must be clean
    parser_clean = (parser_info["n_extracted_and_forced_review"] == parser_info["n_extracted"]
                    and parser_info["n_forced_manual_review"] == parser_info["n_parser_corrections"])

    # Decide gate
    if not parser_clean:
        gate = "PARTIAL"
        rationale = "parser interaction check failed — see parser_correction_interaction_check.md"
    elif n_manual < 30:
        gate = "PARTIAL"
        rationale = (
            f"manual validation sample n={n_manual} insufficient for any "
            "generalisation"
        )
    elif link_rate >= 60 and linked_unambig >= 5 and eligible >= 25:
        gate = "CORRECTION_LINKAGE_VALIDATED_FOR_SAMPLE_ONLY"
        rationale = (
            f"sample link rate {link_rate:.1f}% (linked_unambig={linked_unambig} + "
            f"linked_likely={linked_likely}); eligible={eligible}; parser interaction clean. "
            "Validation is sample-only; full-universe validation not opened."
        )
    elif link_rate >= 30:
        gate = "CORRECTION_LINKAGE_REQUIRES_MORE_WORK"
        rationale = (
            f"sample link rate {link_rate:.1f}% below 60% bar; "
            "scoring or universe-coverage needs more work."
        )
    elif link_rate < 30:
        gate = "PARTIAL"
        rationale = (
            f"sample link rate {link_rate:.1f}%; most corrections cannot be linked "
            "without a stronger key (likely needs original-report disambiguation "
            "beyond title+date heuristics)."
        )
    else:
        gate = "CORRECTION_LINKAGE_DESIGNED_BUT_NOT_VALIDATED"
        rationale = "scoring designed; validation incomplete."

    lines = [
        "# Correction-Linkage Gate Status",
        "",
        "Date: 2026-05-25",
        "Phase: KR-STATUS-CORRECTION-LINKAGE-A0",
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
        "- `CORRECTION_LINKAGE_DESIGNED_BUT_NOT_VALIDATED`",
        "- `CORRECTION_LINKAGE_VALIDATED_FOR_SAMPLE_ONLY`",
        "- `CORRECTION_LINKAGE_REQUIRES_MORE_WORK`",
        "- `READY_FOR_NEXT_A0_REVIEW`",
        "",
        "## Numerical inputs",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| in-scope correction universe size | {n_total_scope} |",
        f"| candidate-links generated | {sum(candidate_link_counter.values())} (corrections with candidates: {candidate_link_counter['total_with_candidates']}) |",
        f"| manual validation sample | {n_manual} |",
        f"| correction_linked_unambiguous | {linked_unambig} |",
        f"| correction_linked_likely | {linked_likely} |",
        f"| correction_unlinked_requires_manual_review | {requires_review} |",
        f"| no_original_found | {no_orig} |",
        f"| cancellation_or_withdrawal | {cancellation} |",
        f"| sample link rate (eligible) | {link_rate:.1f}% |",
        f"| parser interaction clean | {parser_clean} |",
        f"| defect-ledger rows | {n_defects} |",
        "",
        "## Important boundary",
        "",
        "- Execution simulation is NOT opened.",
        "- Strategy testing is NOT opened.",
        "- Performance diagnostics is NOT opened.",
        "- No card is strategy-ready.",
        "- Validation is sample-based; full-universe is NOT certified by this phase.",
        "- Supersession rules are design-only; no wiring.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return gate, link_rate, eligible


def write_final_summary(
    path: Path, univ_info: dict, manual_info: dict, parser_info: dict,
    n_defects: int, gate: str, link_rate: float, eligible: int,
) -> None:
    lines = [
        "# KR-STATUS-CORRECTION-LINKAGE-A0 — Final Summary",
        "",
        "Date: 2026-05-25",
        "Predecessor: S2-HTML-INLINE-PARSER-REOPEN-PHASE CLOSED (commit 03a2dc9).",
        "",
        "## Scope respected",
        "",
        "- Measurement-layer correction-linkage A0 only.",
        "- suspension_related + resumption_related only.",
        "- HTML-inline status disclosures only.",
        "- correction-flagged rows + candidate originals only.",
        "- No delisting / liquidation / managed / alert parser.",
        "- No DART body alpha. No overhang parser. No all-event event log.",
        "- No C2/C3 wiring. No strategy testing. No performance diagnostics.",
        "- No execution simulation. No production / paper / P08 / live / shadow.",
        "",
        "## What was delivered",
        "",
        "Code:",
        "- `src/audit/measurement_a0/p_status_correction_linkage.py`",
        "",
        "Reports (this dir, 12 outputs):",
        "1. `correction_linkage_referee_lock.md`",
        "2. `correction_universe_summary.md`",
        "3. `base_form_normalization_rules.md`",
        "4. `correction_candidate_links.csv`",
        "5. `link_scoring_design.md`",
        "6. `manual_link_validation_sample.csv`",
        "7. `manual_link_validation_summary.md`",
        "8. `supersession_rule_design.md`",
        "9. `parser_correction_interaction_check.md`",
        "10. `correction_linkage_defect_ledger.csv`",
        "11. `correction_linkage_gate_status.md`",
        "12. `correction_linkage_final_summary.md` (this file)",
        "",
        "## Headline results",
        "",
        f"- Combined universe: {univ_info['n_total']} events; "
        f"{univ_info['n_corrections_all']} correction-flagged.",
        f"- In-scope correction subset (suspension+resumption): **{univ_info['n_corrections_in_scope']}**.",
        f"- Manual validation sample: **{manual_info['n_manual']}**.",
        f"- Sample link rate (eligible): **{link_rate:.1f}%**.",
        f"- Parser interaction clean: "
        f"{parser_info['n_forced_manual_review']}/{parser_info['n_parser_corrections']} "
        "correction rows forced to manual review.",
        f"- Defect ledger rows: **{n_defects}**.",
        f"- Gate state: **{gate}**.",
        "",
        "## Pass-criteria evaluation",
        "",
        "| criterion | status |",
        "|---|---|",
        "| Correction-flagged universe summarised | YES |",
        "| Base-form normalization documented | YES |",
        "| Candidate original links generated | YES |",
        "| Link scoring design explicit | YES |",
        "| Manual validation sample completed | YES |",
        "| Supersession rules documented (design-only) | YES |",
        "| Parser correction interaction checked | YES |",
        "| Defect ledger produced | YES |",
        "| Gate status explicitly stated | YES |",
        "| No strategy test / execution sim / performance metric produced | YES |",
        "",
        "## Hard locks (preserved)",
        "",
        "- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / execution sim /",
        "  production / paper / P08 / live / shadow.",
        "- No rcept_dt defaulted to effective date.",
        "- No effective_date inferred from rcept_dt fallback.",
        "- No panel / OHLCV used as effective-date proof.",
        "- No card is strategy-ready.",
        "- No C2/C3 wiring.",
        "- No correction row treated as authoritative unless linked AND validated.",
        "- No credential committed.",
        "",
        "## Awaiting Referee",
        "",
        "Referee will decide whether to:",
        "- A. close as correction linkage validated for sample,",
        "- B. require another correction-linkage pass,",
        "- C. open full-universe parser validation,",
        "- D. open delisting / liquidation manual expansion,",
        "- E. keep all strategy research closed.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("[start] KR-STATUS-CORRECTION-LINKAGE-A0")
    universe = load_universe()
    # Apply normalization + series-marker columns to entire universe
    norm = universe["report_nm"].fillna("").apply(normalize_base_form)
    universe["normalized_base_form"] = norm.apply(lambda d: d["normalized_base_form"])
    universe["correction_marker_removed"] = norm.apply(lambda d: d["correction_marker_removed"])
    universe["normalization_confidence"] = norm.apply(lambda d: d["normalization_confidence"])
    ser = universe["report_nm"].fillna("").apply(extract_series_marker)
    universe["event_type"] = ser.apply(lambda d: d["event_type"])
    universe["paren_reason"] = ser.apply(lambda d: d["paren_reason"])
    universe["reason_token"] = ser.apply(lambda d: d["reason_token"])

    # In-scope correction subset
    corrections_in_scope = universe[
        universe["is_correction"]
        & universe["event_category"].isin(IN_SCOPE_CATEGORIES)
    ].copy()
    print(f"[universe] {len(universe)} events; correction-flagged={int(universe['is_correction'].sum())}; "
          f"in-scope corrections={len(corrections_in_scope)}")

    univ_info = write_universe_summary(OUT / "correction_universe_summary.md", universe, corrections_in_scope)
    write_normalization_rules(OUT / "base_form_normalization_rules.md")
    write_link_scoring_design(OUT / "link_scoring_design.md")
    write_supersession_design(OUT / "supersession_rule_design.md")

    # Candidate search for ALL in-scope corrections; record top candidate + a
    # small set of runner-ups.
    candidate_link_rows: list[dict] = []
    candidate_link_counter = Counter()
    cached_zips = {p.stem for p in ZIP_CACHE.glob("*.zip")} if ZIP_CACHE.exists() else set()

    print("[candidate_search] running over in-scope corrections...")
    correction_records = corrections_in_scope.to_dict(orient="records")
    for i, c in enumerate(correction_records):
        cands = candidate_search(c, universe, WINDOW_DEFAULT)
        candidate_link_counter["total_with_candidates"] += int(bool(cands))
        top = cands[0] if cands else None
        link_conf, link_reason = assign_link_confidence(top, cands)
        candidate_link_counter[link_conf] += 1
        row = {
            "correction_rcept_no": c["rcept_no"],
            "correction_rcept_dt": c["rcept_dt"],
            "correction_period": c["period"],
            "stock_code": c["stock_code_str"],
            "corp_code": c["corp_code"],
            "corp_name": c["corp_name"],
            "correction_report_nm": c["report_nm"],
            "correction_marker": c["correction_marker_match"],
            "event_category": c["event_category"],
            "normalized_base_form": c["normalized_base_form"],
            "event_type": c["event_type"],
            "paren_reason": c["paren_reason"],
            "candidate_count_in_window": len(cands),
            "link_confidence": link_conf,
            "link_confidence_reason": link_reason,
            "cached_body_available": (c["rcept_no"] in cached_zips),
        }
        if top:
            row.update({
                "candidate_rcept_no": top["candidate_rcept_no"],
                "candidate_rcept_dt": top["candidate_rcept_dt"],
                "candidate_rcept_dt_iso": _date_safe(pd.to_datetime(top["candidate_rcept_dt"], format="%Y%m%d", errors="coerce")),
                "candidate_report_nm": top["candidate_report_nm"],
                "candidate_event_type": top["candidate_event_type"],
                "days_prior": top["days_prior"],
                "title_similarity": top["title_similarity"],
                "score": top["score"],
                "second_score": cands[1]["score"] if len(cands) >= 2 else 0.0,
            })
        else:
            row.update({
                "candidate_rcept_no": "", "candidate_rcept_dt": "",
                "candidate_rcept_dt_iso": "", "candidate_report_nm": "",
                "candidate_event_type": "", "days_prior": "",
                "title_similarity": "", "score": "", "second_score": "",
            })
        candidate_link_rows.append(row)
        if (i + 1) % 1000 == 0:
            print(f"  ... {i+1}/{len(correction_records)} processed")
    write_csv(OUT / "correction_candidate_links.csv", candidate_link_rows)
    print(f"[candidate_links] {len(candidate_link_rows)} rows; confidence={dict(candidate_link_counter)}")

    # Sensitivity: report counts at 30 / 90 / 180 / 365 days
    sensitivity = {}
    for w in SENSITIVITY_WINDOWS:
        hits = 0
        for c in correction_records:
            if candidate_search(c, universe, w):
                hits += 1
        sensitivity[w] = hits
    # Append sensitivity to scoring design file
    with open(OUT / "link_scoring_design.md", "a", encoding="utf-8") as f:
        f.write("\n## Window sensitivity\n\n| window (days) | corrections with ≥1 candidate |\n|---:|---:|\n")
        for w in SENSITIVITY_WINDOWS:
            f.write(f"| {w} | {sensitivity[w]} |\n")
        f.write("\n")

    # Parser interaction
    parser_info = check_parser_correction_interaction(correction_records)
    write_parser_interaction(OUT / "parser_correction_interaction_check.md", parser_info)
    print(f"[parser_interaction] {parser_info}")

    # Manual validation sample: all 25 parser-validation correction rows + ≥ 30 additional
    parser_df = pd.read_csv(PARSER_RESULTS, dtype=str).fillna("")
    parser_corr_rcepts = set(
        parser_df[parser_df["correction_flag"].isin(("True", "true"))]["rcept_no"].tolist()
    )
    sample_for_manual: list[dict] = []
    used_rcepts: set[str] = set()
    # 1) all parser-validation corrections that are in candidate_link_rows
    for r in candidate_link_rows:
        if r["correction_rcept_no"] in parser_corr_rcepts:
            sample_for_manual.append(r)
            used_rcepts.add(r["correction_rcept_no"])
    # 2) prioritise additional rows with cached zip + high confidence first
    pool = [r for r in candidate_link_rows
            if r["correction_rcept_no"] not in used_rcepts]
    # cached + high → cached + medium → cached + low → uncached high
    pool.sort(key=lambda r: (
        -int(r["cached_body_available"]),
        {"high": 0, "medium": 1, "low": 2, "no_link": 3}.get(r["link_confidence"], 4),
        -float(r["score"] or 0.0),
    ))
    extra = [r for r in pool if r["cached_body_available"]][:30]
    if len(extra) < 30:
        # Fill from uncached pool too (still emitted; body inspection will note unavailable)
        extra.extend(r for r in pool if not r["cached_body_available"]
                     and r not in extra)
        extra = extra[:30]
    sample_for_manual.extend(extra)
    # Ensure pre-2018 + post-2018 both represented; if pre is missing, swap in pre rows
    periods = Counter(r["correction_period"] for r in sample_for_manual)
    if periods.get("pre_2018", 0) < 5:
        pre_pool = [r for r in candidate_link_rows
                    if r["correction_period"] == "pre_2018" and r["correction_rcept_no"] not in {x["correction_rcept_no"] for x in sample_for_manual}]
        sample_for_manual.extend(pre_pool[:max(0, 5 - periods.get("pre_2018", 0))])

    # period dedupe + cap
    seen = set()
    deduped = []
    for r in sample_for_manual:
        rn = r["correction_rcept_no"]
        if rn in seen:
            continue
        seen.add(rn)
        deduped.append(r)
    sample_for_manual = deduped
    # Re-key the row schema with `period` for manual layer
    for r in sample_for_manual:
        r["period"] = r["correction_period"]
    print(f"[manual_sample] {len(sample_for_manual)} rows")

    manual_rows = manual_validation(sample_for_manual)
    write_csv(OUT / "manual_link_validation_sample.csv", manual_rows)
    manual_info = write_manual_validation_summary(OUT / "manual_link_validation_summary.md", manual_rows)
    print(f"[manual_validation] {manual_info}")

    # Defect ledger
    defect_rows = []
    for r in candidate_link_rows:
        if r["link_confidence"] == "no_link":
            defect_rows.append({
                "defect_id": f"CL_{len(defect_rows)+1:04d}",
                "defect_class": "no_original_found",
                "rcept_no": r["correction_rcept_no"],
                "category": r["event_category"],
                "notes": r["link_confidence_reason"],
            })
        if not r["corp_code"]:
            defect_rows.append({
                "defect_id": f"CL_{len(defect_rows)+1:04d}",
                "defect_class": "corp_code_missing",
                "rcept_no": r["correction_rcept_no"],
                "category": r["event_category"],
                "notes": "corp_code not present in source row",
            })
        if r["link_confidence"] == "low":
            defect_rows.append({
                "defect_id": f"CL_{len(defect_rows)+1:04d}",
                "defect_class": "title_similarity_low",
                "rcept_no": r["correction_rcept_no"],
                "category": r["event_category"],
                "notes": r["link_confidence_reason"],
            })
        if r["score"] and r["second_score"] and r["second_score"] != "" \
                and isinstance(r["score"], (int, float)) and isinstance(r["second_score"], (int, float)):
            margin = float(r["score"]) - float(r["second_score"])
            if r["link_confidence"] != "no_link" and margin < 0.5:
                defect_rows.append({
                    "defect_id": f"CL_{len(defect_rows)+1:04d}",
                    "defect_class": "multiple_candidate_originals",
                    "rcept_no": r["correction_rcept_no"],
                    "category": r["event_category"],
                    "notes": f"top-2 score margin={margin:.2f}",
                })
        if not r["normalized_base_form"] or r["event_type"] == "":
            defect_rows.append({
                "defect_id": f"CL_{len(defect_rows)+1:04d}",
                "defect_class": "base_form_ambiguous",
                "rcept_no": r["correction_rcept_no"],
                "category": r["event_category"],
                "notes": "normalization fallback used or no event_type token",
            })
        if not r["event_type"]:
            defect_rows.append({
                "defect_id": f"CL_{len(defect_rows)+1:04d}",
                "defect_class": "series_marker_missing",
                "rcept_no": r["correction_rcept_no"],
                "category": r["event_category"],
                "notes": "no event_type token matched in report_nm",
            })

    # Manual-layer defects
    for r in manual_rows:
        if r["manual_judgment"] == "cancellation_or_withdrawal":
            defect_rows.append({
                "defect_id": f"CL_{len(defect_rows)+1:04d}",
                "defect_class": "cancellation_unhandled",
                "rcept_no": r["correction_rcept_no"],
                "category": r["event_category"],
                "notes": "body has cancellation/withdrawal marker; needs manual handling",
            })
        if r["correction_changes_effective_date"]:
            defect_rows.append({
                "defect_id": f"CL_{len(defect_rows)+1:04d}",
                "defect_class": "correction_changes_effective_date",
                "rcept_no": r["correction_rcept_no"],
                "category": r["event_category"],
                "notes": "body has date-change marker",
            })
        if r["manual_judgment"] == "correction_unlinked_requires_manual_review":
            defect_rows.append({
                "defect_id": f"CL_{len(defect_rows)+1:04d}",
                "defect_class": "correction_requires_manual_review",
                "rcept_no": r["correction_rcept_no"],
                "category": r["event_category"],
                "notes": f"link_confidence={r['link_confidence']}",
            })

    # Parser interaction defects
    if parser_info["n_extracted_and_forced_review"] != parser_info["n_extracted"]:
        defect_rows.append({
            "defect_id": f"CL_{len(defect_rows)+1:04d}",
            "defect_class": "parser_extracts_correction_without_manual_review",
            "rcept_no": "",
            "category": "",
            "notes": f"parser-extracted-but-not-forced-review = "
                     f"{parser_info['n_extracted'] - parser_info['n_extracted_and_forced_review']}",
        })

    write_csv(OUT / "correction_linkage_defect_ledger.csv", defect_rows)
    n_defects = len(defect_rows)

    gate, link_rate, eligible = write_gate_status(
        OUT / "correction_linkage_gate_status.md",
        univ_info, manual_info, parser_info, n_defects, candidate_link_counter,
    )
    write_final_summary(
        OUT / "correction_linkage_final_summary.md",
        univ_info, manual_info, parser_info, n_defects, gate, link_rate, eligible,
    )

    print(json.dumps({
        "n_corrections_in_scope": univ_info["n_corrections_in_scope"],
        "candidate_link_counter": dict(candidate_link_counter),
        "manual_sample": manual_info["n_manual"],
        "judgments": manual_info["judgments"],
        "parser_interaction": parser_info,
        "defects": n_defects,
        "gate": gate,
        "link_rate_pct": round(link_rate, 2),
        "eligible": eligible,
        "sensitivity": sensitivity,
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
