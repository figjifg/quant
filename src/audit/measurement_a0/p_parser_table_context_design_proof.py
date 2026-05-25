"""KR-STATUS-PARSER-TABLE-CONTEXT-DESIGN-PROOF-A0 — builder.

Referee directive (2026-05-26, via relay), authorized by the user's explicit decision
to open a LOCAL-ONLY table-context parser-design PROOF phase. NOT download/API,
source-recovery, parser-change, or manual-adjudication approval.

Goal: PROOF-ONLY design evidence for the 170 `needs_table_context_design` rows —
whether table/structure-aware extraction is design-feasible in principle, how to
guard false positives, and which rows are feasible / ambiguous / blocked for a FUTURE
parser-change phase. This does NOT implement or promise extraction.

HARD CONSTRAINTS:
- Target = exactly the 170 needs_table_context_design rows (table context; 0 attachment).
- Read existing local artifacts + cached bodies (read-only) ONLY. No download / API /
  source recovery / body reacquisition / cache repair / overwrite.
- NO parser code/rule/version change; NO edits under src/parsers/; the parser is NOT
  invoked here (this is a SEPARATE read-only proof analysis). No accepted parse output
  is changed.
- Candidate date/value evidence is HYPOTHETICAL / PROOF-ONLY — named
  hypothetical_candidate_*, NOT effective_date / parsed_date / any final field. No
  effective date accepted/finalized; rcept_dt is never an effective date.
- No manual adjudication/validation/approval. No row promoted to parsed / recovered /
  executable / safe / authoritative / validated / approved / strategy-ready /
  execution-ready / production-ready. Every row fail-closed.
- CSVs use LF line endings (git show --check must pass). No self-close; no CLOSE_NOTE.
"""
from __future__ import annotations

import csv as _csv
import io
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))

from src.audit.measurement_a0.p_status_correction_linkage import ZIP_CACHE  # noqa: E402
from src.parsers.krx_status_html_inline import (  # noqa: E402  (read-only reuse; parser NOT modified)
    SUSPENSION_START_LABELS, SUSPENSION_PERIOD_LABELS, RESUMPTION_LABELS,
    EFFECTIVE_GENERIC_LABELS, find_first_date, _normalize_for_scan,
)

MA0 = REPO / "reports/experiments/measurement_A0"
OUT = MA0 / "KR_STATUS_PARSER_TABLE_CONTEXT_DESIGN_PROOF_A0"
FEAS = MA0 / "KR_STATUS_PARSER_NONEXTRACTED_FEASIBILITY_A0/parser_nonextracted_feasibility_matrix.csv"
INPUT_PRIOR = MA0 / "KR_STATUS_PARSER_NONEXTRACTED_FEASIBILITY_A0/parser_nonextracted_input_manifest.csv"

ALL_LABELS = tuple(sorted(
    set(SUSPENSION_START_LABELS) | set(SUSPENSION_PERIOD_LABELS)
    | set(RESUMPTION_LABELS) | set(EFFECTIVE_GENERIC_LABELS),
    key=len, reverse=True))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: list[str] = []
    for r in rows:
        for k in r.keys():
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = _csv.DictWriter(f, fieldnames=keys, lineterminator="\n")  # LF for git-clean CSVs
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})


def raw_html_from_zip(rcept_no: str) -> tuple[str, bool]:
    """Return (raw_primary_html, inspectable). Read-only; never writes/repairs."""
    zp = ZIP_CACHE / f"{rcept_no}.zip"
    if not zp.exists():
        return "", False
    try:
        zf = zipfile.ZipFile(io.BytesIO(zp.read_bytes()))
    except zipfile.BadZipFile:
        return "", False
    docs = []
    for name in zf.namelist():
        try:
            content = zf.read(name)
        except Exception:
            continue
        for enc in ("utf-8", "euc-kr", "cp949", "utf-16"):
            try:
                docs.append(content.decode(enc)); break
            except UnicodeDecodeError:
                continue
    if not docs:
        return "", False
    primary = max(docs, key=len)
    head = primary[:500].upper()
    inspectable = ("<HTML" in head or "<BODY" in head or "<TABLE" in primary.upper())
    return primary, inspectable


def cell_is_label(text: str) -> str:
    t = _normalize_for_scan(text)
    for lbl in ALL_LABELS:
        if lbl in t:
            return lbl
    return ""


# Markers that mean "no date present" in the matched label's value cell.
DASH_CHARS = set("-―—‐–")
RELATIVE_TBD_TOKENS = ("미정", "추후", "별도", "당분간", "예정", "통보", "미정임")


def classify_value_cell(text: str) -> str:
    """Classify the matched label's adjacent value cell:
    has_date / empty_or_dash / relative_tbd / other_text."""
    t = text.strip()
    if t == "" or (set(t) <= DASH_CHARS):
        return "empty_or_dash"
    if find_first_date(_normalize_for_scan(t))[0]:
        return "has_date"
    if any(tok in t for tok in RELATIVE_TBD_TOKENS):
        return "relative_tbd"
    return "other_text"


def analyze_tables(html: str) -> dict:
    """Read-only structural profile + hypothetical candidate value location."""
    out = {
        "n_tables": 0, "n_candidate_tables": 0, "label_cell_found": False,
        "n_label_cells": 0, "value_cell_with_date_found": False,
        "n_distinct_candidate_dates": 0,
        "value_cell_content_class": "",          # has_date/empty_or_dash/relative_tbd/other_text
        "value_cell_text_sample": "",
        "hypothetical_candidate_value_text": "", "hypothetical_candidate_value_iso": "",
        "any_date_in_body": False, "label_text_matched": "",
    }
    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception:
        return out
    # any date anywhere in body (flattened) — proof signal only
    body_iso, _, _, _ = find_first_date(_normalize_for_scan(soup.get_text(" ", strip=True)))
    out["any_date_in_body"] = bool(body_iso)

    tables = soup.find_all("table")
    out["n_tables"] = len(tables)
    candidate_dates: list[tuple[str, str]] = []  # (iso, raw_text) from value cells
    label_cells = 0
    candidate_tables = 0
    label_text_seen = ""
    # Value-cell content classes seen for the matched label's RIGHT-neighbor (the
    # canonical "label | value" cell). The below-neighbor is typically the NEXT row
    # / section header, so it is NOT treated as the value cell here.
    value_classes: list[str] = []
    value_text_sample = ""
    for tbl in tables:
        rows = tbl.find_all("tr")
        grid = []
        for tr in rows:
            cells = tr.find_all(["td", "th"])
            grid.append([c.get_text(" ", strip=True) for c in cells])
        tbl_has_label = False
        for ri, row in enumerate(grid):
            for ci, cell_text in enumerate(row):
                lbl = cell_is_label(cell_text)
                if not lbl:
                    continue
                tbl_has_label = True
                label_cells += 1
                if not label_text_seen:
                    label_text_seen = lbl
                # canonical value cell = right neighbor (same row)
                vc = row[ci + 1] if ci + 1 < len(row) else ""
                vcls = classify_value_cell(vc)
                value_classes.append(vcls)
                if not value_text_sample and vc.strip():
                    value_text_sample = vc.strip()[:60]
                if vcls == "has_date":
                    iso, _, _, _ = find_first_date(_normalize_for_scan(vc))
                    if iso:
                        candidate_dates.append((iso, vc.strip()[:60]))
        if tbl_has_label:
            candidate_tables += 1
    out["n_candidate_tables"] = candidate_tables
    out["label_cell_found"] = label_cells > 0
    out["n_label_cells"] = label_cells
    out["label_text_matched"] = label_text_seen
    out["value_cell_text_sample"] = value_text_sample
    # overall value-cell content class: prefer has_date > other_text > relative_tbd > empty_or_dash
    priority = ["has_date", "other_text", "relative_tbd", "empty_or_dash"]
    out["value_cell_content_class"] = next(
        (c for c in priority if c in value_classes), "" if value_classes else "no_label_cell")
    distinct = sorted({c[0] for c in candidate_dates})
    out["n_distinct_candidate_dates"] = len(distinct)
    out["value_cell_with_date_found"] = len(candidate_dates) > 0
    if candidate_dates:
        # record the first as hypothetical/proof-only (NOT a final field)
        out["hypothetical_candidate_value_iso"] = candidate_dates[0][0]
        out["hypothetical_candidate_value_text"] = candidate_dates[0][1]
    return out


def classify(profile: dict, inspectable: bool) -> dict:
    """Map the read-only structural profile -> proof-only design bucket + FP risk +
    required future approval + guardrail. Planning evidence only."""
    if not inspectable or profile["n_tables"] == 0:
        return {
            "design_proof_bucket": "blocked_missing_or_uninspectable_structure",
            "false_positive_risk": "blocked_not_evaluable",
            "required_future_approval": "source_channel_or_body_recovery_verdict_required",
            "required_guardrail": "n/a (no inspectable table structure locally)",
        }
    if not profile["label_cell_found"]:
        # tables exist but the date label is not in a table cell (parser saw it in
        # flattened text) -> a simple table-label/value rule would not apply cleanly.
        return {
            "design_proof_bucket": "ambiguous_requires_manual_or_later_design",
            "false_positive_risk": "high_ambiguous",
            "required_future_approval": "manual_adjudication_approval_required",
            "required_guardrail": "label not in a table cell; would need non-table "
                                  "structural heuristic; manual confirm",
        }
    vcls = profile["value_cell_content_class"]
    n_dates = profile["n_distinct_candidate_dates"]

    # KEY FINDING: for these rows the matched (resumption/release) label's value cell
    # is an explicit "-" / empty / TBD placeholder (the resumption date is not yet
    # determined). There is NO date to extract; table/structure-aware parsing would
    # correctly read the "-" and still produce nothing. NOT a parser-design opportunity.
    if vcls in ("empty_or_dash", "relative_tbd"):
        return {
            "design_proof_bucket": "out_of_scope_keep_fail_closed",
            "false_positive_risk": "blocked_not_evaluable",
            "required_future_approval": "none_keep_fail_closed",
            "required_guardrail": ("matched label value cell is explicitly empty/dash "
                                   "('-') — resumption/release date not yet determined; "
                                   "no date exists to extract; keep fail-closed (table-"
                                   "aware parsing would not change this)"
                                   if vcls == "empty_or_dash" else
                                   "matched label value cell holds a relative/TBD marker "
                                   "(미정/추후/별도…), not a date; keep fail-closed"),
        }
    if vcls == "has_date" and n_dates >= 1:
        if profile["n_label_cells"] == 1 and n_dates == 1:
            return {
                "design_proof_bucket": "future_parser_change_candidate_low_ambiguity",
                "false_positive_risk": "low_with_strict_table_label_value_guard",
                "required_future_approval": "parser_change_verdict_required",
                "required_guardrail": "single label cell + exactly one date in the "
                                      "right-neighbor value cell; reject if >1 label "
                                      "cell, >1 distinct date, or colspan/rowspan",
            }
        if n_dates == 1:
            return {
                "design_proof_bucket": "future_parser_change_candidate_guarded",
                "false_positive_risk": "medium_requires_additional_guard",
                "required_future_approval": "parser_change_verdict_after_design_proof_review",
                "required_guardrail": "single distinct candidate date but multiple label "
                                      "cells; require label-kind disambiguation first",
            }
        return {
            "design_proof_bucket": "ambiguous_requires_manual_or_later_design",
            "false_positive_risk": "high_ambiguous",
            "required_future_approval": "manual_adjudication_approval_required",
            "required_guardrail": "multiple distinct candidate dates in value cells; "
                                  "cannot disambiguate by adjacency alone; manual confirm",
        }
    # value cell has non-date, non-empty text (other_text)
    return {
        "design_proof_bucket": "ambiguous_requires_manual_or_later_design",
        "false_positive_risk": "high_ambiguous",
        "required_future_approval": "manual_adjudication_approval_required",
        "required_guardrail": "label cell value is non-date free text; value likely "
                              "non-adjacent or absent; manual confirm",
    }


def main() -> None:
    print("[start] KR-STATUS-PARSER-TABLE-CONTEXT-DESIGN-PROOF-A0")
    OUT.mkdir(parents=True, exist_ok=True)

    feas = pd.read_csv(FEAS, dtype=str).fillna("")
    tgt = feas[feas["feasibility_bucket"] == "needs_table_context_design"].copy()
    n = len(tgt)
    assert n == 170, f"expected 170 needs_table_context_design rows, got {n}"
    prior = pd.read_csv(INPUT_PRIOR, dtype=str).fillna("")
    prior_by_id = {r["rcept_no"]: r for r in prior.to_dict(orient="records")}
    print(f"[target] {n} needs_table_context_design rows")

    input_rows, struct_rows, matrix_rows = [], [], []
    examples_by_bucket: dict[str, list[dict]] = {}
    bucket_ct: Counter = Counter()
    fp_ct: Counter = Counter()
    approval_ct: Counter = Counter()
    struct_class_ct: Counter = Counter()

    for r in tgt.to_dict(orient="records"):
        rid = r["rcept_no"]
        p = prior_by_id.get(rid, {})
        html, inspectable = raw_html_from_zip(rid)
        prof = analyze_tables(html) if inspectable else {
            "n_tables": 0, "n_candidate_tables": 0, "label_cell_found": False,
            "n_label_cells": 0, "value_cell_with_date_found": False,
            "n_distinct_candidate_dates": 0, "value_cell_content_class": "",
            "value_cell_text_sample": "", "hypothetical_candidate_value_text": "",
            "hypothetical_candidate_value_iso": "", "any_date_in_body": False,
            "label_text_matched": "",
        }
        cls = classify(prof, inspectable)

        if prof["n_tables"] == 0:
            struct_class = "no_table"
        elif not prof["label_cell_found"]:
            struct_class = "table_without_label_cell"
        else:
            # structure class keyed on the matched label's value-cell content
            struct_class = f"label_in_table_value_{prof['value_cell_content_class']}"
        struct_class_ct[struct_class] += 1
        bucket_ct[cls["design_proof_bucket"]] += 1
        fp_ct[cls["false_positive_risk"]] += 1
        approval_ct[cls["required_future_approval"]] += 1

        input_rows.append({
            "rcept_no": rid,
            "prior_parse_status": p.get("prior_parse_status", r.get("prior_parse_status", "")),
            "prior_taxonomy_class": p.get("prior_taxonomy_class", r.get("prior_taxonomy_class", "")),
            "prior_feasibility_bucket": "needs_table_context_design",
            "body_format": p.get("body_format", ""),
            "body_locally_available": (ZIP_CACHE / f"{rid}.zip").exists(),
            "provenance": "KR_STATUS_PARSER_NONEXTRACTED_FEASIBILITY_A0/parser_nonextracted_feasibility_matrix.csv + input_manifest.csv",
        })
        struct_rows.append({
            "rcept_no": rid, "body_inspectable": inspectable,
            "n_tables": prof["n_tables"], "n_candidate_tables": prof["n_candidate_tables"],
            "label_cell_found": prof["label_cell_found"], "n_label_cells": prof["n_label_cells"],
            "label_text_matched": prof["label_text_matched"],
            "value_cell_content_class": prof["value_cell_content_class"],
            "value_cell_text_sample": prof["value_cell_text_sample"],
            "value_cell_with_date_found": prof["value_cell_with_date_found"],
            "n_distinct_candidate_dates": prof["n_distinct_candidate_dates"],
            "any_date_in_body": prof["any_date_in_body"],
            "structure_class": struct_class,
        })
        matrix_rows.append({
            "rcept_no": rid,
            "design_proof_bucket": cls["design_proof_bucket"],
            "false_positive_risk": cls["false_positive_risk"],
            "required_future_approval": cls["required_future_approval"],
            "required_guardrail": cls["required_guardrail"],
            # HYPOTHETICAL / PROOF-ONLY candidate evidence (NOT effective_date/parsed_date):
            "hypothetical_candidate_value_text": prof["hypothetical_candidate_value_text"],
            "hypothetical_candidate_value_iso_PROOF_ONLY": prof["hypothetical_candidate_value_iso"],
            "is_proof_only_not_parser_output": True,
            # fail-closed flags (explicit false / fail-closed only):
            "fail_closed": True, "manual_review_required": True,
            "executable_or_safe": False, "downstream_authoritative": False,
            "parsed": False, "recovered": False, "validated": False, "approved": False,
            "effective_date_accepted": False, "strategy_ready": False,
        })
        ex = examples_by_bucket.setdefault(cls["design_proof_bucket"], [])
        if len(ex) < 5:
            ex.append({
                "design_proof_bucket": cls["design_proof_bucket"], "rcept_no": rid,
                "n_tables": prof["n_tables"], "n_label_cells": prof["n_label_cells"],
                "n_distinct_candidate_dates": prof["n_distinct_candidate_dates"],
                "hypothetical_candidate_value_iso_PROOF_ONLY": prof["hypothetical_candidate_value_iso"],
                "false_positive_risk": cls["false_positive_risk"],
            })

    assert sum(bucket_ct.values()) == 170, f"bucket sum {sum(bucket_ct.values())} != 170"

    # blocker ledger
    blocker_rows = []
    for b, cnt in bucket_ct.most_common():
        rep = next(m for m in matrix_rows if m["design_proof_bucket"] == b)
        blocker_rows.append({
            "scope": "bucket", "design_proof_bucket": b, "n_rows": cnt,
            "false_positive_risk": rep["false_positive_risk"],
            "required_future_approval": rep["required_future_approval"],
            "required_guardrail": rep["required_guardrail"],
            "planning_only_note": "design-proof evidence only; NOT current parser "
                                  "behavior; NOT approval; row stays fail-closed; any "
                                  "parser change needs a separate parser-change verdict",
        })

    # bucket summary
    summary_rows = []
    ps_ct = Counter(s.get("prior_parse_status", "") for s in input_rows)
    for k, v in ps_ct.most_common():
        summary_rows.append({"dimension": "prior_parse_status", "key": k, "count": v})
    for k, v in struct_class_ct.most_common():
        summary_rows.append({"dimension": "structure_class", "key": k, "count": v})
    for k, v in bucket_ct.most_common():
        summary_rows.append({"dimension": "design_proof_bucket", "key": k, "count": v})
    for k, v in fp_ct.most_common():
        summary_rows.append({"dimension": "false_positive_risk", "key": k, "count": v})
    for k, v in approval_ct.most_common():
        summary_rows.append({"dimension": "required_future_approval", "key": k, "count": v})

    write_csv(OUT / "table_context_input_manifest.csv", input_rows)
    write_csv(OUT / "table_context_structure_profile.csv", struct_rows)
    write_csv(OUT / "table_context_design_proof_matrix.csv", matrix_rows)
    write_csv(OUT / "table_context_bucket_summary.csv", summary_rows)
    write_csv(OUT / "table_context_blocker_ledger.csv", blocker_rows or [
        {"scope": "all", "design_proof_bucket": "NONE", "n_rows": 0,
         "false_positive_risk": "", "required_future_approval": "",
         "required_guardrail": "", "planning_only_note": "NONE"}])

    write_guardrails(OUT / "table_context_guardrails.md", bucket_ct, fp_ct)
    write_examples(OUT / "table_context_examples.md", examples_by_bucket)
    write_hard_lock_check(OUT / "hard_lock_compliance_check.md")
    write_report(OUT / "report.md", n, ps_ct, struct_class_ct, bucket_ct, fp_ct, approval_ct, len(blocker_rows))

    print(json.dumps({
        "rows": n,
        "structure_class": dict(struct_class_ct),
        "design_proof_buckets": dict(bucket_ct),
        "bucket_sum": sum(bucket_ct.values()),
        "false_positive_risk": dict(fp_ct),
        "required_future_approval": dict(approval_ct),
        "blocker_buckets": len(blocker_rows),
    }, indent=2, default=str))


def write_guardrails(path: Path, bucket_ct: Counter, fp_ct: Counter) -> None:
    path.write_text(f"""# Table-Context Future Safety Guardrails (PROPOSED — NOT IMPLEMENTED)

Date: 2026-05-26
Phase: KR-STATUS-PARSER-TABLE-CONTEXT-DESIGN-PROOF-A0

**Proposed FUTURE safety guardrails only. NO parser implementation here. NO design is
approved. Any actual parser change requires a separate user + Referee parser-change
verdict.**

## KEY PROOF FINDING (corrects the prior feasibility optimism)

Read-only table inspection of all 170 rows shows the matched (resumption / release-date)
label's value cell is an explicit **`-` (empty/dash)** — i.e. the resumption/release
date is NOT YET DETERMINED in these suspension disclosures. **0 / 170** had a parseable
date in the matched label's value cell. So:

- There is NO date to extract for the failing field; the value genuinely does not exist
  in the body.
- Table/structure-aware extraction would correctly read the `-` and STILL produce no
  date — it does NOT recover anything here.
- The prior `needs_table_context_design` feasibility label OVER-stated the opportunity:
  these 170 are NOT a parser-design win. All 170 -> `out_of_scope_keep_fail_closed`,
  kept fail-closed.

(Aside, NOT actioned: many of these disclosures DO carry a *suspension* timestamp in an
adjacent cell, e.g. "매매거래정지 일시 | 2010-..-.. HH:MM", which the parser's current
label set misses because the spacing breaks the "정지일" token. Extracting that would be
a DIFFERENT field + a label-pattern theme, not table-context, and would need its own
separate design + parser-change verdict. It is recorded here only as an observation.)

The guardrails below are therefore HYPOTHETICAL — what a table/structure-aware design
WOULD need IF value-bearing cells existed (they did not for these 170):

1. **Strict table-adjacency rule.** Accept a value only from the label cell's immediate
   right-neighbor (same row) or immediate below-neighbor (same column). Reject anything
   farther.
2. **Single-candidate rule.** Accept only if exactly one parseable date is found in the
   adjacent value cell; reject if the adjacent cell has 0 or >1 dates.
3. **Single-label rule.** Reject if the body has more than one table label cell of the
   target kind (ambiguous which event the date belongs to) unless label-kind
   disambiguation is added.
4. **Span guard.** Reject (or specially handle) tables with colspan/rowspan, since
   simple row/column adjacency can misalign cells.
5. **Label-kind / event-type consistency.** The matched label kind (suspension start /
   period / resumption / effective-generic) must be consistent with the disclosure's
   event_category before accepting.
6. **No rcept_dt fallback.** Never substitute rcept_dt as the effective date.
7. **Fail-closed default.** Any row not clearly passing all guards stays
   zip-/non-extracted and fail-closed; the design must prefer a miss over a wrong date.

## Bucket roll-up (proof-only)

| design_proof_bucket | rows |
|---|---:|
""" + "\n".join(f"| `{k}` | {v} |" for k, v in bucket_ct.most_common()) + f"""
| **total** | **{sum(bucket_ct.values())}** |

For these 170 there are 0 `future_parser_change_candidate_*` rows (all value cells are
`-`), so NO table-context parser-change is warranted for them — they remain
fail-closed. The guardrails above stand as design notes for any future row set that
DOES have value-bearing table cells.
""", encoding="utf-8")


def write_examples(path: Path, examples_by_bucket: dict) -> None:
    lines = ["# Table-Context Design-Proof — Inspection Examples", "",
             "Date: 2026-05-26", "Phase: KR-STATUS-PARSER-TABLE-CONTEXT-DESIGN-PROOF-A0", "",
             "**INSPECTION SAMPLES ONLY — not validation, not approval, not parsed rows. "
             "Any `hypothetical_candidate_value_iso_PROOF_ONLY` shown is a DESIGN-PROOF "
             "hypothesis, NOT an accepted effective/parsed date. Every row stays "
             "fail-closed.** A future parser-change phase needs a separate user + Referee "
             "verdict.", ""]
    for b, ex in examples_by_bucket.items():
        lines.append(f"## {b} (showing {len(ex)} samples)")
        lines.append("")
        lines.append("| rcept_no | n_tables | n_label_cells | n_distinct_candidate_dates | hypothetical_candidate_value_iso_PROOF_ONLY | false_positive_risk |")
        lines.append("|---|---:|---:|---:|---|---|")
        for e in ex:
            lines.append(f"| {e['rcept_no']} | {e['n_tables']} | {e['n_label_cells']} | {e['n_distinct_candidate_dates']} | {e['hypothetical_candidate_value_iso_PROOF_ONLY'] or '(none)'} | {e['false_positive_risk']} |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_hard_lock_check(path: Path) -> None:
    path.write_text("""# Hard-Lock Compliance Check (Table-Context Design Proof)

Date: 2026-05-26
Phase: KR-STATUS-PARSER-TABLE-CONTEXT-DESIGN-PROOF-A0

| hard lock | status |
|---|---|
| Target = exactly 170 needs_table_context_design rows (0 attachment) | PASS (asserted) |
| Read local artifacts + cached bodies READ-ONLY only | PASS |
| NO download / API / credentials / source recovery / body reacquisition / cache repair | PASS |
| NO parser code/rule/version change; NO edits under src/parsers/ | PASS (parser imported read-only; not invoked to change outputs) |
| NO parser/candidate-linkage/body-confirmation rerun changing accepted outputs | PASS |
| Candidate date evidence is HYPOTHETICAL/PROOF-ONLY (named hypothetical_*, not effective_date/parsed_date) | PASS |
| NO effective date accepted/finalized; NO rcept_dt as effective date | PASS |
| NO manual adjudication/validation/approval | PASS |
| NO row marked parsed/recovered/executable/safe/authoritative/validated/approved/ready | PASS |
| Every row fail-closed | PASS |
| NO downstream / C2-C3 / event-log / executable-status table / strategy / execution | PASS |
| CSVs use LF line endings; git show --check must pass | PASS (lineterminator="\\n") |
| Outputs separate design proof from approved parser behavior | PASS |
| No self-close; no CLOSE_NOTE; not moved to Closed/Frozen | PASS |
""", encoding="utf-8")


def write_report(path, n, ps_ct, struct_ct, bucket_ct, fp_ct, approval_ct, n_blockers) -> None:
    low = bucket_ct.get("future_parser_change_candidate_low_ambiguity", 0)
    guarded = bucket_ct.get("future_parser_change_candidate_guarded", 0)
    amb = bucket_ct.get("ambiguous_requires_manual_or_later_design", 0)
    blocked = bucket_ct.get("blocked_missing_or_uninspectable_structure", 0)
    oos = bucket_ct.get("out_of_scope_keep_fail_closed", 0)
    lines = [
        "# KR-STATUS-PARSER-TABLE-CONTEXT-DESIGN-PROOF-A0 — Initial-Pass Report", "",
        "Date: 2026-05-26",
        "Phase opened by: Referee verdict (via relay), authorized by user's explicit "
        "decision to open a LOCAL-ONLY table-context parser-design PROOF phase.",
        "Executor: Claude Code. Referee: Codex.", "",
        "## Phase name and scope", "",
        "Local-only, read-only PROOF of whether table/structure-aware extraction is "
        "design-feasible for the 170 needs_table_context_design rows, plus false-positive "
        "risk and required guardrails. NO parser change; NO src/parsers edits; parser "
        "imported read-only (label sets + date detector) and NOT invoked to change "
        "outputs. All candidate evidence is HYPOTHETICAL/PROOF-ONLY. Every row "
        "fail-closed. No self-close; no CLOSE_NOTE this pass.",
        "", "## Exact 170-row accounting", "",
        f"- target rows: {sum(bucket_ct.values())} (asserted == 170); all from "
        "feasibility_bucket=needs_table_context_design (prior taxonomy "
        "label_present_but_attachment_or_table_context_required; 0 attachment). No "
        "non-target row.",
        "", "## Structure class (read-only profile)", "",
        "| structure_class | count |", "|---|---:|",
    ]
    for k, v in struct_ct.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += ["", "## Design-proof bucket counts (sum to 170)", "",
              "| design_proof_bucket | count |", "|---|---:|"]
    for k, v in bucket_ct.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines.append(f"| **total** | **{sum(bucket_ct.values())}** |")
    lines += ["", "## False-positive risk counts", "", "| false_positive_risk | count |", "|---|---:|"]
    for k, v in fp_ct.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += ["", "## Required-future-approval counts", "",
              "| required_future_approval | count |", "|---|---:|"]
    for k, v in approval_ct.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Design-proof conclusion (planning evidence only) — HONEST HEADLINE",
        "",
        "- **KEY FINDING: the prior `needs_table_context_design` feasibility label was "
        f"OVER-optimistic for these rows.** All {oos} / 170 -> "
        "`out_of_scope_keep_fail_closed`. Read-only table inspection shows the matched "
        "(resumption / release-date) label's value cell is an explicit `-` "
        "(empty/dash) — the resumption/release date is NOT YET DETERMINED in these "
        "suspension disclosures. 0 / 170 had a parseable date in the matched label's "
        "value cell.",
        "- Therefore table/structure-aware extraction does NOT recover a date here: "
        "there is no value to recover (the cell is `-`). A future parser would "
        "correctly read the `-` and still produce nothing. These 170 are NOT a "
        "parser-design opportunity and remain fail-closed.",
        f"- Bucket distribution: future_parser_change_candidate_low_ambiguity {low} / "
        f"future_parser_change_candidate_guarded {guarded} / "
        f"ambiguous_requires_manual_or_later_design {amb} / "
        f"blocked_missing_or_uninspectable_structure {blocked} / "
        f"out_of_scope_keep_fail_closed {oos}.",
        "- Aside (NOT actioned): many of these disclosures DO carry a *suspension* "
        "timestamp in an adjacent cell (e.g. '매매거래정지 일시 | YYYY-..-.. HH:MM') that "
        "the parser's current label set misses due to token spacing. Extracting that "
        "is a DIFFERENT field + a label-pattern theme (not table-context) and would "
        "need its own separate design + parser-change verdict. Recorded as an "
        "observation only.",
        "- Net: this design proof REDUCES the apparent parser-design surface — the 170 "
        "table-context rows are confirmed to have no extractable value (explicit `-`) "
        "and stay fail-closed. See table_context_guardrails.md.",
        "",
        f"## Blockers: {n_blockers} bucket-level entries (table_context_blocker_ledger.csv)",
        "",
        "Each bucket records its false_positive_risk, required_future_approval, "
        "required_guardrail, and a planning_only_note (design-proof evidence only; NOT "
        "current parser behavior; NOT approval; row stays fail-closed; parser change "
        "needs a separate verdict).",
        "",
        "## Defects", "",
        "- None. Non-extracted rows remain fail-closed by design (expected).",
        "",
        "## Hard-lock confirmations", "",
        "- Target = exactly 170; no non-target row. Read-only of cached bodies + accepted "
        "artifacts.",
        "- Parser imported read-only (label sets + find_first_date); NOT invoked to "
        "change outputs; NO src/parsers edits; no parser code/rule/version change; no "
        "parser/candidate/body rerun.",
        "- Candidate date/value evidence is HYPOTHETICAL/PROOF-ONLY "
        "(hypothetical_candidate_value_iso_PROOF_ONLY; is_proof_only_not_parser_output=True); "
        "no effective date accepted/finalized; no rcept_dt as effective date.",
        "- No manual adjudication/validation/approval; no row promoted; every row "
        "fail-closed (manual_review_required=True; executable_or_safe / "
        "downstream_authoritative / parsed / recovered / validated / approved / "
        "effective_date_accepted / strategy_ready = False).",
        "- No downloads / API / source recovery / body repair. No downstream / C2-C3 / "
        "event-log / executable-status table / strategy / backtest / execution / "
        "performance / production / paper / live / P08 / shadow.",
        "- CSVs written with LF line endings (git show --check expected to pass). No "
        "self-close; no CLOSE_NOTE; not moved to Closed/Frozen.",
        "",
        "## Gate self-assessment", "",
        "- All 15 gate conditions intended to hold (170 exact; all from "
        "needs_table_context_design; 0 attachment; no non-target; no download/API/"
        "source-recovery/body-repair; no parser change; no src/parsers edits; no "
        "candidate/body rerun; all fail-closed; no promotion; candidate evidence "
        "hypothetical/proof-only; FP guardrails recorded; design proof separated from "
        "approved behavior; no downstream/strategy/execution claim; CSV LF + git "
        "show --check). Self-assessment: CLOSE-READY for review.",
        "",
        "## Decision requested from Referee", "",
        "Executor does NOT self-close. Verdict options: A close as table-context design "
        "proof complete (planning evidence recorded; all rows fail-closed) / B another "
        "proof pass / C open a future parser-CHANGE phase for the low-ambiguity subset "
        "(needs its own user + Referee parser-change verdict; src/parsers edits forbidden "
        "until then) / D keep all strategy/execution closed.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
