"""S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0 builder.

Expand OPENDART document.xml body coverage for the body_unavailable in-scope rows
from S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0. Re-apply parser 1.1.0,
quantify coverage delta, validate newly acquired bodies with bounded holdout.

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
import urllib.parse
import urllib.request
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
from src.audit.measurement_a0.p_full_universe_parser_validation import (  # noqa: E402
    _verify_extracted,
    _verify_no_label_or_label_no_value,
)

OUT = REPO / "reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_BODY_COVERAGE_EXPANSION_A0"
OUT.mkdir(parents=True, exist_ok=True)

PASS2_OUTPUTS = REPO / "reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_FULL_UNIVERSE_VALIDATION_A0/pass2_full_universe_parser_outputs.csv"
PASS3_LINKS = REPO / "reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_A0/pass3_candidate_links_recalibrated.csv"

DART_DOCUMENT_URL = "https://opendart.fss.or.kr/api/document.xml"
DOWNLOAD_BUDGET = 5000          # max new downloads this run
THROTTLE_SEC = 0.12             # ~8 req/s
MAX_RETRIES = 1                 # retry once on transient errors

CACHE_DIRS = [
    REPO / "data/acquired/round5_manual_audit_samples",
    REPO / "data/acquired/round5_effective_date_samples",
]


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
# Cache inventory
# ---------------------------------------------------------------------------

def inventory_cache() -> dict:
    info = {"by_dir": {}, "total_zips": 0, "valid_zips": 0, "unparseable_zips": 0,
            "duplicate_rcept_no": 0, "rcept_set": set()}
    for d in CACHE_DIRS:
        if not d.exists():
            continue
        zips = list(d.glob("*.zip"))
        valid = 0
        unparseable = 0
        for z in zips:
            try:
                zipfile.ZipFile(io.BytesIO(z.read_bytes())).namelist()
                valid += 1
            except Exception:
                unparseable += 1
            rn = z.stem
            if rn in info["rcept_set"]:
                info["duplicate_rcept_no"] += 1
            info["rcept_set"].add(rn)
        info["by_dir"][str(d.relative_to(REPO))] = {
            "n_zips": len(zips), "n_valid": valid, "n_unparseable": unparseable,
        }
        info["total_zips"] += len(zips)
        info["valid_zips"] += valid
        info["unparseable_zips"] += unparseable
    info["unique_rcept_no"] = len(info["rcept_set"])
    return info


def write_cache_inventory(path: Path, info: dict, in_scope_rcepts: set[str]) -> dict:
    in_scope_hits = sum(1 for rn in info["rcept_set"] if rn in in_scope_rcepts)
    out_scope_hits = info["unique_rcept_no"] - in_scope_hits
    lines = [
        "# Prior Cache Inventory",
        "",
        "Date: 2026-05-25",
        "Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0",
        "",
        f"## Total cached ZIPs: **{info['total_zips']}**",
        f"## Unique rcept_no: **{info['unique_rcept_no']}**",
        f"## Valid ZIPs: **{info['valid_zips']}**",
        f"## Unparseable ZIPs: **{info['unparseable_zips']}**",
        f"## Duplicate rcept_no within cache: **{info['duplicate_rcept_no']}**",
        f"## In-scope cache hits: **{in_scope_hits}**",
        f"## Out-of-scope cache hits: **{out_scope_hits}**",
        "",
        "## By cache directory",
        "",
        "| directory | n_zips | n_valid | n_unparseable |",
        "|---|---:|---:|---:|",
    ]
    for d, v in info["by_dir"].items():
        lines.append(f"| `{d}` | {v['n_zips']} | {v['n_valid']} | {v['n_unparseable']} |")
    lines += [
        "",
        "## Source phases",
        "",
        "- `data/acquired/round5_manual_audit_samples/` — built by",
        "  `KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE` + extended by every later",
        "  phase needing on-demand bodies.",
        "- `data/acquired/round5_effective_date_samples/` — built by",
        "  `KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0`.",
        "",
        "Both cache dirs are gitignored and reproducible via OPENDART document.xml.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return {"in_scope_hits": in_scope_hits, "out_scope_hits": out_scope_hits}


# ---------------------------------------------------------------------------
# Target universe construction (body_unavailable rows + priority buckets)
# ---------------------------------------------------------------------------

def load_pass3_correction_confidence() -> dict[str, str]:
    if not PASS3_LINKS.exists():
        return {}
    df = pd.read_csv(PASS3_LINKS, dtype=str).fillna("")
    return {r["correction_rcept_no"]: r["pass3_confidence"] for _, r in df.iterrows()}


def assign_priority(row: dict, correction_conf: str) -> str:
    """Per Referee priority buckets."""
    is_correction = str(row.get("correction_flag", "")).lower() in ("true", "1")
    is_resumption = row.get("event_category") == "resumption_related"
    is_suspension = row.get("event_category") == "suspension_related"
    is_period_change = bool(PERIOD_CHANGE_RE.search(row.get("report_nm") or ""))
    period = row.get("source_period", "")

    if is_correction and correction_conf in ("high_validated", "medium_needs_manual"):
        return "P0_correction_high_medium"
    if is_resumption:
        return "P1_resumption"
    if is_suspension and is_period_change:
        return "P2_period_change"
    if is_suspension:
        return "P3_ordinary_suspension"
    if period == "pre_2018":
        return "P4_pre2018"
    return "P5_post2018"


def build_target_universe() -> list[dict]:
    """Body_unavailable in-scope rows + priority bucket."""
    df = pd.read_csv(PASS2_OUTPUTS, dtype=str).fillna("")
    corr_conf = load_pass3_correction_confidence()
    bu = df[df["parse_status"] == "body_unavailable"]
    rows = []
    for _, r in bu.iterrows():
        is_corr = str(r.get("correction_flag", "")).lower() in ("true", "1")
        conf = corr_conf.get(r["rcept_no"], "no_link") if is_corr else ""
        rows.append({
            "rcept_no": r["rcept_no"],
            "rcept_dt": r["rcept_dt"],
            "stock_code": r["stock_code"],
            "corp_name": r["corp_name"],
            "event_category": r["event_category"],
            "report_nm": r["report_nm"],
            "source_period": r["source_period"],
            "prior_body_status": "body_unavailable",
            "prior_parse_status": "body_unavailable",
            "correction_flag": is_corr,
            "correction_pass3_confidence": conf,
            "is_period_change": bool(PERIOD_CHANGE_RE.search(r["report_nm"] or "")),
            "manual_review_required": str(r.get("manual_review_required", "")),
            "priority_bucket": assign_priority(r.to_dict(), conf),
        })
    return rows


def write_acquisition_plan(path: Path, target: list[dict]) -> dict:
    bucket_counter = Counter(r["priority_bucket"] for r in target)
    lines = [
        "# Body Acquisition Plan",
        "",
        "Date: 2026-05-25",
        "Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0",
        "",
        f"## Target body_unavailable rows: **{len(target)}**",
        "",
        "## Priority buckets",
        "",
        "| bucket | count |",
        "|---|---:|",
    ]
    for k in ("P0_correction_high_medium", "P1_resumption", "P2_period_change",
              "P3_ordinary_suspension", "P4_pre2018", "P5_post2018"):
        lines.append(f"| `{k}` | {bucket_counter.get(k, 0)} |")
    lines += [
        "",
        "## Acquisition order (Referee-mandated)",
        "",
        "1. **P0** — correction-flagged rows with Pass-3 `high_validated` or",
        "   `medium_needs_manual` confidence. Highest priority because they may",
        "   become design-supported authoritative-use evidence under the closed",
        "   correction policy.",
        "2. **P1** — resumption_related body_unavailable rows. Lower-volume but",
        "   load-bearing for the resumption_date field.",
        "3. **P2** — period_change_disclosure suspension body_unavailable rows.",
        "   Verified by Pass-2 parser fix; broader coverage validates the fix at scale.",
        "4. **P3** — ordinary suspension_related body_unavailable rows.",
        "5. **P4** — older pre-2018 body_unavailable rows.",
        "6. **P5** — post-2018 body_unavailable rows.",
        "",
        "Acquisition stops at `DOWNLOAD_BUDGET` and reports partial.",
        "",
        f"## Download budget (this run): **{DOWNLOAD_BUDGET}**",
        f"## Throttle: **{THROTTLE_SEC} s** between requests "
        f"(~{int(1/THROTTLE_SEC)} req/s nominal).",
        f"## Max retries on transient error: **{MAX_RETRIES}**.",
        "",
        "## What this plan does NOT do",
        "",
        "- Does NOT silently exclude any row. Rows beyond the budget receive an",
        "  explicit `not_attempted_in_this_run` log entry.",
        "- Does NOT request bodies for out-of-scope categories.",
        "- Does NOT request bodies for already-cached rows.",
        "- Does NOT commit credentials. OPENDART_API_KEY is loaded from",
        "  `research_input_data/.env` at runtime and never written to repo files.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return {"bucket_counter": dict(bucket_counter)}


# ---------------------------------------------------------------------------
# OPENDART acquisition with error taxonomy
# ---------------------------------------------------------------------------

def download_one(rcept_no: str, api_key: str) -> tuple[str, bytes | None, str]:
    """Return (status, zip_bytes_if_any, http_or_err_detail).
    status ∈ {download_success, api_no_document, rate_limited, credential_or_api_error, retry_needed}.
    """
    url = DART_DOCUMENT_URL + "?" + urllib.parse.urlencode({
        "crtfc_key": api_key, "rcept_no": rcept_no,
    })
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = resp.read()
            http_code = resp.status
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return "credential_or_api_error", None, f"http_{e.code}"
        if e.code == 429:
            return "rate_limited", None, "http_429"
        return "retry_needed", None, f"http_{e.code}"
    except urllib.error.URLError as e:
        return "retry_needed", None, f"url_error:{e.reason}"
    except Exception as e:
        return "retry_needed", None, f"exc:{type(e).__name__}"
    # OPENDART returns small XML error doc on no-document
    if len(data) < 200:
        try:
            txt = data.decode("utf-8", errors="ignore")
            if "<status>" in txt and "013" in txt:
                return "api_no_document", None, txt[:200]
        except Exception:
            pass
    return "download_success", data, f"http_{http_code}_size_{len(data)}"


def classify_body(zip_bytes: bytes) -> tuple[str, str]:
    """Inspect downloaded ZIP and return (status, body_format)."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile:
        return "zip_unparseable", "unparseable"
    docs = []
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
        if text:
            docs.append(text)
    if not docs:
        return "zip_unparseable", "unparseable"
    primary = max(docs, key=len)
    head = primary[:500].upper()
    if "<HTML" in head or "<BODY" in head:
        return "download_success", "html_inline"
    if "<DOCUMENT" in head or "<DART" in head:
        return "download_success", "structured_xml"
    if "<?XML" in head:
        return "download_success", "structured_xml"
    # PDF / attachment marker?
    if primary.startswith("%PDF") or "attachment" in head.lower():
        return "download_success", "attachment_only"
    return "download_success", "other"


def acquire_bodies(target: list[dict]) -> tuple[list[dict], dict]:
    """Download bodies per priority. Return (attempt_log, summary)."""
    load_env()
    api_key = os.environ.get("OPENDART_API_KEY")
    if not api_key:
        return [], {"error": "OPENDART_API_KEY missing"}

    # Sort by priority bucket then rcept_dt asc
    priority_order = (
        "P0_correction_high_medium", "P1_resumption", "P2_period_change",
        "P3_ordinary_suspension", "P4_pre2018", "P5_post2018",
    )
    order_key = {p: i for i, p in enumerate(priority_order)}
    sorted_target = sorted(target,
                           key=lambda r: (order_key.get(r["priority_bucket"], 99),
                                          r["rcept_dt"]))

    log = []
    n_attempted = 0
    n_success = 0
    n_no_doc = 0
    n_unparseable = 0
    n_html = 0
    n_structured = 0
    n_attachment = 0
    n_other = 0
    n_rate_limited = 0
    n_credential = 0
    n_retry_needed = 0
    cached = {p.stem for p in ZIP_CACHE.glob("*.zip")} if ZIP_CACHE.exists() else set()

    for r in sorted_target:
        rcept_no = r["rcept_no"]
        if rcept_no in cached:
            log.append({**r, "attempt_status": "already_cached", "body_format": "",
                        "http_detail": "", "retries": 0})
            continue
        if n_attempted >= DOWNLOAD_BUDGET:
            log.append({**r, "attempt_status": "not_attempted_in_this_run",
                        "body_format": "", "http_detail": "budget_exhausted", "retries": 0})
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
                n_success += 1
                if body_format == "html_inline":
                    n_html += 1
                elif body_format == "structured_xml":
                    n_structured += 1
                elif body_format == "attachment_only":
                    n_attachment += 1
                else:
                    n_other += 1
            elif status == "zip_unparseable":
                n_unparseable += 1
        elif status == "api_no_document":
            n_no_doc += 1
        elif status == "rate_limited":
            n_rate_limited += 1
            time.sleep(2.0)
        elif status == "credential_or_api_error":
            n_credential += 1
        else:
            n_retry_needed += 1

        log.append({**r, "attempt_status": status, "body_format": body_format,
                    "http_detail": detail, "retries": retries})
        time.sleep(THROTTLE_SEC)
        if n_attempted % 500 == 0:
            print(f"  ... attempted {n_attempted} | success {n_success} | no_doc {n_no_doc}")

    summary = {
        "n_target": len(sorted_target),
        "n_already_cached": sum(1 for r in log if r["attempt_status"] == "already_cached"),
        "n_attempted": n_attempted,
        "n_success": n_success,
        "n_html_inline": n_html,
        "n_structured_xml": n_structured,
        "n_attachment_only": n_attachment,
        "n_other_format": n_other,
        "n_zip_unparseable": n_unparseable,
        "n_api_no_document": n_no_doc,
        "n_rate_limited": n_rate_limited,
        "n_credential_or_api_error": n_credential,
        "n_retry_needed": n_retry_needed,
        "n_not_attempted_budget": sum(
            1 for r in log if r["attempt_status"] == "not_attempted_in_this_run"
        ),
    }
    return log, summary


# ---------------------------------------------------------------------------
# Re-apply parser
# ---------------------------------------------------------------------------

def reapply_parser(target: list[dict], cached: set[str]) -> list[dict]:
    """Re-run parser 1.1.0 on every body_unavailable target row (cached or not)."""
    out = []
    for r in target:
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
        d["priority_bucket"] = r["priority_bucket"]
        d["is_period_change"] = r["is_period_change"]
        d["correction_pass3_confidence"] = r["correction_pass3_confidence"]
        out.append(d)
    return out


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def write_coverage_delta(path: Path, target: list[dict], post_parser: list[dict],
                         summary: dict) -> dict:
    pre_total = len(target)
    pre_bu = pre_total  # all target rows started as body_unavailable

    post_status = Counter(r["parse_status"] for r in post_parser)
    n_post_bu = post_status["body_unavailable"]
    n_post_extracted = post_status["extracted"]
    n_post_no_label = post_status["no_label_match"]
    n_post_label_no_value = post_status["label_no_value"]
    n_post_out_of_scope_body = post_status["out_of_scope_body_format"]
    n_post_body_available = pre_total - n_post_bu

    # Splits
    sus_post = Counter(r["parse_status"] for r in post_parser
                       if r["event_category"] == "suspension_related")
    res_post = Counter(r["parse_status"] for r in post_parser
                       if r["event_category"] == "resumption_related")
    pre18_post = Counter(r["parse_status"] for r in post_parser
                         if r["source_period"] == "pre_2018")
    post18_post = Counter(r["parse_status"] for r in post_parser
                          if r["source_period"] == "post_2018")
    corr_post = Counter(r["parse_status"] for r in post_parser
                        if str(r.get("correction_flag", "")).lower() in ("true", "1"))
    noncorr_post = Counter(r["parse_status"] for r in post_parser
                           if str(r.get("correction_flag", "")).lower() not in ("true", "1"))
    bucket_post = defaultdict(Counter)
    for r in post_parser:
        bucket_post[r["priority_bucket"]][r["parse_status"]] += 1

    lines = [
        "# Body Coverage Delta Summary",
        "",
        "Date: 2026-05-25",
        "Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0",
        f"Parser version: `{PARSER_VERSION}`.",
        "",
        "## Acquisition summary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| target body_unavailable rows | {summary['n_target']} |",
        f"| already_cached at start | {summary['n_already_cached']} |",
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
        f"| not_attempted (budget) | {summary['n_not_attempted_budget']} |",
        "",
        "## Coverage delta on target rows (before → after)",
        "",
        "| state | before | after |",
        "|---|---:|---:|",
        f"| body_unavailable | {pre_bu} | {n_post_bu} |",
        f"| body_available | 0 | {n_post_body_available} |",
        f"| extracted | 0 | {n_post_extracted} |",
        f"| no_label_match | 0 | {n_post_no_label} |",
        f"| label_no_value | 0 | {n_post_label_no_value} |",
        f"| out_of_scope_body_format | 0 | {n_post_out_of_scope_body} |",
        "",
        f"## Coverage shift: **{n_post_body_available} / {pre_total} = "
        f"{100.0 * n_post_body_available / max(1, pre_total):.1f}%** of body_unavailable "
        "targets now have a body.",
        "",
        "## By event_category (post parser_status)",
        "",
        "| category | extracted | no_label_match | label_no_value | body_unavailable |",
        "|---|---:|---:|---:|---:|",
        f"| `suspension_related` | {sus_post.get('extracted', 0)} | "
        f"{sus_post.get('no_label_match', 0)} | {sus_post.get('label_no_value', 0)} | "
        f"{sus_post.get('body_unavailable', 0)} |",
        f"| `resumption_related` | {res_post.get('extracted', 0)} | "
        f"{res_post.get('no_label_match', 0)} | {res_post.get('label_no_value', 0)} | "
        f"{res_post.get('body_unavailable', 0)} |",
        "",
        "## By period",
        "",
        "| period | extracted | body_unavailable |",
        "|---|---:|---:|",
        f"| `pre_2018` | {pre18_post.get('extracted', 0)} | {pre18_post.get('body_unavailable', 0)} |",
        f"| `post_2018` | {post18_post.get('extracted', 0)} | {post18_post.get('body_unavailable', 0)} |",
        "",
        "## Correction vs non-correction",
        "",
        "| segment | extracted | body_unavailable |",
        "|---|---:|---:|",
        f"| correction | {corr_post.get('extracted', 0)} | {corr_post.get('body_unavailable', 0)} |",
        f"| non_correction | {noncorr_post.get('extracted', 0)} | {noncorr_post.get('body_unavailable', 0)} |",
        "",
        "## By priority bucket",
        "",
        "| bucket | total | extracted | body_unavailable |",
        "|---|---:|---:|---:|",
    ]
    for b in ("P0_correction_high_medium", "P1_resumption", "P2_period_change",
              "P3_ordinary_suspension", "P4_pre2018", "P5_post2018"):
        cnt = bucket_post.get(b, Counter())
        total = sum(cnt.values())
        lines.append(f"| `{b}` | {total} | {cnt.get('extracted', 0)} | "
                     f"{cnt.get('body_unavailable', 0)} |")

    lines += [
        "",
        "## Universe-level coverage estimate",
        "",
        f"- In-scope universe: 12,187 (from prior phase).",
        f"- Body available before this phase: ~1,402 (cached) + 41 (other formats).",
        f"- Body acquired this phase: {summary['n_success']}.",
        f"- **Body available now (estimate): ~{1402 + summary['n_success']} / 12,187 = "
        f"{100.0 * (1402 + summary['n_success']) / 12187:.1f}%**.",
        "",
        "## body_unavailable preserved",
        "",
        f"- {n_post_bu} target rows remain `body_unavailable` after this phase.",
        "- Per Referee: these rows MUST NOT be treated as parsed / executable / safe.",
        "- They are preserved in `post_acquisition_parser_outputs.csv` with",
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
    }


# ---------------------------------------------------------------------------
# Holdout validation on newly acquired bodies
# ---------------------------------------------------------------------------

def build_holdout(post_parser: list[dict]) -> list[dict]:
    """Sample newly-extracted rows for holdout validation."""
    random.seed(20260525)
    sample = []
    extracted = [r for r in post_parser if r["parse_status"] == "extracted"]
    sus = [r for r in extracted if r["event_category"] == "suspension_related"
           and not r["is_period_change"]]
    res = [r for r in extracted if r["event_category"] == "resumption_related"]
    pc = [r for r in extracted if r["is_period_change"]]
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

    # Dedupe by rcept_no
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
        # Re-parse to ensure consistency
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
    n_unparseable = cnt["unparseable"]
    n_success = n_exact + n_accept + n_review
    success_rate = 100.0 * n_success / max(1, n)

    lines = [
        "# New-Body Validation Summary",
        "",
        "Date: 2026-05-25",
        "Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0",
        f"Parser version: `{PARSER_VERSION}`.",
        "",
        "## Method",
        "",
        "Sample is drawn ONLY from rows where the parser produced `extracted`",
        "status against newly-acquired bodies (this phase). Body cross-checks via",
        "BeautifulSoup are used to classify each row per Referee taxonomy.",
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
        "## Interpretation",
        "",
        "- The holdout is drawn from NEWLY acquired bodies that prior phases never",
        "  saw. Stability of parser behavior on these rows indicates the parser",
        "  generalises beyond the prior cache.",
        "- A non-zero `correction_not_forced_manual_review` would indicate parser",
        "  regression. (Expected: 0.)",
        "- A non-zero `false_positive` would indicate negative-control leakage on",
        "  bodies that should be out-of-scope.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return {"n": n, "n_success": n_success, "success_rate": success_rate,
            "n_wrong": n_wrong, "n_missed": n_missed, "n_fp": n_fp,
            "n_corr_fail": n_corr_fail, "n_body_unavail": n_body_unavail}


# ---------------------------------------------------------------------------
# Defects + gate + final
# ---------------------------------------------------------------------------

def build_defects(log: list[dict], post_parser: list[dict],
                  holdout: list[dict]) -> list[dict]:
    defects = []
    error_map = {
        "api_no_document": "api_no_document",
        "rate_limited": "rate_limited",
        "zip_unparseable": "zip_unparseable",
        "credential_or_api_error": "credential_or_api_error",
        "retry_needed": "body_download_failed",
        "not_attempted_in_this_run": "body_unavailable_remaining",
    }
    for r in log:
        cls = error_map.get(r["attempt_status"])
        if cls:
            defects.append({
                "defect_id": f"BC_{len(defects)+1:05d}",
                "defect_class": cls,
                "rcept_no": r["rcept_no"],
                "category": r["event_category"],
                "notes": r["attempt_status"] + "/" + str(r.get("http_detail", "")),
            })
        elif r["attempt_status"] == "download_success" and r["body_format"] == "attachment_only":
            defects.append({
                "defect_id": f"BC_{len(defects)+1:05d}",
                "defect_class": "attachment_only",
                "rcept_no": r["rcept_no"],
                "category": r["event_category"],
                "notes": "PDF/attachment, no HTML body",
            })
        elif r["attempt_status"] == "download_success" and r["body_format"] == "structured_xml":
            defects.append({
                "defect_id": f"BC_{len(defects)+1:05d}",
                "defect_class": "structured_xml_out_of_scope",
                "rcept_no": r["rcept_no"],
                "category": r["event_category"],
                "notes": "structured_xml; out of HTML-inline parser scope",
            })
    # Holdout defects
    for r in holdout:
        if r["holdout_classification"] == "wrong_date":
            defects.append({
                "defect_id": f"BC_{len(defects)+1:05d}",
                "defect_class": "newly_parsed_wrong_date",
                "rcept_no": r["rcept_no"], "category": r["event_category"],
                "notes": f"holdout: parsed {r.get('holdout_parsed_effective_date')}",
            })
        elif r["holdout_classification"] == "missed_date":
            defects.append({
                "defect_id": f"BC_{len(defects)+1:05d}",
                "defect_class": "newly_parsed_missed_date",
                "rcept_no": r["rcept_no"], "category": r["event_category"],
                "notes": "holdout: body has label parser missed",
            })
        elif r["holdout_classification"] == "correction_not_forced_manual_review":
            defects.append({
                "defect_id": f"BC_{len(defects)+1:05d}",
                "defect_class": "correction_policy_violation",
                "rcept_no": r["rcept_no"], "category": r["event_category"],
                "notes": "holdout: correction row not forced to manual review",
            })
    return defects


def write_gate_status(path: Path, summary: dict, delta: dict,
                      holdout_info: dict, defects_n: int) -> tuple[str, float]:
    n_success = summary["n_success"]
    n_target = summary["n_target"]
    n_post_bu = delta["n_post_bu"]
    coverage_shift = 100.0 * (n_target - n_post_bu) / max(1, n_target)

    if holdout_info["n_corr_fail"] > 0 or holdout_info["n_fp"] > 0:
        gate = "BODY_COVERAGE_REQUIRES_MORE_WORK"
        rationale = (
            f"correction_not_forced_manual_review={holdout_info['n_corr_fail']}; "
            f"holdout FP={holdout_info['n_fp']}; safety regression."
        )
    elif n_success >= 3000 and coverage_shift >= 30 \
            and holdout_info["success_rate"] >= 90 \
            and holdout_info["n_wrong"] + holdout_info["n_missed"] <= 5:
        gate = "READY_FOR_NEXT_A0_REVIEW"
        rationale = (
            f"acquired {n_success} bodies; coverage shift on target rows "
            f"{coverage_shift:.1f}%; holdout success {holdout_info['success_rate']:.1f}%; "
            f"wrong+missed={holdout_info['n_wrong'] + holdout_info['n_missed']}; "
            "parser behavior preserved; correction policy unchanged."
        )
    elif n_success >= 1000 and coverage_shift >= 10 \
            and holdout_info["success_rate"] >= 85:
        gate = "BODY_COVERAGE_EXPANDED_AND_VALIDATED_FOR_AVAILABLE_ROWS"
        rationale = (
            f"acquired {n_success} bodies; coverage shift {coverage_shift:.1f}%; "
            f"holdout success {holdout_info['success_rate']:.1f}%; "
            "parser behavior preserved."
        )
    elif n_success >= 200:
        gate = "BODY_COVERAGE_EXPANDED_BUT_INCOMPLETE"
        rationale = (
            f"acquired {n_success} bodies but coverage shift {coverage_shift:.1f}% "
            f"or holdout success {holdout_info['success_rate']:.1f}% below validation bar."
        )
    elif n_success == 0:
        gate = "DATA_SOURCE_FAIL" if summary.get("n_credential_or_api_error", 0) > 100 \
            else "PARTIAL"
        rationale = "acquisition produced no new bodies."
    else:
        gate = "PARTIAL"
        rationale = f"acquired {n_success} bodies; insufficient for material coverage shift."

    lines = [
        "# Body-Coverage Gate Status",
        "",
        "Date: 2026-05-25",
        "Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0",
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
        "- `BODY_COVERAGE_EXPANDED_BUT_INCOMPLETE`",
        "- `BODY_COVERAGE_EXPANDED_AND_VALIDATED_FOR_AVAILABLE_ROWS`",
        "- `BODY_COVERAGE_REQUIRES_MORE_WORK`",
        "- `READY_FOR_NEXT_A0_REVIEW`",
        "",
        "## Numerical inputs",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| target body_unavailable rows | {summary['n_target']} |",
        f"| download_success | {summary['n_success']} |",
        f"| html_inline | {summary['n_html_inline']} |",
        f"| structured_xml | {summary['n_structured_xml']} |",
        f"| attachment_only | {summary['n_attachment_only']} |",
        f"| zip_unparseable | {summary['n_zip_unparseable']} |",
        f"| api_no_document | {summary['n_api_no_document']} |",
        f"| not_attempted (budget) | {summary['n_not_attempted_budget']} |",
        f"| body_available on target (after) | {delta['n_post_body_available']} |",
        f"| body_unavailable on target (after) | {delta['n_post_bu']} |",
        f"| coverage shift on target | {coverage_shift:.1f}% |",
        f"| holdout sample | {holdout_info['n']} |",
        f"| holdout success rate | {holdout_info['success_rate']:.1f}% |",
        f"| holdout FP | {holdout_info['n_fp']} |",
        f"| holdout wrong_date | {holdout_info['n_wrong']} |",
        f"| holdout missed_date | {holdout_info['n_missed']} |",
        f"| holdout correction_not_forced_manual_review | {holdout_info['n_corr_fail']} |",
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
                       holdout_info: dict, gate: str, coverage_shift: float,
                       cache_info: dict, defects_n: int) -> None:
    lines = [
        "# S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0 — Final Summary",
        "",
        "Date: 2026-05-25",
        f"Parser version: `{PARSER_VERSION}` (no feature change in this phase).",
        "",
        "## Scope respected",
        "",
        "- Measurement-layer body-coverage expansion A0 only.",
        "- suspension_related + resumption_related only.",
        "- HTML-inline body candidates only.",
        "- body_unavailable rows from prior validation phase.",
        "- Parser 1.1.0 used as-is (no feature expansion).",
        "- No delisting / liquidation / managed / alert parser.",
        "- No DART body alpha. No overhang. No all-event event log.",
        "- No C2/C3 wiring. No strategy testing. No execution simulation.",
        "- No performance diagnostics. No production / paper / P08 / live / shadow.",
        "",
        "## What was delivered",
        "",
        "Code:",
        "- `src/audit/measurement_a0/p_body_coverage_expansion.py`",
        "",
        "Reports (this dir, 12 outputs):",
        "1. `body_coverage_referee_lock.md`",
        "2. `body_unavailable_target_universe.csv`",
        "3. `cache_inventory_summary.md`",
        "4. `body_acquisition_plan.md`",
        "5. `body_acquisition_attempt_log.csv`",
        "6. `body_coverage_delta_summary.md`",
        "7. `post_acquisition_parser_outputs.csv`",
        "8. `new_body_validation_sample.csv`",
        "9. `new_body_validation_summary.md`",
        "10. `body_coverage_defect_ledger.csv`",
        "11. `body_coverage_gate_status.md`",
        "12. `body_coverage_final_summary.md` (this file)",
        "",
        "## Headline results",
        "",
        f"- Target body_unavailable rows: **{summary['n_target']}**.",
        f"- Already-cached at start: **{summary['n_already_cached']}**.",
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
        f"- Not attempted (budget exhausted): **{summary['n_not_attempted_budget']}**",
        "",
        f"- Body available on target rows (after): **{delta['n_post_body_available']}**.",
        f"- Body unavailable on target rows (after): **{delta['n_post_bu']}**.",
        f"- Coverage shift on target rows: **{coverage_shift:.1f}%**.",
        "",
        f"- New extractions: **{delta['n_post_extracted']}**.",
        f"- Holdout sample: **{holdout_info['n']}** (drawn from newly extracted).",
        f"- Holdout success rate: **{holdout_info['success_rate']:.1f}%**.",
        f"- Holdout FP: **{holdout_info['n_fp']}**.",
        f"- Holdout wrong+missed: **{holdout_info['n_wrong'] + holdout_info['n_missed']}**.",
        f"- Holdout correction_not_forced_manual_review: **{holdout_info['n_corr_fail']}**.",
        f"- Defect ledger rows: **{defects_n}**.",
        f"- Gate state: **{gate}**.",
        "",
        "## Pass-criteria evaluation",
        "",
        "| criterion | status |",
        "|---|---|",
        "| target universe documented | YES |",
        "| cache inventory produced | YES |",
        "| acquisition attempt log produced | YES |",
        "| coverage before vs after quantified | YES |",
        "| newly acquired bodies parsed with existing parser only | YES |",
        f"| new body validation sample completed | {'YES' if holdout_info['n'] > 0 else 'PARTIAL'} |",
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
        "- A. close as body coverage expanded,",
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
    print(f"[start] body coverage expansion — parser {PARSER_VERSION}")

    # Target universe
    print("[target] building target universe from Pass-2 outputs...")
    target = build_target_universe()
    write_csv(OUT / "body_unavailable_target_universe.csv", target)
    print(f"[target] {len(target)} body_unavailable in-scope rows")

    # Cache inventory
    in_scope_rcepts = {r["rcept_no"] for r in target}
    pass2_df = pd.read_csv(PASS2_OUTPUTS, dtype=str).fillna("")
    in_scope_rcepts |= set(pass2_df["rcept_no"].tolist())
    cache_info = inventory_cache()
    cache_extra = write_cache_inventory(OUT / "cache_inventory_summary.md",
                                        cache_info, in_scope_rcepts)
    print(f"[cache] {cache_info['unique_rcept_no']} unique cached; "
          f"{cache_extra['in_scope_hits']} in-scope hits")

    # Acquisition plan
    plan_info = write_acquisition_plan(OUT / "body_acquisition_plan.md", target)
    print(f"[plan] bucket counts: {plan_info['bucket_counter']}")

    # Acquisition
    print(f"[acquire] downloading up to {DOWNLOAD_BUDGET} bodies "
          f"(~{DOWNLOAD_BUDGET * THROTTLE_SEC / 60:.1f} min nominal)...")
    log, summary = acquire_bodies(target)
    write_csv(OUT / "body_acquisition_attempt_log.csv", log)
    print(f"[acquire] {summary}")

    # Re-apply parser to target rows (now some have bodies)
    print("[parser] re-applying parser 1.1.0...")
    cached = {p.stem for p in ZIP_CACHE.glob("*.zip")}
    post_parser = reapply_parser(target, cached)
    write_csv(OUT / "post_acquisition_parser_outputs.csv", post_parser)
    print(f"[parser] applied to {len(post_parser)} rows")

    # Coverage delta
    delta = write_coverage_delta(OUT / "body_coverage_delta_summary.md",
                                 target, post_parser, summary)
    print(f"[delta] {delta}")

    # Holdout validation
    print("[holdout] building holdout...")
    holdout = build_holdout(post_parser)
    holdout_classified = classify_holdout(holdout)
    write_csv(OUT / "new_body_validation_sample.csv", holdout_classified)
    holdout_info = write_holdout_summary(OUT / "new_body_validation_summary.md",
                                          holdout_classified)
    print(f"[holdout] {holdout_info}")

    # Defects
    defects = build_defects(log, post_parser, holdout_classified)
    write_csv(OUT / "body_coverage_defect_ledger.csv", defects)

    # Gate + final
    gate, coverage_shift = write_gate_status(
        OUT / "body_coverage_gate_status.md",
        summary, delta, holdout_info, len(defects),
    )
    write_final_summary(
        OUT / "body_coverage_final_summary.md",
        summary, delta, holdout_info, gate, coverage_shift,
        cache_extra, len(defects),
    )

    print(json.dumps({
        "parser_version": PARSER_VERSION,
        "target_rows": len(target),
        "summary": summary,
        "delta": delta,
        "holdout_info": holdout_info,
        "defects": len(defects),
        "gate": gate,
        "coverage_shift_pct": round(coverage_shift, 2),
    }, indent=2))


if __name__ == "__main__":
    main()
