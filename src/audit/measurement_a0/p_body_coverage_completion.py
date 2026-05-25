"""S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0 builder.

Attempt the remaining body_unavailable rows from S2-HTML-INLINE-PARSER-BODY-
COVERAGE-EXPANSION-A0 (5,744 not_attempted_in_this_run). Re-apply parser 1.1.0,
quantify completion coverage delta, validate newly acquired bodies, classify
residual body_unavailable.

Audit only. No strategy. No execution simulation. No performance.
No parser feature expansion (parser version 1.1.0 used as-is).
"""
from __future__ import annotations

import csv
import io
import json
import os
import random
import sys
import time
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))

from src.parsers.krx_status_html_inline import (  # noqa: E402
    PARSER_VERSION,
    PERIOD_CHANGE_RE,
    IN_SCOPE_CATEGORIES,
    parse_disclosure,
)
from src.audit.measurement_a0.p_status_correction_linkage import (  # noqa: E402
    load_env,
    ZIP_CACHE,
)
from src.audit.measurement_a0.p_body_coverage_expansion import (  # noqa: E402
    DART_DOCUMENT_URL, THROTTLE_SEC, MAX_RETRIES,
    download_one, classify_body, inventory_cache,
)
from src.audit.measurement_a0.p_full_universe_parser_validation import (  # noqa: E402
    _verify_extracted, _verify_no_label_or_label_no_value,
)

OUT = REPO / "reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_BODY_COVERAGE_COMPLETION_A0"
OUT.mkdir(parents=True, exist_ok=True)

PRIOR_DIR = REPO / "reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_BODY_COVERAGE_EXPANSION_A0"
PRIOR_ATTEMPT_LOG = PRIOR_DIR / "body_acquisition_attempt_log.csv"
PRIOR_PARSER_OUTPUTS = PRIOR_DIR / "post_acquisition_parser_outputs.csv"
PRIOR_TARGET = PRIOR_DIR / "body_unavailable_target_universe.csv"

# Completion run: attempt all remaining (~5,744). Bigger budget than prior phase.
COMPLETION_BUDGET = 6000


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


# ---------------------------------------------------------------------------
# Remaining target construction
# ---------------------------------------------------------------------------

def build_remaining_target() -> list[dict]:
    """All rows from prior attempt log with attempt_status = not_attempted_in_this_run."""
    log = pd.read_csv(PRIOR_ATTEMPT_LOG, dtype=str).fillna("")
    remaining = log[log["attempt_status"] == "not_attempted_in_this_run"]
    rows = []
    for _, r in remaining.iterrows():
        rows.append({
            "rcept_no": r["rcept_no"],
            "rcept_dt": r["rcept_dt"],
            "stock_code": r["stock_code"],
            "corp_name": r["corp_name"],
            "event_category": r["event_category"],
            "report_nm": r["report_nm"],
            "source_period": r["source_period"],
            "prior_priority_bucket": r["priority_bucket"],
            "prior_acquisition_status": r["attempt_status"],
            "prior_parse_status": "body_unavailable",
            "prior_body_status": "body_unavailable",
            "correction_flag": r["correction_flag"],
            "correction_pass3_confidence": r.get("correction_pass3_confidence", ""),
            "is_period_change": r["is_period_change"],
            "manual_review_required": r.get("manual_review_required", ""),
            "remaining_target_reason": "prior_budget_cap",
        })
    return rows


# ---------------------------------------------------------------------------
# Cache re-inventory
# ---------------------------------------------------------------------------

def write_cache_reinventory(path: Path, info: dict, remaining: list[dict]) -> dict:
    """Re-inventory cache + cross-check remaining target."""
    remaining_set = {r["rcept_no"] for r in remaining}
    already_cached_now = sum(1 for rn in info["rcept_set"] if rn in remaining_set)
    still_missing = len(remaining_set) - already_cached_now
    in_scope_now = info.get("in_scope_now", 0)
    lines = [
        "# Cache Re-inventory Summary",
        "",
        "Date: 2026-05-25",
        "Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0",
        "",
        f"## Total cached ZIPs (after prior phase): **{info['total_zips']}**",
        f"## Unique rcept_no in cache: **{info['unique_rcept_no']}**",
        f"## Valid ZIPs: **{info['valid_zips']}**",
        f"## Unparseable ZIPs: **{info['unparseable_zips']}**",
        f"## Duplicate rcept_no: **{info['duplicate_rcept_no']}**",
        "",
        "## Cache re-cross-check vs remaining target",
        "",
        f"- Remaining target rows from prior phase: **{len(remaining)}**",
        f"- Remaining rows already cached now (recovered via manual / other phases): "
        f"**{already_cached_now}**",
        f"- Remaining rows still missing: **{still_missing}**",
        "",
        "## Per cache directory",
        "",
        "| directory | n_zips | n_valid | n_unparseable |",
        "|---|---:|---:|---:|",
    ]
    for d, v in info["by_dir"].items():
        lines.append(f"| `{d}` | {v['n_zips']} | {v['n_valid']} | {v['n_unparseable']} |")
    lines += [
        "",
        "## Acquisition reuse rule",
        "",
        "Already-cached rows are NOT re-downloaded. Only `still_missing` rows are",
        "attempted in this completion pass.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return {"already_cached_now": already_cached_now, "still_missing": still_missing}


# ---------------------------------------------------------------------------
# Completion acquisition
# ---------------------------------------------------------------------------

def write_acquisition_plan(path: Path, remaining: list[dict], cached: set[str]) -> dict:
    bucket = Counter(r["prior_priority_bucket"] for r in remaining)
    in_remaining_already_cached = sum(1 for r in remaining if r["rcept_no"] in cached)
    to_attempt = len(remaining) - in_remaining_already_cached
    lines = [
        "# Completion Acquisition Plan",
        "",
        "Date: 2026-05-25",
        "Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0",
        "",
        f"## Remaining body_unavailable rows (prior not_attempted): **{len(remaining)}**",
        f"## Already cached now (skip): **{in_remaining_already_cached}**",
        f"## To attempt this run: **{to_attempt}**",
        f"## Download budget cap (this run): **{COMPLETION_BUDGET}**",
        f"## Throttle: **{THROTTLE_SEC} s** between requests "
        f"(~{int(1/THROTTLE_SEC)} req/s nominal).",
        f"## Max retries: **{MAX_RETRIES}**.",
        "",
        "## Priority bucket distribution (from prior phase)",
        "",
        "| bucket | count |",
        "|---|---:|",
    ]
    for k in ("P0_correction_high_medium", "P1_resumption", "P2_period_change",
              "P3_ordinary_suspension", "P4_pre2018", "P5_post2018"):
        lines.append(f"| `{k}` | {bucket.get(k, 0)} |")
    lines += [
        "",
        "## Acquisition order",
        "",
        "Same priority order as expansion phase: P0 → P1 → P2 → P3 → P4 → P5.",
        "If budget is large enough to cover everything, all rows are attempted.",
        "",
        "## Terminal status taxonomy (every row receives one)",
        "",
        "- `already_cached` — body present from prior expansion or other phase.",
        "- `success` (with body_format ∈ html_inline / structured_xml / attachment_only / other) — new download succeeded.",
        "- `api_no_document` — OPENDART returned <status>013 (no document).",
        "- `zip_unparseable` — downloaded data not a valid ZIP.",
        "- `rate_limited` — HTTP 429.",
        "- `credential_or_api_error` — HTTP 401/403.",
        "- `retry_needed` — transient error after retry budget exhausted.",
        "- `not_attempted_due_to_budget` — beyond COMPLETION_BUDGET.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return {"bucket": dict(bucket), "to_attempt": to_attempt}


def acquire_completion(remaining: list[dict]) -> tuple[list[dict], dict]:
    load_env()
    api_key = os.environ.get("OPENDART_API_KEY")
    if not api_key:
        return [], {"error": "OPENDART_API_KEY missing"}

    # Sort remaining by prior priority bucket then rcept_dt
    priority_order = (
        "P0_correction_high_medium", "P1_resumption", "P2_period_change",
        "P3_ordinary_suspension", "P4_pre2018", "P5_post2018",
    )
    order_key = {p: i for i, p in enumerate(priority_order)}
    sorted_remaining = sorted(
        remaining,
        key=lambda r: (order_key.get(r["prior_priority_bucket"], 99), r["rcept_dt"]),
    )

    log = []
    n_attempted = 0
    counters = Counter()
    cached = {p.stem for p in ZIP_CACHE.glob("*.zip")} if ZIP_CACHE.exists() else set()

    for r in sorted_remaining:
        rcept_no = r["rcept_no"]
        if rcept_no in cached:
            log.append({**r, "attempt_status": "already_cached", "body_format": "",
                        "http_detail": "", "retries": 0})
            counters["already_cached"] += 1
            continue
        if n_attempted >= COMPLETION_BUDGET:
            log.append({**r, "attempt_status": "not_attempted_due_to_budget",
                        "body_format": "", "http_detail": "budget_exhausted",
                        "retries": 0})
            counters["not_attempted_due_to_budget"] += 1
            continue

        retries = 0
        while True:
            status, data, detail = download_one(rcept_no, api_key)
            if status == "retry_needed" and retries < MAX_RETRIES:
                retries += 1
                time.sleep(THROTTLE_SEC * 2)
                continue
            break

        n_attempted += 1
        body_format = ""
        if status == "download_success" and data is not None:
            zip_path = ZIP_CACHE / f"{rcept_no}.zip"
            zip_path.write_bytes(data)
            class_status, body_format = classify_body(data)
            if class_status != "download_success":
                status = class_status  # zip_unparseable
            cached.add(rcept_no)

        if status == "download_success":
            counters["success"] += 1
            counters[f"body_format_{body_format}"] += 1
        elif status == "zip_unparseable":
            counters["zip_unparseable"] += 1
        elif status == "api_no_document":
            counters["api_no_document"] += 1
        elif status == "rate_limited":
            counters["rate_limited"] += 1
            time.sleep(2.0)
        elif status == "credential_or_api_error":
            counters["credential_or_api_error"] += 1
        else:
            counters["retry_needed"] += 1

        log.append({**r, "attempt_status": status, "body_format": body_format,
                    "http_detail": detail, "retries": retries})
        time.sleep(THROTTLE_SEC)
        if n_attempted % 500 == 0:
            print(f"  ... attempted {n_attempted} | success {counters['success']} | "
                  f"no_doc {counters['api_no_document']} | unparseable {counters['zip_unparseable']}")

    summary = {
        "n_remaining": len(sorted_remaining),
        "n_attempted": n_attempted,
        "n_already_cached": counters["already_cached"],
        "n_success": counters["success"],
        "n_html_inline": counters["body_format_html_inline"],
        "n_structured_xml": counters["body_format_structured_xml"],
        "n_attachment_only": counters["body_format_attachment_only"],
        "n_other_format": counters["body_format_other"],
        "n_zip_unparseable": counters["zip_unparseable"],
        "n_api_no_document": counters["api_no_document"],
        "n_rate_limited": counters["rate_limited"],
        "n_credential_or_api_error": counters["credential_or_api_error"],
        "n_retry_needed": counters["retry_needed"],
        "n_not_attempted_due_to_budget": counters["not_attempted_due_to_budget"],
    }
    return log, summary


# ---------------------------------------------------------------------------
# Re-apply parser
# ---------------------------------------------------------------------------

def reapply_parser(remaining: list[dict], cached: set[str]) -> list[dict]:
    out = []
    for r in remaining:
        rcept_no = r["rcept_no"]
        zip_bytes = None
        if rcept_no in cached:
            zip_path = ZIP_CACHE / f"{rcept_no}.zip"
            try:
                zip_bytes = zip_path.read_bytes()
            except Exception:
                zip_bytes = None
        res = parse_disclosure(
            rcept_no=rcept_no,
            rcept_dt=r["rcept_dt"],
            stock_code=r["stock_code"],
            corp_name=r["corp_name"],
            report_nm=r["report_nm"],
            zip_bytes=zip_bytes,
        )
        d = res.as_dict()
        d["source_period"] = r["source_period"]
        d["parser_version"] = PARSER_VERSION
        d["cached_body_at_run"] = (rcept_no in cached)
        d["prior_priority_bucket"] = r["prior_priority_bucket"]
        d["is_period_change"] = r["is_period_change"]
        d["correction_pass3_confidence"] = r["correction_pass3_confidence"]
        out.append(d)
    return out


# ---------------------------------------------------------------------------
# Reports (coverage delta + holdout + residuals)
# ---------------------------------------------------------------------------

def write_coverage_delta(path: Path, remaining: list[dict],
                         post_parser: list[dict], summary: dict) -> dict:
    pre_total = len(remaining)
    post_status = Counter(r["parse_status"] for r in post_parser)
    n_post_bu = post_status["body_unavailable"]
    n_post_extracted = post_status["extracted"]
    n_post_no_label = post_status["no_label_match"]
    n_post_label_no_value = post_status["label_no_value"]
    n_post_oosc_body_format = post_status["out_of_scope_body_format"]
    n_post_body_available = pre_total - n_post_bu

    sus = Counter(r["parse_status"] for r in post_parser
                  if r["event_category"] == "suspension_related")
    res = Counter(r["parse_status"] for r in post_parser
                  if r["event_category"] == "resumption_related")
    pre18 = Counter(r["parse_status"] for r in post_parser
                    if r["source_period"] == "pre_2018")
    post18 = Counter(r["parse_status"] for r in post_parser
                     if r["source_period"] == "post_2018")
    corr = Counter(r["parse_status"] for r in post_parser
                   if str(r.get("correction_flag", "")).lower() in ("true", "1"))
    noncorr = Counter(r["parse_status"] for r in post_parser
                      if str(r.get("correction_flag", "")).lower() not in ("true", "1"))
    bucket = defaultdict(Counter)
    for r in post_parser:
        bucket[r["prior_priority_bucket"]][r["parse_status"]] += 1
    pc = Counter(r["parse_status"] for r in post_parser
                 if r["is_period_change"] in (True, "True", "true"))
    ord_sus = Counter(r["parse_status"] for r in post_parser
                      if r["event_category"] == "suspension_related"
                      and r["is_period_change"] not in (True, "True", "true"))

    lines = [
        "# Completion Coverage Delta Summary",
        "",
        "Date: 2026-05-25",
        "Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0",
        f"Parser version: `{PARSER_VERSION}` (no feature change).",
        "",
        "## Acquisition summary (this run)",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| remaining target rows | {summary['n_remaining']} |",
        f"| already_cached at start of this run | {summary['n_already_cached']} |",
        f"| attempted | {summary['n_attempted']} |",
        f"| download_success | {summary['n_success']} |",
        f"| html_inline | {summary['n_html_inline']} |",
        f"| structured_xml | {summary['n_structured_xml']} |",
        f"| attachment_only | {summary['n_attachment_only']} |",
        f"| other_format | {summary['n_other_format']} |",
        f"| zip_unparseable | {summary['n_zip_unparseable']} |",
        f"| api_no_document | {summary['n_api_no_document']} |",
        f"| rate_limited | {summary['n_rate_limited']} |",
        f"| credential_or_api_error | {summary['n_credential_or_api_error']} |",
        f"| retry_needed_after_retries | {summary['n_retry_needed']} |",
        f"| not_attempted_due_to_budget | {summary['n_not_attempted_due_to_budget']} |",
        "",
        "## Coverage delta on remaining target rows (before → after)",
        "",
        "| state | before | after |",
        "|---|---:|---:|",
        f"| body_unavailable | {pre_total} | {n_post_bu} |",
        f"| body_available | 0 | {n_post_body_available} |",
        f"| extracted | 0 | {n_post_extracted} |",
        f"| no_label_match | 0 | {n_post_no_label} |",
        f"| label_no_value | 0 | {n_post_label_no_value} |",
        f"| out_of_scope_body_format | 0 | {n_post_oosc_body_format} |",
        "",
        f"## Coverage shift on remaining: **{n_post_body_available} / {pre_total} = "
        f"{100.0 * n_post_body_available / max(1, pre_total):.1f}%**",
        "",
        "## By event_category",
        "",
        "| category | extracted | no_label | label_no_value | body_unavailable |",
        "|---|---:|---:|---:|---:|",
        f"| `suspension_related` | {sus.get('extracted', 0)} | "
        f"{sus.get('no_label_match', 0)} | {sus.get('label_no_value', 0)} | "
        f"{sus.get('body_unavailable', 0)} |",
        f"| `resumption_related` | {res.get('extracted', 0)} | "
        f"{res.get('no_label_match', 0)} | {res.get('label_no_value', 0)} | "
        f"{res.get('body_unavailable', 0)} |",
        "",
        "## By period",
        "",
        "| period | extracted | body_unavailable |",
        "|---|---:|---:|",
        f"| `pre_2018` | {pre18.get('extracted', 0)} | {pre18.get('body_unavailable', 0)} |",
        f"| `post_2018` | {post18.get('extracted', 0)} | {post18.get('body_unavailable', 0)} |",
        "",
        "## Correction vs non-correction",
        "",
        "| segment | extracted | body_unavailable |",
        "|---|---:|---:|",
        f"| correction | {corr.get('extracted', 0)} | {corr.get('body_unavailable', 0)} |",
        f"| non_correction | {noncorr.get('extracted', 0)} | {noncorr.get('body_unavailable', 0)} |",
        "",
        "## period_change vs ordinary suspension",
        "",
        "| segment | extracted | body_unavailable |",
        "|---|---:|---:|",
        f"| `period_change` | {pc.get('extracted', 0)} | {pc.get('body_unavailable', 0)} |",
        f"| `ordinary_suspension` | {ord_sus.get('extracted', 0)} | {ord_sus.get('body_unavailable', 0)} |",
        "",
        "## By prior priority bucket",
        "",
        "| bucket | total | extracted | body_unavailable |",
        "|---|---:|---:|---:|",
    ]
    for b in ("P0_correction_high_medium", "P1_resumption", "P2_period_change",
              "P3_ordinary_suspension", "P4_pre2018", "P5_post2018"):
        c = bucket.get(b, Counter())
        total = sum(c.values())
        lines.append(f"| `{b}` | {total} | {c.get('extracted', 0)} | "
                     f"{c.get('body_unavailable', 0)} |")
    # Universe-level update estimate
    # Prior phase final universe body_available ≈ 6,398 / 12,187 = 52.5%.
    # After completion add (n_success) — should approach 12,187 if all attempted.
    new_universe_body_available = 6398 + summary['n_success']
    lines += [
        "",
        "## Universe-level body coverage estimate",
        "",
        f"- In-scope universe: 12,187.",
        f"- Body available before this run (estimate): 6,398 ≈ 52.5%.",
        f"- Body acquired this run: {summary['n_success']}.",
        f"- **Body available now (estimate): ~{new_universe_body_available} / 12,187 = "
        f"{100.0 * new_universe_body_available / 12187:.1f}%**.",
        "",
        "## body_unavailable remaining (preserved)",
        "",
        f"- {n_post_bu} target rows remain `body_unavailable` after this phase.",
        "- Per Referee: these rows MUST NOT be treated as parsed / executable / safe.",
        "- They are preserved in `completion_parser_outputs.csv` with",
        "  `parse_status = body_unavailable` and `manual_review_required = True`.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "n_post_bu": n_post_bu,
        "n_post_body_available": n_post_body_available,
        "n_post_extracted": n_post_extracted,
        "n_post_no_label": n_post_no_label,
        "n_post_label_no_value": n_post_label_no_value,
        "universe_body_pct": 100.0 * new_universe_body_available / 12187,
    }


# Holdout
def build_holdout(post_parser: list[dict]) -> list[dict]:
    random.seed(20260525)
    sample = []
    extracted = [r for r in post_parser if r["parse_status"] == "extracted"]
    sus = [r for r in extracted if r["event_category"] == "suspension_related"
           and r["is_period_change"] not in (True, "True", "true")]
    res = [r for r in extracted if r["event_category"] == "resumption_related"]
    pc = [r for r in extracted if r["is_period_change"] in (True, "True", "true")]
    corr = [r for r in extracted
            if str(r.get("correction_flag", "")).lower() in ("true", "1")]

    def add(pool: list[dict], n: int, bucket: str) -> None:
        if not pool:
            return
        picks = random.sample(pool, min(n, len(pool)))
        for p in picks:
            sample.append({**p, "holdout_bucket": bucket})

    add(sus, 50, "ordinary_suspension")
    add(res, 50, "ordinary_resumption")
    add(pc, 30, "period_change_disclosure")
    add(corr, 30, "correction_flagged")

    seen = set()
    deduped = []
    for r in sample:
        if r["rcept_no"] in seen:
            continue
        seen.add(r["rcept_no"])
        deduped.append(r)
    return deduped


def classify_holdout(holdout: list[dict]) -> list[dict]:
    out = []
    for r in holdout:
        rcept_no = r["rcept_no"]
        zip_path = ZIP_CACHE / f"{rcept_no}.zip"
        zip_bytes = zip_path.read_bytes() if zip_path.exists() else None
        res = parse_disclosure(
            rcept_no=rcept_no, rcept_dt=r.get("rcept_dt", ""),
            stock_code=r.get("stock_code", ""), corp_name=r.get("corp_name", ""),
            report_nm=r.get("report_nm", ""), zip_bytes=zip_bytes,
        )
        bucket = r["holdout_bucket"]
        if bucket == "correction_flagged":
            cls = ("manual_review_required_correctly" if res.manual_review_required
                   else "correction_not_forced_manual_review")
        elif res.parse_status == "body_unavailable":
            cls = "body_unavailable"
        elif res.parse_status == "out_of_scope_body_format":
            cls = "unparseable"
        elif res.parse_status in ("no_label_match", "label_no_value"):
            cls = _verify_no_label_or_label_no_value(zip_bytes, bucket, res)
        elif res.parse_status == "extracted":
            cls = _verify_extracted(zip_bytes, res)
        else:
            cls = "manual_review_required_correctly"
        out.append({
            **r,
            "holdout_parse_status": res.parse_status,
            "holdout_parsed_effective_date": res.parsed_effective_date or "",
            "holdout_date_label_used": res.date_label_used or "",
            "holdout_classification": cls,
        })
    return out


def write_holdout_summary(path: Path, holdout: list[dict]) -> dict:
    cnt = Counter(r["holdout_classification"] for r in holdout)
    bucket_cnt = Counter(r["holdout_bucket"] for r in holdout)
    n = len(holdout)
    n_exact = cnt["exact_match"]
    n_accept = cnt["acceptable_range_match"]
    n_wrong = cnt["wrong_date"]
    n_missed = cnt["missed_date"]
    n_fp = cnt["false_positive"]
    n_corr_fail = cnt["correction_not_forced_manual_review"]
    n_review = cnt["manual_review_required_correctly"]
    n_body_unavail = cnt["body_unavailable"]
    n_success = n_exact + n_accept + n_review
    success_rate = 100.0 * n_success / max(1, n)
    lines = [
        "# Completion Validation Summary",
        "",
        "Date: 2026-05-25",
        "Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0",
        f"Parser version: `{PARSER_VERSION}` (used as-is).",
        "",
        "## Method",
        "",
        "Sample drawn from rows extracted against newly-acquired completion bodies.",
        "Body cross-checks classify each row per Referee taxonomy.",
        "",
        f"## Holdout sample size: **{n}**",
        "",
        "## Bucket distribution",
        "",
        "| bucket | count |",
        "|---|---:|",
    ]
    for k, v in bucket_cnt.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Classification distribution",
        "",
        "| classification | count |",
        "|---|---:|",
    ]
    for k in ("exact_match", "acceptable_range_match", "wrong_date", "missed_date",
              "false_positive", "body_unavailable", "unparseable",
              "manual_review_required_correctly",
              "correction_not_forced_manual_review"):
        lines.append(f"| `{k}` | {cnt.get(k, 0)} |")
    lines += [
        "",
        f"## Success rate (exact + acceptable + review): **{n_success} / {n} = "
        f"{success_rate:.1f}%**",
        f"## Wrong+missed: **{n_wrong + n_missed}**",
        f"## False positives: **{n_fp}**",
        f"## Correction not forced manual review (must be 0): **{n_corr_fail}**",
        "",
        "## Comparison vs Expansion-phase holdout",
        "",
        "| metric | Expansion (84 rows) | Completion ({n} rows) |".replace("{n}", str(n)),
        "|---|---:|---:|",
        f"| success rate | 100.0% | {success_rate:.1f}% |",
        f"| FP | 0 | {n_fp} |",
        f"| wrong+missed | 0 | {n_wrong + n_missed} |",
        f"| correction_not_forced | 0 | {n_corr_fail} |",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return {"n": n, "success_rate": success_rate, "n_fp": n_fp,
            "n_wrong": n_wrong, "n_missed": n_missed, "n_corr_fail": n_corr_fail,
            "n_body_unavail": n_body_unavail, "n_success": n_success}


def write_residual_classification(path: Path, log: list[dict],
                                  post_parser: list[dict]) -> list[dict]:
    """Classify every remaining body_unavailable row per Referee taxonomy."""
    # Index log by rcept_no
    by_rn = {r["rcept_no"]: r for r in log}
    rows = []
    for r in post_parser:
        if r["parse_status"] != "body_unavailable":
            continue
        log_row = by_rn.get(r["rcept_no"], {})
        attempt_status = log_row.get("attempt_status", "unknown")
        if attempt_status == "not_attempted_due_to_budget":
            classification = "not_attempted_due_to_budget"
        elif attempt_status == "api_no_document":
            classification = "api_no_document"
        elif attempt_status == "zip_unparseable":
            classification = "zip_unparseable"
        elif attempt_status == "credential_or_api_error":
            classification = "credential_or_api_error"
        elif attempt_status == "rate_limited":
            classification = "rate_limited"
        elif attempt_status == "retry_needed":
            classification = "retry_needed"
        elif attempt_status == "already_cached":
            # Body cached but parser still says body_unavailable — weird edge case
            classification = "source_unavailable"
        elif attempt_status == "success":
            # Downloaded but parser couldn't get body? Probably unparseable.
            classification = "source_unavailable"
        else:
            classification = "other"
        rows.append({
            "rcept_no": r["rcept_no"],
            "event_category": r["event_category"],
            "source_period": r["source_period"],
            "prior_priority_bucket": r["prior_priority_bucket"],
            "attempt_status": attempt_status,
            "http_detail": log_row.get("http_detail", ""),
            "classification": classification,
        })
    write_csv(path, rows)
    return rows


# ---------------------------------------------------------------------------
# Defects + gate + final
# ---------------------------------------------------------------------------

def build_defects(log: list[dict], residual: list[dict], holdout: list[dict]) -> list[dict]:
    defects = []
    error_map = {
        "api_no_document": "api_no_document",
        "rate_limited": "rate_limited",
        "zip_unparseable": "zip_unparseable",
        "credential_or_api_error": "credential_or_api_error",
        "retry_needed": "body_download_failed",
        "not_attempted_due_to_budget": "not_attempted_remaining",
    }
    for r in log:
        cls = error_map.get(r["attempt_status"])
        if cls:
            defects.append({
                "defect_id": f"CP_{len(defects)+1:05d}",
                "defect_class": cls,
                "rcept_no": r["rcept_no"],
                "category": r["event_category"],
                "notes": f"{r['attempt_status']}/{r.get('http_detail', '')}",
            })
        elif r["attempt_status"] == "success" and r["body_format"] == "attachment_only":
            defects.append({
                "defect_id": f"CP_{len(defects)+1:05d}",
                "defect_class": "attachment_only",
                "rcept_no": r["rcept_no"], "category": r["event_category"],
                "notes": "PDF/attachment",
            })
        elif r["attempt_status"] == "success" and r["body_format"] == "structured_xml":
            defects.append({
                "defect_id": f"CP_{len(defects)+1:05d}",
                "defect_class": "structured_xml_out_of_scope",
                "rcept_no": r["rcept_no"], "category": r["event_category"],
                "notes": "structured_xml",
            })
    for r in residual:
        defects.append({
            "defect_id": f"CP_{len(defects)+1:05d}",
            "defect_class": "body_unavailable_remaining",
            "rcept_no": r["rcept_no"],
            "category": r["event_category"],
            "notes": f"classification={r['classification']}",
        })
    for r in holdout:
        if r["holdout_classification"] == "wrong_date":
            defects.append({
                "defect_id": f"CP_{len(defects)+1:05d}",
                "defect_class": "newly_parsed_wrong_date",
                "rcept_no": r["rcept_no"], "category": r["event_category"],
                "notes": f"parsed {r.get('holdout_parsed_effective_date')}",
            })
        elif r["holdout_classification"] == "missed_date":
            defects.append({
                "defect_id": f"CP_{len(defects)+1:05d}",
                "defect_class": "newly_parsed_missed_date",
                "rcept_no": r["rcept_no"], "category": r["event_category"],
                "notes": "body has label parser missed",
            })
        elif r["holdout_classification"] == "correction_not_forced_manual_review":
            defects.append({
                "defect_id": f"CP_{len(defects)+1:05d}",
                "defect_class": "correction_policy_violation",
                "rcept_no": r["rcept_no"], "category": r["event_category"],
                "notes": "correction row not forced to manual review",
            })
    return defects


def write_gate_status(path: Path, summary: dict, delta: dict,
                      holdout_info: dict, residual: list[dict],
                      defects_n: int) -> tuple[str, float]:
    n_success = summary["n_success"]
    n_remaining = summary["n_remaining"]
    n_post_bu = delta["n_post_bu"]
    coverage_shift = 100.0 * (n_remaining - n_post_bu) / max(1, n_remaining)
    n_not_attempted_residual = sum(1 for r in residual
                                   if r["classification"] == "not_attempted_due_to_budget")
    n_source_failures = sum(1 for r in residual
                            if r["classification"] not in ("not_attempted_due_to_budget",))

    if holdout_info["n_corr_fail"] > 0 or holdout_info["n_fp"] > 0:
        gate = "BODY_COVERAGE_REQUIRES_MORE_WORK"
        rationale = (
            f"correction_not_forced_manual_review={holdout_info['n_corr_fail']}; "
            f"holdout FP={holdout_info['n_fp']}; safety regression."
        )
    elif n_not_attempted_residual >= 1000:
        gate = "BODY_COVERAGE_REQUIRES_MORE_WORK"
        rationale = (
            f"{n_not_attempted_residual} rows still not_attempted_due_to_budget; "
            "another pass needed."
        )
    elif n_success >= 3000 and coverage_shift >= 80 \
            and holdout_info["success_rate"] >= 90 \
            and holdout_info["n_wrong"] + holdout_info["n_missed"] <= 5:
        gate = "READY_FOR_NEXT_A0_REVIEW"
        rationale = (
            f"acquired {n_success} bodies; remaining coverage shift {coverage_shift:.1f}%; "
            f"holdout success {holdout_info['success_rate']:.1f}%; "
            f"FP=0; correction policy unchanged; "
            f"residual classified ({n_source_failures} source-side; "
            f"{n_not_attempted_residual} budget)."
        )
    elif n_success >= 1000 and coverage_shift >= 50 \
            and holdout_info["success_rate"] >= 85:
        gate = "BODY_COVERAGE_COMPLETED_AND_VALIDATED_FOR_AVAILABLE_ROWS"
        rationale = (
            f"acquired {n_success} bodies; coverage shift {coverage_shift:.1f}%; "
            f"holdout success {holdout_info['success_rate']:.1f}%; "
            "parser behavior preserved."
        )
    elif n_source_failures > 0 and n_not_attempted_residual < 500:
        gate = "BODY_COVERAGE_COMPLETED_WITH_RESIDUALS"
        rationale = (
            f"acquired {n_success} bodies; coverage shift {coverage_shift:.1f}%; "
            f"residual {n_source_failures} source-side defects classified; "
            f"holdout success {holdout_info['success_rate']:.1f}%."
        )
    elif n_success == 0:
        gate = "DATA_SOURCE_FAIL" if summary.get("n_credential_or_api_error", 0) > 100 \
            else "PARTIAL"
        rationale = "completion acquisition produced no new bodies."
    else:
        gate = "PARTIAL"
        rationale = f"acquired {n_success} bodies; coverage shift {coverage_shift:.1f}%."

    lines = [
        "# Body Completion Gate Status",
        "",
        "Date: 2026-05-25",
        "Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0",
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
        "- `BODY_COVERAGE_COMPLETED_WITH_RESIDUALS`",
        "- `BODY_COVERAGE_COMPLETED_AND_VALIDATED_FOR_AVAILABLE_ROWS`",
        "- `BODY_COVERAGE_REQUIRES_MORE_WORK`",
        "- `READY_FOR_NEXT_A0_REVIEW`",
        "",
        "## Numerical inputs",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| remaining target | {summary['n_remaining']} |",
        f"| download_success | {summary['n_success']} |",
        f"| html_inline | {summary['n_html_inline']} |",
        f"| structured_xml | {summary['n_structured_xml']} |",
        f"| attachment_only | {summary['n_attachment_only']} |",
        f"| zip_unparseable | {summary['n_zip_unparseable']} |",
        f"| api_no_document | {summary['n_api_no_document']} |",
        f"| rate_limited | {summary['n_rate_limited']} |",
        f"| credential_or_api_error | {summary['n_credential_or_api_error']} |",
        f"| not_attempted_due_to_budget | {summary['n_not_attempted_due_to_budget']} |",
        f"| body_unavailable on remaining (after) | {delta['n_post_bu']} |",
        f"| coverage shift on remaining | {coverage_shift:.1f}% |",
        f"| universe-level body coverage estimate | {delta['universe_body_pct']:.1f}% |",
        f"| holdout sample | {holdout_info['n']} |",
        f"| holdout success rate | {holdout_info['success_rate']:.1f}% |",
        f"| holdout FP | {holdout_info['n_fp']} |",
        f"| holdout wrong+missed | {holdout_info['n_wrong'] + holdout_info['n_missed']} |",
        f"| holdout correction_not_forced_manual_review | {holdout_info['n_corr_fail']} |",
        f"| residual rows classified | {len(residual)} |",
        f"| residual not_attempted_due_to_budget | {n_not_attempted_residual} |",
        f"| residual source-side | {n_source_failures} |",
        f"| defects | {defects_n} |",
        "",
        "## Important boundary",
        "",
        "- Execution simulation is NOT opened.",
        "- Strategy testing is NOT opened.",
        "- Performance diagnostics is NOT opened.",
        "- No card is strategy-ready.",
        "- Parser scope unchanged (1.1.0 used as-is).",
        "- `body_unavailable` rows remaining MUST NOT be treated as parsed or safe.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return gate, coverage_shift


def write_final_summary(path: Path, summary: dict, delta: dict,
                       holdout_info: dict, residual: list[dict],
                       gate: str, coverage_shift: float, defects_n: int) -> None:
    n_not_attempted_residual = sum(1 for r in residual
                                   if r["classification"] == "not_attempted_due_to_budget")
    n_source_failures = len(residual) - n_not_attempted_residual
    lines = [
        "# S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0 — Final Summary",
        "",
        "Date: 2026-05-25",
        f"Parser version: `{PARSER_VERSION}` (no feature change in this phase).",
        "",
        "## Scope respected",
        "",
        "- Measurement-layer body-coverage completion A0 only.",
        "- suspension_related + resumption_related only.",
        "- HTML-inline body candidates only.",
        "- Remaining body_unavailable rows only.",
        "- Parser 1.1.0 used as-is (no feature expansion).",
        "- No delisting / liquidation / managed / alert parser.",
        "- No DART body alpha. No overhang. No all-event event log.",
        "- No C2/C3 wiring. No strategy testing. No execution simulation.",
        "- No performance diagnostics. No production / paper / P08 / live / shadow.",
        "",
        "## What was delivered",
        "",
        "Code:",
        "- `src/audit/measurement_a0/p_body_coverage_completion.py`",
        "",
        "Reports (this dir, 13 outputs):",
        "1. `body_completion_referee_lock.md`",
        "2. `remaining_body_unavailable_target.csv`",
        "3. `cache_reinventory_summary.md`",
        "4. `completion_acquisition_plan.md`",
        "5. `completion_acquisition_attempt_log.csv`",
        "6. `completion_coverage_delta_summary.md`",
        "7. `completion_parser_outputs.csv`",
        "8. `completion_validation_sample.csv`",
        "9. `completion_validation_summary.md`",
        "10. `residual_body_unavailable_classification.csv`",
        "11. `body_completion_defect_ledger.csv`",
        "12. `body_completion_gate_status.md`",
        "13. `body_completion_final_summary.md` (this file)",
        "",
        "## Headline results",
        "",
        f"- Remaining target rows: **{summary['n_remaining']}**.",
        f"- Already cached at start of this run: **{summary['n_already_cached']}**.",
        f"- Download attempts: **{summary['n_attempted']}**.",
        f"- Download successes: **{summary['n_success']}**.",
        f"  - html_inline: {summary['n_html_inline']}",
        f"  - structured_xml: {summary['n_structured_xml']}",
        f"  - attachment_only: {summary['n_attachment_only']}",
        f"  - other_format: {summary['n_other_format']}",
        f"  - zip_unparseable: {summary['n_zip_unparseable']}",
        f"- API no_document: {summary['n_api_no_document']}",
        f"- Rate limited: {summary['n_rate_limited']}",
        f"- Credential / API errors: {summary['n_credential_or_api_error']}",
        f"- Not attempted (budget exhausted this run): {summary['n_not_attempted_due_to_budget']}",
        "",
        f"- Body available on remaining (after): **{delta['n_post_body_available']}**.",
        f"- Body unavailable on remaining (after): **{delta['n_post_bu']}**.",
        f"- Coverage shift on remaining: **{coverage_shift:.1f}%**.",
        f"- New extractions: **{delta['n_post_extracted']}**.",
        "",
        f"- Universe-level body coverage estimate now: **~{delta['universe_body_pct']:.1f}%** "
        f"(up from ~52.5% before this run).",
        "",
        f"- Holdout sample: **{holdout_info['n']}** (drawn from newly extracted).",
        f"- Holdout success rate: **{holdout_info['success_rate']:.1f}%**.",
        f"- Holdout FP: **{holdout_info['n_fp']}**.",
        f"- Holdout wrong+missed: **{holdout_info['n_wrong'] + holdout_info['n_missed']}**.",
        f"- Holdout correction_not_forced_manual_review: **{holdout_info['n_corr_fail']}**.",
        "",
        f"- Residual body_unavailable rows classified: **{len(residual)}**.",
        f"  - not_attempted_due_to_budget: {n_not_attempted_residual}",
        f"  - source-side (api_no_document / zip_unparseable / etc.): {n_source_failures}",
        f"- Defect ledger rows: **{defects_n}**.",
        f"- Gate state: **{gate}**.",
        "",
        "## Pass-criteria evaluation",
        "",
        "| criterion | status |",
        "|---|---|",
        "| remaining target universe documented | YES |",
        "| cache re-inventoried | YES |",
        "| completion acquisition log produced | YES |",
        "| coverage before vs after quantified | YES |",
        "| newly acquired bodies parsed with existing parser only | YES |",
        f"| completion validation sample completed | {'YES' if holdout_info['n'] > 0 else 'PARTIAL'} |",
        "| residual body_unavailable rows classified | YES |",
        "| body_unavailable preserved and not silently dropped | YES |",
        "| defect ledger produced | YES |",
        "| gate status explicitly stated | YES |",
        "| no strategy / execution / performance produced | YES |",
        "",
        "## Hard locks (preserved)",
        "",
        "- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / execution sim /",
        "  production / paper / P08 / live / shadow.",
        "- No `rcept_dt` defaulted to effective date.",
        "- No `effective_date` inferred from `rcept_dt` fallback.",
        "- No panel / OHLCV used as effective-date proof.",
        "- No card is strategy-ready.",
        "- No C2/C3 wiring.",
        "- No correction row treated as authoritative unless high_validated AND validated.",
        "- No parser feature expansion.",
        "- No `body_unavailable` row treated as parsed or safe.",
        "- No credential committed.",
        "",
        "## Awaiting Referee",
        "",
        "Referee will decide whether to:",
        "- A. close as body coverage completed with residuals,",
        "- B. require another coverage pass,",
        "- C. open correction-linkage full-universe validation,",
        "- D. open delisting / liquidation manual expansion,",
        "- E. keep all strategy research closed.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"[start] body coverage completion — parser {PARSER_VERSION}")

    print("[target] building remaining target...")
    remaining = build_remaining_target()
    write_csv(OUT / "remaining_body_unavailable_target.csv", remaining)
    print(f"[target] {len(remaining)} remaining body_unavailable rows from prior phase")

    cache_info = inventory_cache()
    reinv = write_cache_reinventory(OUT / "cache_reinventory_summary.md",
                                    cache_info, remaining)
    print(f"[cache] {cache_info['unique_rcept_no']} cached; "
          f"{reinv['already_cached_now']} of remaining already cached")

    cached = {p.stem for p in ZIP_CACHE.glob("*.zip")} if ZIP_CACHE.exists() else set()
    plan_info = write_acquisition_plan(OUT / "completion_acquisition_plan.md",
                                       remaining, cached)
    print(f"[plan] to_attempt: {plan_info['to_attempt']}; budget {COMPLETION_BUDGET}")

    print(f"[acquire] downloading up to {COMPLETION_BUDGET} bodies "
          f"(~{COMPLETION_BUDGET * THROTTLE_SEC / 60:.1f} min nominal)...")
    log, summary = acquire_completion(remaining)
    write_csv(OUT / "completion_acquisition_attempt_log.csv", log)
    print(f"[acquire] {summary}")

    print("[parser] re-applying parser 1.1.0...")
    cached = {p.stem for p in ZIP_CACHE.glob("*.zip")}
    post_parser = reapply_parser(remaining, cached)
    write_csv(OUT / "completion_parser_outputs.csv", post_parser)
    print(f"[parser] applied to {len(post_parser)} rows")

    delta = write_coverage_delta(OUT / "completion_coverage_delta_summary.md",
                                 remaining, post_parser, summary)
    print(f"[delta] {delta}")

    holdout = build_holdout(post_parser)
    holdout_classified = classify_holdout(holdout)
    write_csv(OUT / "completion_validation_sample.csv", holdout_classified)
    holdout_info = write_holdout_summary(OUT / "completion_validation_summary.md",
                                          holdout_classified)
    print(f"[holdout] {holdout_info}")

    residual = write_residual_classification(
        OUT / "residual_body_unavailable_classification.csv", log, post_parser,
    )
    print(f"[residual] {len(residual)} body_unavailable classified")

    defects = build_defects(log, residual, holdout_classified)
    write_csv(OUT / "body_completion_defect_ledger.csv", defects)

    gate, coverage_shift = write_gate_status(
        OUT / "body_completion_gate_status.md",
        summary, delta, holdout_info, residual, len(defects),
    )
    write_final_summary(
        OUT / "body_completion_final_summary.md",
        summary, delta, holdout_info, residual, gate, coverage_shift, len(defects),
    )

    print(json.dumps({
        "parser_version": PARSER_VERSION,
        "remaining_target": len(remaining),
        "summary": summary,
        "delta": delta,
        "holdout_info": holdout_info,
        "residual": len(residual),
        "defects": len(defects),
        "gate": gate,
        "coverage_shift_pct": round(coverage_shift, 2),
    }, indent=2))


if __name__ == "__main__":
    main()
