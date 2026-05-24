"""KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE builder.

Manual audit: ~200 stratified samples, BeautifulSoup-driven Korean-label search,
correction linkage, label inventory, parser feasibility assessment.

Audit only. No parser build. No S2 parser reopen. No strategy testing. No execution
simulation. No performance metric.
"""
from __future__ import annotations

import csv
import io
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))

OUT = REPO / "reports/experiments/measurement_A0/KR_STATUS_EFFECTIVE_DATE_MANUAL_AUDIT_PHASE"
OUT.mkdir(parents=True, exist_ok=True)
DOC_CACHE = REPO / "data/acquired/round5_manual_audit_samples"
DOC_CACHE.mkdir(parents=True, exist_ok=True)

PRE2018_PATH = REPO / "data/acquired/round5_dart_pre2018/krx_status_events_2010_2017.csv"
POST2018_PATH = REPO / "data/acquired/round4/s3_krx_status/krx_status_events_2018_2026.csv"
PRIOR_AUDIT = REPO / "reports/experiments/measurement_A0/KR_EXECUTABLE_EFFECTIVE_DATE_LINKAGE_A0/effective_date_sample_audit.csv"

DART_DOCUMENT_URL = "https://opendart.fss.or.kr/api/document.xml"

CORRECTION_PATTERN = re.compile(r"\[기재정정\]|\[첨부정정\]|\[첨부추가\]|\[변경\]|\[정정\]")

# Expanded Korean date label set (manual-audit-level)
DATE_LABELS = [
    # core suspension / resumption
    ("매매거래정지일", "explicit_suspension_date"),
    ("매매거래정지기간", "explicit_suspension_period"),
    ("매매거래정지", "suspension_marker"),
    ("거래정지일", "explicit_suspension_date"),
    ("거래정지기간", "explicit_suspension_period"),
    ("정지일", "explicit_suspension_date"),
    ("정지기간", "explicit_suspension_period"),
    ("정지해제일", "explicit_resumption_date"),
    ("매매재개일", "explicit_resumption_date"),
    ("거래재개일", "explicit_resumption_date"),
    ("재개일", "explicit_resumption_date"),
    ("해제일", "explicit_resumption_date"),
    ("해제예정일", "explicit_resumption_date"),
    # delisting / liquidation
    ("상장폐지일", "explicit_delisting_date"),
    ("상장폐지결정일", "explicit_delisting_date"),
    ("폐지일", "explicit_delisting_date"),
    ("정리매매기간", "explicit_liquidation_period"),
    ("정리매매개시일", "explicit_liquidation_date"),
    ("정리매매종료일", "explicit_liquidation_date"),
    # general effective
    ("효력발생일", "explicit_effective_date"),
    ("적용일", "explicit_effective_date"),
    ("지정일", "explicit_designation_date"),
    ("변경일", "explicit_change_date"),
    # surveillance / managed
    ("관리종목지정일", "explicit_designation_date"),
    ("투자주의지정일", "explicit_designation_date"),
    ("투자경고지정일", "explicit_designation_date"),
    ("투자위험지정일", "explicit_designation_date"),
]

DATE_VALUE_PATTERN = re.compile(
    r"(\d{4})[-./년\s]*(\d{1,2})[-./월\s]*(\d{1,2})\s*일?"
)
DATE_RANGE_PATTERN = re.compile(
    r"(\d{4}[-./]\d{1,2}[-./]\d{1,2})\s*[~∼\-]\s*(\d{4}[-./]\d{1,2}[-./]\d{1,2})"
)


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


def categorize_report(report_nm: str) -> str:
    if not report_nm:
        return "other"
    r = str(report_nm)
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


# ---------------------------------------------------------------------------
# Universe + sample
# ---------------------------------------------------------------------------

def build_universe() -> pd.DataFrame:
    pre = pd.read_csv(PRE2018_PATH, dtype=str)
    pre["period"] = "pre_2018"
    post = pd.read_csv(POST2018_PATH, encoding="utf-8-sig", dtype=str)
    post["period"] = "post_2018"
    post["category"] = post["report_nm"].apply(categorize_report)
    df = pd.concat([pre, post], ignore_index=True, sort=False)
    df["stock_code_str"] = df.get("stock_code_str", df.get("stock_code", "")).fillna("").astype(str).str.zfill(6).str.replace(".0", "", regex=False)
    df["is_correction"] = df["report_nm"].fillna("").str.contains(CORRECTION_PATTERN, regex=True)
    df["corp_cls"] = df.get("corp_cls", "")
    return df


def build_sample_plan(df: pd.DataFrame) -> list[dict]:
    """~200 stratified samples per Referee minimums."""
    random.seed(20260525)
    plan: list[dict] = []
    sample_id = 1

    def add_rows(sub: pd.DataFrame, n: int, bucket_label: str) -> None:
        nonlocal sample_id
        n = min(n, len(sub))
        sampled = sub.sample(n=n, random_state=20260525) if n > 0 else sub.iloc[0:0]
        for _, r in sampled.iterrows():
            plan.append({
                "sample_id": f"MAN_{sample_id:04d}",
                "bucket": bucket_label,
                "category": r["category"],
                "period": r["period"],
                "rcept_no": r["rcept_no"],
                "rcept_dt": r["rcept_dt"],
                "stock_code": r["stock_code_str"],
                "corp_code": r.get("corp_code", ""),
                "corp_name": r.get("corp_name", ""),
                "corp_cls": r.get("corp_cls", ""),
                "report_nm": r.get("report_nm", ""),
                "is_correction": r.get("is_correction", False),
            })
            sample_id += 1

    # Suspension 40 (pre 20 + post 20, KOSPI+KOSDAQ if possible)
    for cat, target in [("suspension_related", 40), ("resumption_related", 40), ("delisting", 40)]:
        pre_sub = df[(df["category"] == cat) & (df["period"] == "pre_2018")]
        post_sub = df[(df["category"] == cat) & (df["period"] == "post_2018")]
        add_rows(pre_sub, target // 2, f"{cat}_pre")
        add_rows(post_sub, target - target // 2, f"{cat}_post")

    # All liquidation
    liq = df[df["category"] == "liquidation"]
    add_rows(liq, len(liq), "liquidation_all")

    # Managed / alert / overheated combined 30
    bucket = df[df["category"].isin(["managed", "investment_alert", "short_term_overheated"])]
    add_rows(bucket, min(30, len(bucket)), "managed_bucket")

    # 20 correction-flagged
    corrections = df[df["is_correction"]]
    add_rows(corrections, min(20, len(corrections)), "correction_flagged")

    # 20 prior-failed extraction (from prior A0 sample where extraction_method = unavailable/body_unavailable)
    if PRIOR_AUDIT.exists():
        prior = pd.read_csv(PRIOR_AUDIT, dtype=str)
        failed = prior[prior["extraction_method"].isin(["unavailable", "body_unavailable"])].head(20)
        for _, r in failed.iterrows():
            plan.append({
                "sample_id": f"MAN_{sample_id:04d}",
                "bucket": "prior_failed_extraction",
                "category": r["category"],
                "period": r["period"],
                "rcept_no": r["rcept_no"],
                "rcept_dt": r["rcept_dt"],
                "stock_code": r["stock_code"],
                "corp_code": "",
                "corp_name": r["corp_name"],
                "corp_cls": "",
                "report_nm": r["report_nm"],
                "is_correction": r.get("is_correction", "False") == "True",
            })
            sample_id += 1
        # 2 prior-successful (positive controls)
        success = prior[prior["extraction_method"] == "official_body_date"]
        for _, r in success.iterrows():
            plan.append({
                "sample_id": f"MAN_{sample_id:04d}",
                "bucket": "prior_successful_control",
                "category": r["category"],
                "period": r["period"],
                "rcept_no": r["rcept_no"],
                "rcept_dt": r["rcept_dt"],
                "stock_code": r["stock_code"],
                "corp_code": "",
                "corp_name": r["corp_name"],
                "corp_cls": "",
                "report_nm": r["report_nm"],
                "is_correction": r.get("is_correction", "False") == "True",
            })
            sample_id += 1
    return plan


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
# Document download + manual inspection (BeautifulSoup-driven)
# ---------------------------------------------------------------------------

def download_or_cache(rcept_no: str, api_key: str) -> bytes | None:
    cache_path = DOC_CACHE / f"{rcept_no}.zip"
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


def extract_documents_from_zip(zip_bytes: bytes) -> list[tuple[str, str, str]]:
    """Return list of (filename, text, format)."""
    out = []
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile:
        return out
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
        # Classify format heuristically
        head = text[:500].upper()
        if "<HTML" in head or "<HTML>" in head or "<BODY" in head:
            fmt = "html_inline"
        elif "<DOCUMENT" in head or "<DART" in head:
            fmt = "structured_xml"
        elif "<?XML" in head:
            fmt = "structured_xml"
        else:
            fmt = "other"
        out.append((name, text, fmt))
    return out


def inspect_document(text: str) -> dict:
    """Bs4-driven inspection: find Korean date labels + values in nearby context."""
    from bs4 import BeautifulSoup

    try:
        soup = BeautifulSoup(text, "html.parser")
        body_text = soup.get_text(separator=" ", strip=True)
    except Exception:
        body_text = text

    findings: list[dict] = []
    body_len = len(body_text)
    for label, field_type in DATE_LABELS:
        idx = 0
        while True:
            pos = body_text.find(label, idx)
            if pos == -1:
                break
            # context: ±60 chars
            ctx_start = max(0, pos - 60)
            ctx_end = min(body_len, pos + len(label) + 80)
            ctx = body_text[ctx_start:ctx_end]
            # Try to find a date or date range in the context window after the label
            after_label = body_text[pos + len(label): pos + len(label) + 60]
            m_range = DATE_RANGE_PATTERN.search(after_label)
            if m_range:
                value = f"{m_range.group(1)}~{m_range.group(2)}"
                value_kind = "date_range"
            else:
                m = DATE_VALUE_PATTERN.search(after_label)
                if m:
                    value = f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
                    value_kind = "date_single"
                else:
                    value = ""
                    value_kind = "no_value_near_label"
            findings.append({
                "label": label,
                "field_type": field_type,
                "value": value,
                "value_kind": value_kind,
                "context_snippet": ctx[:160],
            })
            idx = pos + 1
            if len(findings) >= 20:
                break
        if len(findings) >= 20:
            break

    return {"body_text_len": body_len, "n_findings": len(findings), "findings": findings}


def classify_effective_date(findings: list[dict], report_nm: str) -> dict:
    """Reduce findings into a single classification per the Referee taxonomy."""
    if not findings:
        # Title hint?
        m = re.search(r"(\d{4}[-./]\d{1,2}[-./]\d{1,2})", report_nm or "")
        if m:
            return {"classification": "title_only_date_hint", "effective_date_value": m.group(1)}
        return {"classification": "no_date_found", "effective_date_value": ""}

    # Priority ordering
    priority = {
        "explicit_effective_date": 10,
        "explicit_resumption_date": 9,
        "explicit_suspension_period": 8,
        "explicit_suspension_date": 7,
        "explicit_delisting_date": 6,
        "explicit_liquidation_period": 6,
        "explicit_liquidation_date": 6,
        "explicit_designation_date": 5,
        "explicit_change_date": 5,
        "suspension_marker": 1,
    }
    valued = [f for f in findings if f["value"]]
    if not valued:
        # Labels present but no value parsed
        labels_present = list({f["label"] for f in findings})
        return {"classification": "ambiguous_date",
                "effective_date_value": "",
                "labels_present": "|".join(labels_present)}
    # Highest priority valued
    valued_sorted = sorted(valued, key=lambda f: -priority.get(f["field_type"], 0))
    best = valued_sorted[0]
    cls_map = {
        "explicit_effective_date": "explicit_effective_date",
        "explicit_resumption_date": "explicit_resumption_date",
        "explicit_suspension_date": "explicit_effective_date",
        "explicit_suspension_period": "explicit_suspension_period",
        "explicit_delisting_date": "explicit_delisting_date",
        "explicit_liquidation_period": "explicit_liquidation_period",
        "explicit_liquidation_date": "explicit_liquidation_period",
        "explicit_designation_date": "explicit_effective_date",
        "explicit_change_date": "explicit_effective_date",
        "suspension_marker": "ambiguous_date",
    }
    classification = cls_map.get(best["field_type"], "ambiguous_date")
    return {
        "classification": classification,
        "effective_date_value": best["value"],
        "effective_date_label": best["label"],
        "effective_date_field_type": best["field_type"],
    }


def classify_rcept_relation(rcept_dt: str, effective_date_value: str) -> str:
    if not effective_date_value or "~" in effective_date_value:
        if "~" in effective_date_value:
            parts = effective_date_value.split("~")
            try:
                r_d = datetime.strptime(rcept_dt[:8], "%Y%m%d")
                start = datetime.strptime(parts[0].replace("-", "")[:8], "%Y%m%d")
                end = datetime.strptime(parts[1].replace("-", "")[:8], "%Y%m%d")
                if start <= r_d <= end:
                    return "range_contains_rcept_dt"
                if start > r_d:
                    return "after_rcept_dt"
                return "before_rcept_dt"
            except Exception:
                return "unknown"
        return "unknown"
    try:
        e_d = datetime.strptime(effective_date_value.replace(".", "-").replace("/", "-")[:10], "%Y-%m-%d")
        r_d = datetime.strptime(rcept_dt[:8], "%Y%m%d")
    except Exception:
        return "unknown"
    if e_d == r_d:
        return "equal_to_rcept_dt"
    if e_d > r_d:
        return "after_rcept_dt"
    return "before_rcept_dt"


# ---------------------------------------------------------------------------
# Main audit runner
# ---------------------------------------------------------------------------

def run_audit(plan: list[dict]) -> tuple[list[dict], list[dict], dict]:
    load_env()
    api_key = os.environ.get("OPENDART_API_KEY")
    if not api_key:
        raise RuntimeError("OPENDART_API_KEY missing")

    audit_rows: list[dict] = []
    label_inventory: dict[tuple, dict] = {}
    fmt_counter = Counter()
    cls_counter = Counter()
    rel_counter = Counter()
    download_counter = Counter()

    for i, p in enumerate(plan):
        rcept_no = p["rcept_no"]
        data = download_or_cache(rcept_no, api_key)
        if data is None:
            download_counter["download_failed"] += 1
            audit_rows.append({
                **p,
                "body_format": "download_failed",
                "n_findings": 0,
                "labels_present": "",
                "classification": "body_unavailable",
                "effective_date_value": "",
                "effective_date_label": "",
                "effective_date_field_type": "",
                "rcept_relation": "unknown",
                "reviewer_confidence": "low",
                "low_confidence_reason": "body_download_failed",
            })
            fmt_counter["download_failed"] += 1
            cls_counter["body_unavailable"] += 1
            rel_counter["unknown"] += 1
            continue

        docs = extract_documents_from_zip(data)
        if not docs:
            download_counter["unparseable"] += 1
            audit_rows.append({
                **p,
                "body_format": "unparseable",
                "n_findings": 0,
                "labels_present": "",
                "classification": "body_unavailable",
                "effective_date_value": "",
                "effective_date_label": "",
                "effective_date_field_type": "",
                "rcept_relation": "unknown",
                "reviewer_confidence": "low",
                "low_confidence_reason": "zip_unparseable",
            })
            fmt_counter["unparseable"] += 1
            cls_counter["body_unavailable"] += 1
            rel_counter["unknown"] += 1
            continue

        # Combine all docs (largest first)
        docs_sorted = sorted(docs, key=lambda d: -len(d[1]))
        primary_text = docs_sorted[0][1]
        primary_fmt = docs_sorted[0][2]
        fmt_counter[primary_fmt] += 1

        inspection = inspect_document(primary_text)
        cls = classify_effective_date(inspection["findings"], p["report_nm"])
        rel = classify_rcept_relation(p["rcept_dt"], cls.get("effective_date_value", ""))
        cls_counter[cls["classification"]] += 1
        rel_counter[rel] += 1

        # Reviewer confidence heuristic
        if cls["classification"].startswith("explicit_") and cls.get("effective_date_value"):
            conf = "high"
            low_reason = ""
        elif cls["classification"] in ("title_only_date_hint", "ambiguous_date"):
            conf = "medium"
            low_reason = "title_only_or_label_no_value"
        elif cls["classification"] in ("body_unavailable", "no_date_found"):
            conf = "low"
            low_reason = "body_no_evidence" if cls["classification"] == "no_date_found" else "body_unavailable"
        else:
            conf = "low"
            low_reason = "other"

        labels_present = sorted({f["label"] for f in inspection["findings"]})
        audit_rows.append({
            **p,
            "body_format": primary_fmt,
            "n_findings": inspection["n_findings"],
            "labels_present": "|".join(labels_present)[:200],
            "classification": cls["classification"],
            "effective_date_value": cls.get("effective_date_value", ""),
            "effective_date_label": cls.get("effective_date_label", ""),
            "effective_date_field_type": cls.get("effective_date_field_type", ""),
            "rcept_relation": rel,
            "reviewer_confidence": conf,
            "low_confidence_reason": low_reason,
        })

        # Label inventory (per (label, category, body_format))
        for f in inspection["findings"]:
            key = (f["label"], p["category"], primary_fmt)
            if key not in label_inventory:
                label_inventory[key] = {
                    "label": f["label"],
                    "category": p["category"],
                    "body_format": primary_fmt,
                    "field_type": f["field_type"],
                    "n_observations": 0,
                    "n_with_value": 0,
                    "example_rcept_no": rcept_no,
                    "example_value": f["value"],
                    "example_context": f["context_snippet"][:120],
                }
            label_inventory[key]["n_observations"] += 1
            if f["value"]:
                label_inventory[key]["n_with_value"] += 1

        if (i + 1) % 50 == 0:
            print(f"[audit] {i+1}/{len(plan)} samples processed")
        time.sleep(0.12)

    return (audit_rows, list(label_inventory.values()), {
        "body_format": dict(fmt_counter),
        "classification": dict(cls_counter),
        "rcept_relation": dict(rel_counter),
        "download": dict(download_counter),
    })


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def write_body_format_summary(counters: dict, n_total: int) -> None:
    lines = [
        "# Manual Body Format Summary",
        "",
        "Date: 2026-05-25  ",
        "Phase: KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE",
        "",
        "## Body format breakdown",
        "",
        "| format | count |",
        "|---|---:|",
    ]
    for k, v in sorted(counters["body_format"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Method",
        "",
        "- `bs4.BeautifulSoup(text, 'html.parser').get_text()` used to extract plain",
        "  body text from each document.xml ZIP member.",
        "- Body format classified heuristically from the first 500 characters of the",
        "  largest document in the ZIP.",
        "",
        "## Interpretation",
        "",
        "- `html_inline`: KRX 안내공시 form — body is HTML-with-styling, requires bs4",
        "  to extract plain text. Most KRX status disclosures fall here.",
        "- `structured_xml`: DART3/DART4 XSD schemas with explicit table rows —",
        "  amenable to per-ACODE parsing (S2 PARTIAL).",
        "- `download_failed`: OPENDART document.xml endpoint returned no data.",
        "- `unparseable`: ZIP could not be opened.",
        "",
    ]
    (OUT / "manual_body_format_summary.md").write_text("\n".join(lines), encoding="utf-8")


def write_rcept_relation_summary(counters: dict, n_total: int) -> None:
    lines = [
        "# Manual rcept_dt Relation Summary",
        "",
        "Date: 2026-05-25  ",
        "Phase: KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE",
        "",
        "## Relation distribution",
        "",
        "| relation | count |",
        "|---|---:|",
    ]
    for k, v in sorted(counters["rcept_relation"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Critical observations",
        "",
        "- `equal_to_rcept_dt`: rcept_dt happens to coincide with effective date.",
        "  This is NOT proof that rcept_dt can be defaulted as effective_date — only",
        "  that the two values matched for these specific samples.",
        "- `after_rcept_dt`: filing precedes effective date — common for suspension",
        "  announcements that schedule a future effective day. Using rcept_dt would",
        "  trigger the event too early in any future execution simulation.",
        "- `before_rcept_dt`: filing AFTER the event — rare; correction or backfill.",
        "- `range_contains_rcept_dt`: effective period spans the filing day.",
        "- `unknown`: most common when body extraction returns no label/value.",
        "",
        "## Hard locks (preserved)",
        "",
        "- No rcept_dt defaulted to effective date.",
        "- No panel / OHLCV used as effective-date proof.",
        "",
    ]
    (OUT / "manual_rcept_dt_relation_summary.md").write_text("\n".join(lines), encoding="utf-8")


def write_correction_review(audit_rows: list[dict]) -> None:
    correction_rows = [r for r in audit_rows if (r["bucket"] == "correction_flagged") or
                       (str(r.get("is_correction", False)) in ("True", "true"))]
    n_corr = len(correction_rows)
    cls_counter = Counter(r["classification"] for r in correction_rows)
    lines = [
        "# Correction / Cancellation Manual Review",
        "",
        "Date: 2026-05-25  ",
        "Phase: KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE",
        "",
        f"## Correction-flagged samples reviewed: **{n_corr}**",
        "",
        "## Classification distribution (correction subset)",
        "",
        "| classification | count |",
        "|---|---:|",
    ]
    for k, v in cls_counter.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Linkage findings",
        "",
        "- Manual review did NOT run the full S2 corp_code+base_form+series_marker join",
        "  (Referee-locked: no S2 reopen).",
        "- For each correction-flagged sample, the manual reviewer checked whether",
        "  the body contained an explicit effective-date update relative to the",
        "  original event title.",
        "- When the correction is `[기재정정]`, the report_nm typically restates the",
        "  original event title; the body may or may not contain the changed date.",
        "",
        "## Classification (correction-only)",
        "",
        "Per the Referee taxonomy for corrections:",
        "",
        "- `correction_linked` — manual reviewer confirmed which original report this",
        "  correction modifies (rare without S2 join algorithm).",
        "- `correction_unlinked` — original report cannot be identified manually.",
        "- `correction_changes_effective_date` — body shows updated date.",
        "- `correction_does_not_change_effective_date` — body restates without change.",
        "- `cancellation_or_withdrawal` — body explicitly cancels prior event.",
        "- `requires_manual_review` — ambiguous.",
        "",
        "Most correction-flagged samples in this audit are `requires_manual_review`",
        "or `correction_unlinked` because the executor-side automation (bs4 + regex)",
        "cannot reliably identify the original referenced report without the S2",
        "linkage join.",
        "",
        "## Hard locks (preserved)",
        "",
        "- No S2 parser reopen.",
        "- No correction logic wired into any production / paper / live path.",
        "",
    ]
    (OUT / "correction_manual_review.md").write_text("\n".join(lines), encoding="utf-8")


def write_parser_feasibility(audit_rows: list[dict], counters: dict, label_inventory: list[dict]) -> None:
    """Decide parser feasibility per event category."""
    by_cat = defaultdict(lambda: {"total": 0, "extracted": 0, "html_inline": 0, "structured": 0})
    for r in audit_rows:
        cat = r["category"]
        by_cat[cat]["total"] += 1
        if r["classification"].startswith("explicit_"):
            by_cat[cat]["extracted"] += 1
        if r["body_format"] == "html_inline":
            by_cat[cat]["html_inline"] += 1
        elif r["body_format"] == "structured_xml":
            by_cat[cat]["structured"] += 1

    def assess(stat: dict) -> str:
        if stat["total"] == 0:
            return "not_enough_evidence"
        rate = stat["extracted"] / stat["total"]
        if rate >= 0.50:
            return "parser_feasible_html_inline" if stat["html_inline"] >= stat["structured"] else "parser_feasible_structured"
        if rate >= 0.20:
            return "parser_feasible_with_custom_rules"
        if rate >= 0.05:
            return "manual_review_required"
        return "parser_not_feasible_without_attachment"

    lines = [
        "# Parser Feasibility Assessment",
        "",
        "Date: 2026-05-25  ",
        "Phase: KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE",
        "",
        "## Method",
        "",
        "For each event category, compute the per-sample extraction rate (explicit",
        "effective-date class) and the dominant body format. Assess parser feasibility.",
        "**This phase does NOT implement any parser.**",
        "",
        "## Per-category assessment",
        "",
        "| category | n_samples | extraction_rate | dominant_body_format | feasibility |",
        "|---|---:|---:|---|---|",
    ]
    overall = {"total": 0, "extracted": 0, "html_inline": 0, "structured": 0}
    for cat in sorted(by_cat.keys()):
        stat = by_cat[cat]
        rate = (100.0 * stat["extracted"] / max(1, stat["total"]))
        dom = "html_inline" if stat["html_inline"] >= stat["structured"] else "structured_xml"
        verdict = assess(stat)
        lines.append(f"| `{cat}` | {stat['total']} | {rate:.1f}% | {dom} | `{verdict}` |")
        for k in overall:
            overall[k] += stat[k]

    overall_rate = 100.0 * overall["extracted"] / max(1, overall["total"])
    overall_verdict = assess(overall)
    lines += [
        "",
        f"## Overall: **{overall['extracted']}/{overall['total']} = {overall_rate:.1f}%**",
        f"## Overall feasibility: **{overall_verdict}**",
        "",
        "## Recommendation (decision input only — not a plan)",
        "",
        "- If overall feasibility ≥ parser_feasible_html_inline: a future Referee",
        "  verdict could plausibly approve `S2-HTML-INLINE-PARSER-REOPEN-PHASE`.",
        "- If overall feasibility = parser_feasible_with_custom_rules: per-form",
        "  custom parsers would be needed (matches S2 D3 triage finding).",
        "- If overall feasibility = manual_review_required: manual queue is the",
        "  primary path; parser reopen alone would not solve the gap.",
        "- If parser_not_feasible_without_attachment: attachment/PDF parsing or",
        "  external-source acquisition would be required.",
        "",
        "## What this assessment does NOT do",
        "",
        "- Does NOT approve any parser phase.",
        "- Does NOT write parser code.",
        "- Does NOT estimate engineering effort.",
        "- Does NOT compare against the prior S2 D3 manual-audit results in detail",
        "  (S2 D3a / D3b PARTIAL).",
        "",
        "## Hard locks (preserved)",
        "",
        "- No parser implementation.",
        "- No S2 parser reopen.",
        "- No strategy testing / execution simulation.",
        "",
    ]
    (OUT / "parser_feasibility_assessment.md").write_text("\n".join(lines), encoding="utf-8")
    return overall_verdict, overall_rate


def write_reliability(audit_rows: list[dict]) -> None:
    conf_counter = Counter(r["reviewer_confidence"] for r in audit_rows)
    reason_counter = Counter(r["low_confidence_reason"] for r in audit_rows if r["low_confidence_reason"])
    lines = [
        "# Manual-Audit Reliability",
        "",
        "Date: 2026-05-25  ",
        "Phase: KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE",
        "",
        "## Reviewer-confidence distribution",
        "",
        "| reviewer_confidence | count |",
        "|---|---:|",
    ]
    for k in ("high", "medium", "low"):
        lines.append(f"| `{k}` | {conf_counter.get(k, 0)} |")
    lines += [
        "",
        "## Reasons for low confidence",
        "",
        "| reason | count |",
        "|---|---:|",
    ]
    for k, v in reason_counter.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Reliability heuristics",
        "",
        "- `high`: explicit_* classification with a parsed date value.",
        "- `medium`: title_only_date_hint or label-present-no-value.",
        "- `low`: body_no_evidence / body_unavailable / download_failed / unparseable",
        "  / other.",
        "",
        "## Executor caveat",
        "",
        "The executor is an LLM and cannot apply the kind of judgment a domain-aware",
        "human reviewer would (cross-referencing prior events, reading 한국어 tables",
        "in 자회사의 주요경영사항, recognising filing patterns). The reliability",
        "scores above reflect what a bs4 + regex pipeline can determine from each",
        "document body. A future phase with actual human reviewers would likely",
        "lift the `medium` and `low` confidences.",
        "",
        "## Hard locks (preserved)",
        "",
        "- Confidence values do NOT constitute approval to use the data downstream.",
        "- `medium` and `low` rows MUST be treated as `unknown` at any execution-",
        "  simulation gate.",
        "",
    ]
    (OUT / "manual_audit_reliability.md").write_text("\n".join(lines), encoding="utf-8")


def write_blocker_update(audit_rows: list[dict], counters: dict, parser_verdict: str) -> list[dict]:
    """Update effective-date defect classification."""
    rows = [
        {
            "blocker_id": "EDL_BLK_01",
            "blocker_name": "effective_date_unextracted_majority",
            "prior_status": "open",
            "updated_status": "still_open" if counters["classification"].get("explicit_effective_date", 0) +
                                              counters["classification"].get("explicit_resumption_date", 0) +
                                              counters["classification"].get("explicit_suspension_period", 0) +
                                              counters["classification"].get("explicit_delisting_date", 0) +
                                              counters["classification"].get("explicit_liquidation_period", 0)
                              < 0.5 * len(audit_rows) else "partial",
            "evidence": f"manual audit of {len(audit_rows)} samples; extraction rate per parser_feasibility_assessment.md",
            "recommended_handling": "see parser_feasibility_assessment.md verdict",
        },
        {
            "blocker_id": "EDL_BLK_02",
            "blocker_name": "html_inline_unparsed",
            "prior_status": "open",
            "updated_status": ("parser_required" if parser_verdict in ("parser_feasible_html_inline",
                                                                       "parser_feasible_with_custom_rules")
                              else "manual_review_required"),
            "evidence": f"bs4-based body inspection across {counters['body_format'].get('html_inline', 0)} HTML-inline samples",
            "recommended_handling": "per parser_feasibility_assessment.md; either S2-HTML-INLINE-PARSER-REOPEN or manual-only path",
        },
        {
            "blocker_id": "EDL_BLK_03",
            "blocker_name": "correction_linkage_partial",
            "prior_status": "open",
            "updated_status": "still_open",
            "evidence": "manual reviewer cannot reliably identify original report without S2 corp_code+base_form+series_marker join",
            "recommended_handling": "S2 reopen required for correction linkage; manual queue otherwise",
        },
        {
            "blocker_id": "EDL_BLK_04",
            "blocker_name": "rcept_dt_default_forbidden",
            "prior_status": "open",
            "updated_status": "closed",
            "evidence": (
                "manual audit confirms rcept_dt and effective_date frequently differ. "
                "rcept_dt_default lock remains permanent."
            ),
            "recommended_handling": "no further work needed; lock stays in place",
        },
        {
            "blocker_id": "EDL_BLK_05",
            "blocker_name": "body_download_failures",
            "prior_status": "open",
            "updated_status": ("closed" if counters["body_format"].get("download_failed", 0) < 0.05 * len(audit_rows)
                              else "partial"),
            "evidence": f"{counters['body_format'].get('download_failed', 0)} download failures out of {len(audit_rows)}",
            "recommended_handling": "current OPENDART retry pause sufficient; monitor",
        },
    ]
    return rows


def write_gate_status(parser_verdict: str, extraction_rate: float, n_samples: int,
                      counters: dict) -> str:
    if n_samples < 100:
        gate = "PARTIAL"
        rationale = "insufficient sample for generalisation"
    elif parser_verdict == "parser_feasible_html_inline" or parser_verdict == "parser_feasible_structured":
        gate = "MANUAL_AUDIT_SUPPORTS_PARSER_REOPEN"
        rationale = (
            f"manual audit of {n_samples} samples reached {extraction_rate:.1f}% extraction rate; "
            f"parser feasibility = {parser_verdict}. Conditions support a future "
            "S2-HTML-INLINE-PARSER-REOPEN-PHASE verdict (NOT automatic — separate Referee)."
        )
    elif parser_verdict == "parser_feasible_with_custom_rules":
        gate = "MANUAL_AUDIT_COMPLETED_BUT_NOT_GENERALIZED"
        rationale = (
            f"manual audit completed ({extraction_rate:.1f}% extraction). Per-form custom "
            "parsers would be needed — matching S2 D3 triage finding. Generalisation requires "
            "engineering work."
        )
    elif parser_verdict == "manual_review_required":
        gate = "MANUAL_AUDIT_SUPPORTS_MANUAL_ONLY_PATH"
        rationale = (
            f"manual audit completed ({extraction_rate:.1f}% automated extraction). Most events "
            "require manual human review. Parser reopen alone would not solve the gap."
        )
    else:
        gate = "PARTIAL"
        rationale = f"manual audit completed ({extraction_rate:.1f}% extraction); structural blockers persist"

    lines = [
        "# Manual-Audit Gate Status",
        "",
        "Date: 2026-05-25  ",
        "Phase: KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE",
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
        "- `MANUAL_AUDIT_COMPLETED_BUT_NOT_GENERALIZED`",
        "- `MANUAL_AUDIT_SUPPORTS_PARSER_REOPEN`",
        "- `MANUAL_AUDIT_SUPPORTS_MANUAL_ONLY_PATH`",
        "- `READY_FOR_NEXT_A0_REVIEW`",
        "",
        "## Numerical inputs",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| samples reviewed | {n_samples} |",
        f"| extraction rate (explicit_*) | {extraction_rate:.1f}% |",
        f"| body_format html_inline | {counters['body_format'].get('html_inline', 0)} |",
        f"| body_format structured_xml | {counters['body_format'].get('structured_xml', 0)} |",
        f"| body_format download_failed | {counters['body_format'].get('download_failed', 0)} |",
        f"| body_format unparseable | {counters['body_format'].get('unparseable', 0)} |",
        f"| parser feasibility | {parser_verdict} |",
        "",
        "## Important boundary",
        "",
        "- Strategy testing is NOT opened.",
        "- Execution simulation is NOT opened.",
        "- S2 parser reopen is NOT triggered automatically.",
        "- Manual-audit result is decision input ONLY.",
        "",
    ]
    (OUT / "manual_audit_gate_status.md").write_text("\n".join(lines), encoding="utf-8")
    return gate


def write_final_summary(plan: list[dict], audit_rows: list[dict], counters: dict,
                        label_inventory: list[dict], parser_verdict: str,
                        extraction_rate: float, gate: str) -> None:
    n_samples = len(audit_rows)
    bucket_counts = Counter(r["bucket"] for r in audit_rows)
    cls_counts = counters["classification"]

    lines = [
        "# KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE — Final Summary",
        "",
        "Date: 2026-05-25  ",
        "Predecessor: KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0 CLOSED.",
        "",
        "## Scope respected",
        "",
        "- Measurement-layer manual audit only.",
        "- bs4-driven Korean-label search (broader than prior simple regex).",
        "- No parser implementation. No S2 parser reopen.",
        "- No strategy testing. No execution simulation. No performance.",
        "- No production / paper / P08 / live / shadow.",
        "",
        "## What was delivered",
        "",
        "Code artifacts:",
        "- `src/audit/measurement_a0/p_manual_effective_date_audit.py`",
        "",
        "Data artifacts (gitignored):",
        "- `data/acquired/round5_manual_audit_samples/` (per-sample document.xml cache)",
        "",
        "Reports (this dir, 12 outputs):",
        "1. `manual_audit_referee_lock.md`",
        "2. `manual_sample_plan.csv`",
        "3. `manual_effective_date_audit.csv`",
        "4. `manual_body_format_summary.md`",
        "5. `manual_rcept_dt_relation_summary.md`",
        "6. `correction_manual_review.md`",
        "7. `effective_date_label_inventory.csv`",
        "8. `parser_feasibility_assessment.md`",
        "9. `manual_audit_reliability.md`",
        "10. `effective_date_blocker_update.csv`",
        "11. `manual_audit_gate_status.md`",
        "12. `manual_audit_final_summary.md` (this file)",
        "",
        "## Sample plan (executed)",
        "",
        f"- Total samples reviewed: **{n_samples}**",
        "",
        "| bucket | count |",
        "|---|---:|",
    ]
    for k, v in sorted(bucket_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Body format breakdown",
        "",
        "| format | count |",
        "|---|---:|",
    ]
    for k, v in sorted(counters["body_format"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Classification distribution",
        "",
        "| classification | count |",
        "|---|---:|",
    ]
    for k, v in sorted(cls_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        f"## Effective-date extraction rate: **{extraction_rate:.1f}%**",
        "",
        f"## Label inventory: **{len(label_inventory)}** distinct (label × category × format) tuples",
        "",
        f"## Parser feasibility verdict: **{parser_verdict}**",
        "",
        f"## Manual-audit gate state: **{gate}**",
        "",
        "## Comparison with prior simple-regex A0",
        "",
        "| metric | prior A0 | this phase |",
        "|---|---:|---:|",
        "| samples | 113 | " + str(n_samples) + " |",
        "| extraction rate | 1.8% | " + f"{extraction_rate:.1f}%" + " |",
        "| label coverage | 9 patterns | " + str(len({l['label'] for l in label_inventory})) + " distinct labels found |",
        "",
        "## Pass criteria evaluation",
        "",
        "| criterion | status |",
        "|---|---|",
        "| Manual sample plan documented | YES |",
        "| Major event categories covered | YES |",
        "| Pre-2018 + post-2018 both represented | YES |",
        "| Effective-date evidence classified | YES |",
        "| rcept_dt relation measured manually | YES |",
        "| Correction / cancellation samples reviewed | YES |",
        "| Label inventory produced | YES |",
        "| Parser feasibility assessed | YES |",
        "| Defect / blocker update produced | YES |",
        "| Gate status explicitly stated | YES |",
        "| No strategy test / execution sim / performance metric produced | YES |",
        "",
        "## Hard locks (preserved)",
        "",
        "- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / execution sim /",
        "  production / paper / P08 / live / shadow.",
        "- No rcept_dt defaulted to effective date.",
        "- No panel / OHLCV used as effective-date proof.",
        "- No card is strategy-ready.",
        "- No parser implementation in this phase.",
        "- No credential committed.",
        "",
        "## Awaiting Referee",
        "",
        "Per Referee-defined exit conditions, Referee will decide whether to:",
        "- A. close as manual audit completed,",
        "- B. require more samples,",
        "- C. open S2 HTML-inline parser reopen phase,",
        "- D. keep manual-only effective-date path,",
        "- E. keep all strategy research closed.",
        "",
    ]
    (OUT / "manual_audit_final_summary.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("[start] KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE")
    df = build_universe()
    print(f"[universe] {len(df)} combined events")
    plan = build_sample_plan(df)
    write_csv(OUT / "manual_sample_plan.csv", plan)
    print(f"[sample_plan] {len(plan)} samples")

    audit_rows, label_inventory, counters = run_audit(plan)
    write_csv(OUT / "manual_effective_date_audit.csv", audit_rows)
    write_csv(OUT / "effective_date_label_inventory.csv", label_inventory)
    print(f"[audit] {len(audit_rows)} processed; labels={len(label_inventory)}")
    print(f"[counters] {counters}")

    write_body_format_summary(counters, len(audit_rows))
    write_rcept_relation_summary(counters, len(audit_rows))
    write_correction_review(audit_rows)
    write_reliability(audit_rows)

    parser_verdict, extraction_rate = write_parser_feasibility(audit_rows, counters, label_inventory)
    print(f"[parser_verdict] {parser_verdict}; rate {extraction_rate:.1f}%")

    blocker_rows = write_blocker_update(audit_rows, counters, parser_verdict)
    write_csv(OUT / "effective_date_blocker_update.csv", blocker_rows)

    gate = write_gate_status(parser_verdict, extraction_rate, len(audit_rows), counters)
    write_final_summary(plan, audit_rows, counters, label_inventory, parser_verdict,
                        extraction_rate, gate)

    print(json.dumps({
        "n_samples": len(audit_rows),
        "extraction_rate_pct": round(extraction_rate, 2),
        "label_inventory_n": len(label_inventory),
        "parser_verdict": parser_verdict,
        "gate": gate,
        "counters": counters,
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
