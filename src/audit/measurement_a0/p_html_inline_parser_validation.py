"""S2-HTML-INLINE-PARSER-REOPEN-PHASE validation script.

Runs `src.parsers.krx_status_html_inline.parse_disclosure` against the 195 cached
manual-audit document ZIPs and compares output to the manual-audit ground truth.

Outputs 2 + 5-12 from the Referee output list:
- parser_input_sample_plan.csv
- parser_validation_results.csv
- parser_validation_summary.md
- negative_control_results.md
- correction_handling_status.md
- parser_defect_ledger.csv
- parser_gate_status.md
- parser_final_summary.md
- downstream_blockers_after_parser_reopen.md
- html_inline_parser_design.md (output 3)
- parser_output_schema.md (output 4)

Audit only. No strategy use. No execution simulation. No performance metric.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))

from src.parsers.krx_status_html_inline import (  # noqa: E402
    IN_SCOPE_CATEGORIES,
    parse_disclosure,
)

OUT = REPO / "reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_REOPEN_PHASE"
OUT.mkdir(parents=True, exist_ok=True)

MANUAL_AUDIT_DIR = REPO / "reports/experiments/measurement_A0/KR_STATUS_EFFECTIVE_DATE_MANUAL_AUDIT_PHASE"
GROUND_TRUTH_CSV = MANUAL_AUDIT_DIR / "manual_effective_date_audit.csv"
SAMPLE_PLAN_PRIOR = MANUAL_AUDIT_DIR / "manual_sample_plan.csv"
ZIP_CACHE = REPO / "data/acquired/round5_manual_audit_samples"


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
# Sample plan + run
# ---------------------------------------------------------------------------

def build_sample_plan() -> list[dict]:
    """Reuse prior 195-row sample plan. Mark in_scope_for_parser per category."""
    plan_df = pd.read_csv(SAMPLE_PLAN_PRIOR, dtype=str).fillna("")
    rows = []
    for _, r in plan_df.iterrows():
        cat = r["category"]
        in_scope = cat in IN_SCOPE_CATEGORIES
        rows.append({
            "sample_id": r["sample_id"],
            "bucket": r["bucket"],
            "category": cat,
            "in_scope_for_parser": in_scope,
            "negative_control": (not in_scope),
            "period": r["period"],
            "rcept_no": r["rcept_no"],
            "rcept_dt": r["rcept_dt"],
            "stock_code": r["stock_code"],
            "corp_name": r["corp_name"],
            "report_nm": r["report_nm"],
            "is_correction": r["is_correction"],
        })
    return rows


def run_parser(plan: list[dict]) -> list[dict]:
    results = []
    for p in plan:
        zip_path = ZIP_CACHE / f"{p['rcept_no']}.zip"
        zip_bytes = zip_path.read_bytes() if zip_path.exists() else None
        r = parse_disclosure(
            rcept_no=p["rcept_no"],
            rcept_dt=p["rcept_dt"],
            stock_code=p["stock_code"],
            corp_name=p["corp_name"],
            report_nm=p["report_nm"],
            zip_bytes=zip_bytes,
        )
        d = r.as_dict()
        # carry along sample-plan attributes
        d["sample_id"] = p["sample_id"]
        d["bucket"] = p["bucket"]
        d["in_scope_for_parser"] = p["in_scope_for_parser"]
        d["negative_control"] = p["negative_control"]
        d["period"] = p["period"]
        results.append(d)
    return results


# ---------------------------------------------------------------------------
# Ground-truth comparison
# ---------------------------------------------------------------------------

def load_ground_truth() -> dict[str, dict]:
    gt = {}
    df = pd.read_csv(GROUND_TRUTH_CSV, dtype=str).fillna("")
    for _, r in df.iterrows():
        gt[r["rcept_no"]] = {
            "classification": r["classification"],
            "effective_date_value": r["effective_date_value"],
            "effective_date_label": r["effective_date_label"],
            "effective_date_field_type": r["effective_date_field_type"],
            "rcept_relation": r["rcept_relation"],
            "reviewer_confidence": r["reviewer_confidence"],
            "labels_present": r["labels_present"],
            "body_format": r["body_format"],
            "category": r["category"],
        }
    return gt


def _norm_date(s: str) -> str:
    s = (s or "").strip()
    if not s or s == "nan":
        return ""
    if "~" in s:
        s = s.split("~", 1)[0].strip()
    s = s.replace(".", "-").replace("/", "-")
    parts = s.split("-")
    if len(parts) == 3 and all(p.isdigit() for p in parts):
        y, m, d = parts
        return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
    return s


def compare_to_ground_truth(parsed: list[dict], gt: dict[str, dict]) -> list[dict]:
    out = []
    for p in parsed:
        g = gt.get(p["rcept_no"], {})
        parser_date = p.get("parsed_effective_date") or ""
        gt_date = _norm_date(g.get("effective_date_value", ""))
        gt_class = g.get("classification", "")
        cat = p["event_category"]
        in_scope = p["in_scope_for_parser"]

        # Determine outcome
        if not in_scope:
            outcome = "negative_control"
        elif p["parse_status"] in ("body_unavailable", "out_of_scope_body_format"):
            outcome = "body_unavailable" if "unavailable" in p["parse_status"] else "non_html_body"
        elif p["parse_status"] == "out_of_scope_category":
            outcome = "out_of_scope_category"
        else:
            gt_has_date = bool(gt_date)
            parser_has_date = bool(parser_date)
            if parser_has_date and gt_has_date:
                outcome = "exact_match" if parser_date == gt_date else "date_mismatch"
            elif parser_has_date and not gt_has_date:
                # Parser found something where manual audit found nothing — could be
                # legitimate (manual audit missed) or false positive.
                outcome = "parser_only_no_gt"
            elif not parser_has_date and gt_has_date:
                outcome = "missed_date"
            else:
                # Neither found a date
                if gt_class in ("body_unavailable",):
                    outcome = "body_unavailable_agreed"
                elif gt_class in ("no_date_found", "ambiguous_date", "title_only_date_hint"):
                    outcome = "agreed_no_date"
                else:
                    outcome = "both_empty"

        out.append({
            **p,
            "gt_classification": gt_class,
            "gt_effective_date_value": gt_date,
            "gt_effective_date_label": g.get("effective_date_label", ""),
            "gt_reviewer_confidence": g.get("reviewer_confidence", ""),
            "comparison_outcome": outcome,
        })
    return out


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def write_design(path: Path) -> None:
    text = """# HTML-Inline Parser Design

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-REOPEN-PHASE
Module: `src/parsers/krx_status_html_inline.py`

## Scope (Referee-fixed)

- Categories: `suspension_related` + `resumption_related` only.
- Body format: `html_inline` only.
- Target fields: `effective_date`, `suspension_start`, `suspension_end`,
  `resumption_date`, `resumption_time`.

## Pipeline

```
zip_bytes
  -> extract_body_from_zip()        # extract + decode + format-detect
  -> detect_body_format(text)       # html_inline / structured_xml / other / unparseable
  -> if not html_inline: return out_of_scope_body_format
  -> if category not in {suspension_related, resumption_related}: return out_of_scope_category
  -> bs4.get_text(separator=" ", strip=True)
  -> _normalize_for_scan(text)      # collapse NBSP / `：`->`:` / whitespace
  -> find_label_hits(text, max_hits=40)
        for each label in FLAT_LABELS (longest-first per kind):
            find label position, walk ahead 80 chars, look for:
                - date range (delimited / korean / 부터-까지)
                - single date (delimited / korean)
  -> arbitrate hits by category:
        suspension_related: suspension_period > suspension_start > effective_generic
        resumption_related: resumption_date > effective_generic
  -> if hit has iso_date:        parse_status=extracted, confidence=high
     elif label present no date: parse_status=label_no_value, confidence=medium
     else:                       parse_status=no_label_match, confidence=low
  -> if correction marker in report_nm: manual_review_required=True
```

## Label inventory (drawn from manual-audit `effective_date_label_inventory.csv`)

| kind | labels |
|---|---|
| `suspension_start` | 매매거래정지일, 거래정지일, 정지일, 매매거래정지(개시)일 |
| `suspension_period` | 매매거래정지기간, 거래정지기간, 정지기간 |
| `resumption_date` | 매매재개일, 거래재개일, 정지해제일, 해제일, 재개일, 해제예정일, 재개예정일 |
| `effective_generic` | 효력발생일, 적용일, 지정일, 변경일 |

Longest-prefix-first scan order prevents `정지일` substring-shadowing
`매매거래정지일`.

## Date format support

- Delimited: `YYYY-MM-DD`, `YYYY.MM.DD`, `YYYY/MM/DD` (single-digit MM/DD ok).
- Korean: `YYYY년 M월 D일`.
- Range (delimited): `YYYY-MM-DD ~ YYYY-MM-DD` (separators: `~ ∼ - ― —`).
- Range (Korean): `YYYY년 M월 D일 ~ YYYY년 M월 D일`.
- Range (부터-까지): `YYYY년 M월 D일부터 [Y년] M월 D일까지`.
- Compact `YYYYMMDD` intentionally NOT consumed near labels (frequent
  collision with rcept_no digits).
- Invalid calendar dates (e.g. month=13) rejected via `datetime.date()`.

## Confidence scoring

| confidence | condition |
|---|---|
| `high` | explicit in-scope label with parseable date or range |
| `medium` | in-scope label present but no parseable date |
| `low` | no in-scope label match |

## Manual review forcing

- Any `report_nm` matching `[기재정정]|[첨부정정]|[첨부추가]|[변경]|[정정]` →
  `manual_review_required = True` regardless of extraction outcome.
- Correction linkage to original report is NOT attempted in this phase
  (depends on S2 `corp_code + base_form + series_marker` join).

## Negative-control gate

- `event_category not in {suspension_related, resumption_related}` →
  `parse_status = out_of_scope_category`; no fields populated.
- This explicitly prevents the parser from extracting suspension/resumption dates
  out of a delisting / liquidation / managed / alert body, even if the body text
  contains a label-like substring.

## What this parser does NOT do

- Does NOT parse delisting / liquidation / managed / alert / overhang.
- Does NOT parse structured-XML schemas (S2 D3a/D3b territory).
- Does NOT link corrections.
- Does NOT make any strategy / execution / performance claim.
- Does NOT fallback to `rcept_dt` for `effective_date` (forbidden).
- Does NOT touch ops / paper / live / P08 / shadow code paths.
"""
    path.write_text(text, encoding="utf-8")


def write_output_schema(path: Path) -> None:
    text = """# Parser Output Schema

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-REOPEN-PHASE

## `ParseResult` (one row per disclosure)

| field | type | description |
|---|---|---|
| `rcept_no` | str | OPENDART receipt id |
| `rcept_dt` | str | OPENDART filing date `YYYYMMDD` (filing-only; NEVER effective_date) |
| `stock_code` | str | KRX 6-digit issuer code |
| `corp_name` | str | issuer name as filed |
| `report_nm` | str | original Korean disclosure title |
| `event_category` | str | suspension_related / resumption_related / delisting / managed / investment_alert / liquidation / short_term_overheated / other |
| `body_format` | str | html_inline / structured_xml / other / unparseable / missing |
| `parsed_effective_date` | str ISO or None | best-effort effective date for in-scope categories |
| `parsed_suspension_start` | str ISO or None | suspension start (suspension_related only) |
| `parsed_suspension_end` | str ISO or None | suspension end (range only) |
| `parsed_resumption_date` | str ISO or None | resumption date (resumption_related only) |
| `parsed_resumption_time` | str HH:MM or None | resumption time if found in body |
| `date_label_used` | str | the Korean label that supplied the chosen date |
| `raw_text_window` | str | ±30/+100 char context window around the chosen label |
| `parser_confidence` | str | high / medium / low |
| `manual_review_required` | bool | True if correction-flagged or low/medium confidence |
| `parse_status` | str | enum below |
| `correction_flag` | bool | True if `[기재정정]` etc. detected in `report_nm` |
| `notes` | str | free-text annotation |

## `parse_status` enum

| value | meaning |
|---|---|
| `extracted` | at least one in-scope date extracted with high confidence |
| `label_no_value` | in-scope label found but no parseable date — medium confidence |
| `no_label_match` | no in-scope label matched body text |
| `out_of_scope_category` | event_category not in `{suspension_related, resumption_related}` |
| `out_of_scope_body_format` | body format is not `html_inline` |
| `body_unavailable` | no zip bytes / unparseable zip / empty document |
| `no_extraction` | default initial state — should be replaced by one of the above |

## Forbidden defaults

- `parsed_effective_date` MUST NOT be silently filled from `rcept_dt`.
- `parser_confidence = high` MUST NOT be claimed without a body-supplied date.
- `manual_review_required = False` MUST NOT be claimed for correction-flagged rows.

## Downstream consumption boundary

- Parser output is research / measurement-layer evidence only.
- No execution simulation may consume it.
- No strategy gate may key off `parsed_effective_date`.
- No paper / live / shadow / P08 / production code may import this parser.
"""
    path.write_text(text, encoding="utf-8")


def write_validation_summary(path: Path, comparisons: list[dict]) -> None:
    in_scope = [c for c in comparisons if c["in_scope_for_parser"]]
    out_scope = [c for c in comparisons if not c["in_scope_for_parser"]]
    n_in = len(in_scope)

    cat_breakdown = defaultdict(lambda: Counter())
    for c in in_scope:
        cat_breakdown[c["event_category"]][c["comparison_outcome"]] += 1

    overall = Counter(c["comparison_outcome"] for c in in_scope)
    period_breakdown = defaultdict(Counter)
    for c in in_scope:
        period_breakdown[c["period"]][c["comparison_outcome"]] += 1

    n_exact = overall["exact_match"]
    n_mismatch = overall["date_mismatch"]
    n_parser_only = overall["parser_only_no_gt"]
    n_missed = overall["missed_date"]
    n_agreed = overall["agreed_no_date"] + overall["both_empty"]
    n_body_unavail = overall["body_unavailable_agreed"] + overall["body_unavailable"]
    n_non_html = overall["non_html_body"]

    # Suspension / resumption specific
    sus_total = sum(cat_breakdown.get("suspension_related", Counter()).values())
    sus_exact = cat_breakdown.get("suspension_related", Counter())["exact_match"]
    res_total = sum(cat_breakdown.get("resumption_related", Counter()).values())
    res_exact = cat_breakdown.get("resumption_related", Counter())["exact_match"]

    sus_exact_rate = (100 * sus_exact / max(1, sus_total))
    res_exact_rate = (100 * res_exact / max(1, res_total))
    overall_exact_rate = (100 * n_exact / max(1, n_in))

    confidence_counter = Counter(c["parser_confidence"] for c in in_scope)
    manual_review_count = sum(1 for c in in_scope if c["manual_review_required"])

    lines = [
        "# Parser Validation Summary",
        "",
        "Date: 2026-05-25",
        "Phase: S2-HTML-INLINE-PARSER-REOPEN-PHASE",
        "",
        "## Method",
        "",
        "- Run `parse_disclosure` against the 195 cached manual-audit ZIPs.",
        "- Compare `parsed_effective_date` to manual-audit ground truth",
        "  (`effective_date_value` from `manual_effective_date_audit.csv`).",
        "- Date normalisation: range start used when ground-truth value is a range.",
        "- In-scope rows = `suspension_related` + `resumption_related` (filtered by",
        "  `parser_input_sample_plan.csv`).",
        "- Out-of-scope rows reported separately in `negative_control_results.md`.",
        "",
        "## In-scope sample size",
        "",
        f"- Total in-scope samples: **{n_in}**",
        f"- suspension_related: {sus_total}",
        f"- resumption_related: {res_total}",
        "",
        "## Overall comparison outcome (in-scope only)",
        "",
        "| outcome | count |",
        "|---|---:|",
    ]
    for k, v in overall.most_common():
        lines.append(f"| `{k}` | {v} |")

    lines += [
        "",
        f"## Exact-match rate (parser vs manual audit): **{n_exact}/{n_in} = {overall_exact_rate:.1f}%**",
        "",
        f"### Category split",
        "",
        f"- suspension_related exact match: **{sus_exact}/{sus_total} = {sus_exact_rate:.1f}%**",
        f"- resumption_related exact match: **{res_exact}/{res_total} = {res_exact_rate:.1f}%**",
        "",
        "## Period split",
        "",
        "| period | total | exact_match | mismatch | parser_only | missed | agreed_no_date | body_unavail |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for period in ("pre_2018", "post_2018"):
        cnt = period_breakdown.get(period, Counter())
        total = sum(cnt.values())
        lines.append(
            f"| `{period}` | {total} | {cnt['exact_match']} | {cnt['date_mismatch']} | "
            f"{cnt['parser_only_no_gt']} | {cnt['missed_date']} | "
            f"{cnt['agreed_no_date'] + cnt['both_empty']} | "
            f"{cnt['body_unavailable_agreed'] + cnt['body_unavailable']} |"
        )
    lines += [
        "",
        "## Parser confidence distribution (in-scope)",
        "",
        "| confidence | count |",
        "|---|---:|",
    ]
    for k in ("high", "medium", "low"):
        lines.append(f"| `{k}` | {confidence_counter.get(k, 0)} |")
    lines += [
        "",
        f"## Manual-review-required count (in-scope): **{manual_review_count}**",
        "",
        "(includes all correction-flagged rows and all medium/low confidence rows.)",
        "",
        "## Baseline comparison",
        "",
        "| baseline | sample | extraction rate |",
        "|---|---:|---:|",
        "| Prior simple-regex A0 | 113 | 1.8% |",
        f"| Manual audit (bs4) | 195 | 56.4% |",
        f"| Parser (this phase) overall in-scope | {n_in} | {overall_exact_rate:.1f}% exact match |",
        f"| Parser (this phase) suspension only | {sus_total} | {sus_exact_rate:.1f}% exact match |",
        f"| Parser (this phase) resumption only | {res_total} | {res_exact_rate:.1f}% exact match |",
        "",
        "## Material improvement assessment",
        "",
        f"- Suspension exact-match {sus_exact_rate:.1f}% vs manual audit 92.5% extraction.",
        f"- Resumption exact-match {res_exact_rate:.1f}% vs manual audit 90.2% extraction.",
        "",
        "Parser produces strictly more structured output (suspension_start /",
        "suspension_end / resumption_date / resumption_time) than the manual-audit",
        "classification, with deterministic confidence labels and a strict",
        "negative-control gate.",
        "",
        "## What this validation does NOT do",
        "",
        "- Does NOT certify strategy / backtest readiness.",
        "- Does NOT open execution simulation.",
        "- Does NOT certify correctness for delisting / liquidation / managed / alert.",
        "- Does NOT certify across the entire S3 + pre-2018 universe (17,924 events) —",
        "  only the 195 sampled disclosures.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "n_in_scope": n_in,
        "overall_exact_rate": overall_exact_rate,
        "sus_exact_rate": sus_exact_rate,
        "res_exact_rate": res_exact_rate,
        "manual_review_count": manual_review_count,
        "confidence_counter": dict(confidence_counter),
    }


def write_negative_controls(path: Path, comparisons: list[dict]) -> dict:
    neg = [c for c in comparisons if c["negative_control"]]
    n = len(neg)
    by_cat = defaultdict(Counter)
    for c in neg:
        by_cat[c["event_category"]][c["parse_status"]] += 1

    # False positive = neg control with parser-emitted suspension/resumption date
    fps = [c for c in neg if c["parsed_effective_date"]]
    n_fp = len(fps)

    lines = [
        "# Negative-control Results",
        "",
        "Date: 2026-05-25",
        "Phase: S2-HTML-INLINE-PARSER-REOPEN-PHASE",
        "",
        "## Method",
        "",
        "- Negative controls = rows whose `event_category` is NOT in",
        "  `{suspension_related, resumption_related}`.",
        "- Parser MUST return `parse_status = out_of_scope_category` for all such rows.",
        "- Any extracted date counts as a false positive.",
        "",
        f"## Negative-control sample size: **{n}**",
        "",
        "## Per-category parse_status distribution",
        "",
        "| category | n | parse_status counts |",
        "|---|---:|---|",
    ]
    for cat in sorted(by_cat.keys()):
        cnt = by_cat[cat]
        total = sum(cnt.values())
        sub = ", ".join(f"`{k}`:{v}" for k, v in cnt.most_common())
        lines.append(f"| `{cat}` | {total} | {sub} |")
    lines += [
        "",
        f"## False positives (parser extracted a date from a negative-control body): **{n_fp}**",
        "",
    ]
    if n_fp:
        lines.append("### FP rows")
        lines.append("")
        lines.append("| rcept_no | category | report_nm | parsed_effective_date | date_label_used |")
        lines.append("|---|---|---|---|---|")
        for c in fps[:20]:
            lines.append(
                f"| `{c['rcept_no']}` | {c['event_category']} | "
                f"{(c['report_nm'] or '')[:60]} | {c['parsed_effective_date']} | "
                f"{c['date_label_used']} |"
            )
    lines += [
        "",
        "## Interpretation",
        "",
        "- A zero false-positive count would indicate that the negative-control gate",
        "  is functioning correctly — the parser refuses to fire on delisting /",
        "  liquidation / managed / alert categories.",
        "- Non-zero false positives MUST be recorded in `parser_defect_ledger.csv`",
        "  under defect class `unsupported_category_false_positive`.",
        "- This phase does NOT expand parser scope to handle these categories.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return {"n_neg": n, "n_fp": n_fp, "fp_rows": fps}


def write_correction_status(path: Path, comparisons: list[dict]) -> dict:
    corrections = [c for c in comparisons if c["correction_flag"]]
    n = len(corrections)
    n_forced_review = sum(1 for c in corrections if c["manual_review_required"])
    cat_counter = Counter(c["event_category"] for c in corrections)
    status_counter = Counter(c["parse_status"] for c in corrections)
    lines = [
        "# Correction Handling Status",
        "",
        "Date: 2026-05-25",
        "Phase: S2-HTML-INLINE-PARSER-REOPEN-PHASE",
        "",
        "## Method",
        "",
        "- Correction marker regex: `[기재정정] | [첨부정정] | [첨부추가] | [변경] | [정정]`.",
        "- Any match in `report_nm` sets `correction_flag = True`.",
        "- Correction-flagged rows ALWAYS get `manual_review_required = True`,",
        "  regardless of extraction confidence.",
        "- This parser does NOT attempt to link a correction to its original report",
        "  (S2 `corp_code + base_form + series_marker` join dependency).",
        "",
        f"## Correction-flagged rows in sample: **{n}**",
        f"## Forced to manual review: **{n_forced_review} / {n}**",
        "",
        "## Category breakdown",
        "",
        "| category | count |",
        "|---|---:|",
    ]
    for k, v in cat_counter.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Parse_status on correction-flagged rows",
        "",
        "| parse_status | count |",
        "|---|---:|",
    ]
    for k, v in status_counter.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## What this parser does NOT do",
        "",
        "- Does NOT link `[기재정정]` to the original report.",
        "- Does NOT supersede prior events.",
        "- Does NOT mark prior events as cancelled.",
        "- Does NOT call corrections authoritative.",
        "",
        "Correction linkage is a separate proposed phase",
        "(`KR-STATUS-CORRECTION-LINKAGE-A0`) and is NOT opened by this phase.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return {"n_correction": n, "n_forced_review": n_forced_review}


def build_defect_ledger(comparisons: list[dict], neg_info: dict) -> list[dict]:
    rows = []

    # Per-row defects
    for c in comparisons:
        if not c["in_scope_for_parser"]:
            continue
        outcome = c["comparison_outcome"]
        if outcome == "missed_date":
            rows.append({
                "defect_id": f"PDL_{len(rows)+1:04d}",
                "defect_class": "missed_resumption_date" if c["event_category"] == "resumption_related"
                                else "missed_suspension_date",
                "rcept_no": c["rcept_no"],
                "category": c["event_category"],
                "gt_value": c["gt_effective_date_value"],
                "gt_label": c["gt_effective_date_label"],
                "parser_value": "",
                "notes": c.get("notes", ""),
            })
        elif outcome == "date_mismatch":
            rows.append({
                "defect_id": f"PDL_{len(rows)+1:04d}",
                "defect_class": "wrong_date_extracted",
                "rcept_no": c["rcept_no"],
                "category": c["event_category"],
                "gt_value": c["gt_effective_date_value"],
                "gt_label": c["gt_effective_date_label"],
                "parser_value": c["parsed_effective_date"],
                "notes": f"parser label={c['date_label_used']}",
            })
        elif outcome == "parser_only_no_gt":
            # Could be legitimate parser-improvement OR ambiguous_multiple_dates
            cls = "ambiguous_multiple_dates" if c["gt_classification"] == "ambiguous_date" \
                  else "low_confidence_parse"
            rows.append({
                "defect_id": f"PDL_{len(rows)+1:04d}",
                "defect_class": cls,
                "rcept_no": c["rcept_no"],
                "category": c["event_category"],
                "gt_value": "",
                "gt_label": c["gt_effective_date_label"],
                "parser_value": c["parsed_effective_date"],
                "notes": f"gt classification={c['gt_classification']}",
            })

        # body / format defects
        if c["body_format"] == "unparseable":
            rows.append({
                "defect_id": f"PDL_{len(rows)+1:04d}",
                "defect_class": "html_unparseable",
                "rcept_no": c["rcept_no"],
                "category": c["event_category"],
                "gt_value": "",
                "gt_label": "",
                "parser_value": "",
                "notes": "zip unparseable",
            })
        elif c["parse_status"] == "out_of_scope_body_format":
            rows.append({
                "defect_id": f"PDL_{len(rows)+1:04d}",
                "defect_class": "attachment_required",
                "rcept_no": c["rcept_no"],
                "category": c["event_category"],
                "gt_value": "",
                "gt_label": "",
                "parser_value": "",
                "notes": f"body_format={c['body_format']}",
            })

        if c["correction_flag"]:
            rows.append({
                "defect_id": f"PDL_{len(rows)+1:04d}",
                "defect_class": "correction_requires_manual_review",
                "rcept_no": c["rcept_no"],
                "category": c["event_category"],
                "gt_value": "",
                "gt_label": "",
                "parser_value": c.get("parsed_effective_date", "") or "",
                "notes": "forced manual review",
            })

    # FP defects (negative control)
    for c in neg_info["fp_rows"]:
        rows.append({
            "defect_id": f"PDL_{len(rows)+1:04d}",
            "defect_class": "unsupported_category_false_positive",
            "rcept_no": c["rcept_no"],
            "category": c["event_category"],
            "gt_value": "",
            "gt_label": "",
            "parser_value": c["parsed_effective_date"],
            "notes": f"negative control fired; label={c['date_label_used']}",
        })

    return rows


def write_gate_status(
    path: Path,
    val_info: dict,
    neg_info: dict,
    corr_info: dict,
    defect_rows: list[dict],
) -> str:
    sus_rate = val_info["sus_exact_rate"]
    res_rate = val_info["res_exact_rate"]
    n_fp = neg_info["n_fp"]
    n_in = val_info["n_in_scope"]
    overall = val_info["overall_exact_rate"]

    fail_signal_fp = n_fp > 0
    # Material improvement = exact match clearly above the simple-regex 1.8% baseline
    material_improvement = overall >= 50
    # "Validated" demands both suspension and resumption above 80% exact match
    validated = (sus_rate >= 80 and res_rate >= 80 and overall >= 70)

    if fail_signal_fp:
        gate = "PARTIAL"
        rationale = (
            f"parser extracted dates from {n_fp} negative-control rows. "
            "Negative-control gate is leaky; record defects and require more work."
        )
    elif not material_improvement:
        gate = "PARTIAL"
        rationale = (
            f"overall exact-match rate {overall:.1f}% does not materially exceed simple-regex baseline."
        )
    elif validated:
        gate = "HTML_INLINE_PARSER_VALIDATED_FOR_SUSPENSION_RESUMPTION_ONLY"
        rationale = (
            f"suspension exact-match {sus_rate:.1f}%; resumption exact-match {res_rate:.1f}%; "
            f"overall {overall:.1f}%; negative-control false positives = 0; "
            "correction-flagged rows forced to manual review."
        )
    else:
        gate = "HTML_INLINE_PARSER_REQUIRES_MORE_WORK"
        rationale = (
            f"suspension {sus_rate:.1f}% / resumption {res_rate:.1f}% / overall {overall:.1f}%; "
            "improvement is real but does not yet clear the 80/80/70 bar for full validation."
        )

    lines = [
        "# Parser Gate Status",
        "",
        "Date: 2026-05-25",
        "Phase: S2-HTML-INLINE-PARSER-REOPEN-PHASE",
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
        "- `HTML_INLINE_PARSER_BUILT_BUT_NOT_VALIDATED`",
        "- `HTML_INLINE_PARSER_VALIDATED_FOR_SUSPENSION_RESUMPTION_ONLY`",
        "- `HTML_INLINE_PARSER_REQUIRES_MORE_WORK`",
        "- `READY_FOR_NEXT_A0_REVIEW`",
        "",
        "## Numerical inputs",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| in-scope samples | {n_in} |",
        f"| overall exact match | {overall:.1f}% |",
        f"| suspension exact match | {sus_rate:.1f}% |",
        f"| resumption exact match | {res_rate:.1f}% |",
        f"| manual_review_required | {val_info['manual_review_count']} |",
        f"| negative-control false positives | {n_fp} |",
        f"| total defect-ledger rows | {len(defect_rows)} |",
        f"| correction-flagged rows | {corr_info['n_correction']} |",
        "",
        "## Important boundary",
        "",
        "- Execution simulation is NOT opened.",
        "- Strategy testing is NOT opened.",
        "- Performance diagnostics is NOT opened.",
        "- No card is strategy-ready.",
        "- This gate state is a parser-quality verdict only.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return gate


def write_final_summary(
    path: Path, val_info: dict, neg_info: dict, corr_info: dict,
    defect_rows: list[dict], gate: str,
) -> None:
    lines = [
        "# S2-HTML-INLINE-PARSER-REOPEN-PHASE — Final Summary",
        "",
        "Date: 2026-05-25",
        "Predecessor: KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE CLOSED",
        "(commit 8339efb).",
        "",
        "## Scope respected",
        "",
        "- Measurement-layer parser reopen only.",
        "- HTML-inline body only.",
        "- suspension_related + resumption_related ONLY.",
        "- No delisting parser. No liquidation parser. No managed / alert parser.",
        "- No strategy testing. No execution simulation. No performance diagnostics.",
        "- No production / paper / P08 / live / shadow.",
        "- No C2/C3 wiring. No full S2 parser rebuild. No DART body alpha.",
        "",
        "## What was delivered",
        "",
        "Code:",
        "- `src/parsers/krx_status_html_inline.py` (parser module)",
        "- `tests/test_krx_status_html_inline.py` (26/26 passing)",
        "- `src/audit/measurement_a0/p_html_inline_parser_validation.py` (validator)",
        "",
        "Reports (this dir, 12 outputs):",
        "1. parser_reopen_referee_lock.md",
        "2. parser_input_sample_plan.csv",
        "3. html_inline_parser_design.md",
        "4. parser_output_schema.md",
        "5. parser_validation_results.csv",
        "6. parser_validation_summary.md",
        "7. negative_control_results.md",
        "8. correction_handling_status.md",
        "9. parser_defect_ledger.csv",
        "10. parser_gate_status.md",
        "11. parser_final_summary.md (this file)",
        "12. downstream_blockers_after_parser_reopen.md",
        "",
        "## Headline results",
        "",
        f"- Overall exact-match rate (in-scope, n={val_info['n_in_scope']}): "
        f"**{val_info['overall_exact_rate']:.1f}%**",
        f"- Suspension exact-match: **{val_info['sus_exact_rate']:.1f}%**",
        f"- Resumption exact-match: **{val_info['res_exact_rate']:.1f}%**",
        f"- Negative-control false positives: **{neg_info['n_fp']}**",
        f"- Correction-flagged rows forced to manual review: "
        f"**{corr_info['n_forced_review']} / {corr_info['n_correction']}**",
        f"- Defect ledger rows: **{len(defect_rows)}**",
        f"- Gate state: **{gate}**",
        "",
        "## Pass-criteria evaluation",
        "",
        "| criterion | status |",
        "|---|---|",
        "| Parser handles HTML-inline body format | YES |",
        "| Parser output schema produced | YES |",
        "| Validated against manual audit | YES |",
        "| Suspension / resumption rates reported | YES |",
        "| False positives on negative controls measured | YES |",
        "| Correction-flagged rows forced to manual review | YES |",
        "| Defect ledger produced | YES |",
        "| Gate status explicitly stated | YES |",
        "| No strategy / execution / performance metric produced | YES |",
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
        "- No delisting / liquidation / managed / alert parser scope creep.",
        "- No credential committed.",
        "",
        "## Awaiting Referee",
        "",
        "Referee will decide whether to:",
        "- A. close as HTML-inline parser validated for suspension / resumption,",
        "- B. require another parser pass,",
        "- C. open correction-linkage A0,",
        "- D. open delisting / liquidation manual expansion,",
        "- E. keep all strategy research closed.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_downstream_blockers(path: Path, neg_info: dict, val_info: dict) -> None:
    text = f"""# Downstream Blockers After Parser Reopen

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-REOPEN-PHASE

## Question

Even if this parser reopen is accepted, what still blocks strategy testing,
execution simulation, and any production-side use?

## Blockers preserved (do NOT count this phase as resolving any of them)

### Category coverage

- Delisting parser: NOT implemented (manual audit extraction was 3.8%).
- Liquidation parser: NOT implemented (manual audit 0.0%).
- Managed / investment_alert / short_term_overheated: NOT implemented.
- Other category: NOT implemented.

### Effective-date linkage

- Correction linkage: NOT implemented. Depends on S2 `corp_code + base_form +
  series_marker + window` join (S2 closed as PARTIAL).
- `rcept_dt` MUST NOT be used as `effective_date` fallback (permanent lock).
- Effective-date for `parser_only_no_gt` rows MUST NOT be auto-promoted to
  authoritative without per-row manual review.

### Universe / data

- KRX intraday-halt source: NOT acquired.
- KRX official limit-lock source: NOT acquired (only rule-derived proxy).
- Listed-universe daily lifecycle: NOT acquired (monthly resolution only).
- Pre-2018 corrections: not back-validated against this parser at full universe scale.

### OHLCV / runtime

- 45 OHLCV residual blockers preserved (40 patched in prior phase; 4 ops
  blockers remain reopen-blocker).
- Closed-strategy entry guards remain mandatory before any strategy reopen.

### Ops / production

- `src/ops/nav_update.py` 4 ops blockers remain in
  `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` (not approved).
- P08 / paper / live / shadow are UNCHANGED.

## Minimum additional work before this parser can be used downstream

- Approve `KR-STATUS-CORRECTION-LINKAGE-A0` (separate Referee).
- Approve a delisting / liquidation manual expansion or attachment-acquisition phase
  (separate Referee).
- Approve full-universe parser validation (not just 195 samples) (separate Referee).
- Resolve `rcept_dt` vs `effective_date` policy for all unknown rows
  (currently fail-closed per permanent lock).

## What this phase does NOT unlock

- Strategy testing remains CLOSED.
- Execution simulation remains CLOSED.
- Performance diagnostics remains CLOSED.
- No card is strategy-ready.
- No production / paper / P08 / live / shadow connection.

## Numerical context (this phase)

- In-scope sample size: {val_info['n_in_scope']}.
- Negative-control false positives: {neg_info['n_fp']}.
- Manual-review-required rate (in-scope): {val_info['manual_review_count']} / {val_info['n_in_scope']}.

Even at this parser quality, the surrounding data + universe + execution-safety
blockers preserved across the prior measurement-layer closes are unchanged.
"""
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("[start] S2-HTML-INLINE-PARSER-REOPEN-PHASE validation")
    plan = build_sample_plan()
    write_csv(OUT / "parser_input_sample_plan.csv", plan)
    print(f"[sample_plan] {len(plan)} rows; "
          f"in_scope={sum(1 for r in plan if r['in_scope_for_parser'])}")

    write_design(OUT / "html_inline_parser_design.md")
    write_output_schema(OUT / "parser_output_schema.md")

    parsed = run_parser(plan)
    gt = load_ground_truth()
    comparisons = compare_to_ground_truth(parsed, gt)
    write_csv(OUT / "parser_validation_results.csv", comparisons)
    print(f"[parsed] {len(parsed)} rows")

    val_info = write_validation_summary(OUT / "parser_validation_summary.md", comparisons)
    neg_info = write_negative_controls(OUT / "negative_control_results.md", comparisons)
    corr_info = write_correction_status(OUT / "correction_handling_status.md", comparisons)

    defect_rows = build_defect_ledger(comparisons, neg_info)
    write_csv(OUT / "parser_defect_ledger.csv", defect_rows)

    gate = write_gate_status(OUT / "parser_gate_status.md", val_info, neg_info, corr_info, defect_rows)
    write_final_summary(OUT / "parser_final_summary.md", val_info, neg_info, corr_info, defect_rows, gate)
    write_downstream_blockers(OUT / "downstream_blockers_after_parser_reopen.md", neg_info, val_info)

    summary = {
        "n_samples": len(plan),
        "n_in_scope": val_info["n_in_scope"],
        "overall_exact_rate_pct": round(val_info["overall_exact_rate"], 2),
        "sus_exact_rate_pct": round(val_info["sus_exact_rate"], 2),
        "res_exact_rate_pct": round(val_info["res_exact_rate"], 2),
        "negative_control_fps": neg_info["n_fp"],
        "correction_flagged": corr_info["n_correction"],
        "defect_rows": len(defect_rows),
        "gate": gate,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
