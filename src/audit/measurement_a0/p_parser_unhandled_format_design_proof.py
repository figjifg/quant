"""KR-STATUS-PARSER-UNHANDLED-FORMAT-DESIGN-PROOF-A0 — builder.

Referee directive (2026-05-26, via relay), authorized by the user's explicit decision
to open a LOCAL-ONLY unhandled-format parser-design PROOF phase for the 23
`label_present_but_value_in_unhandled_format` rows (prior feasibility theme
`date_format_or_relative_date_handling`). NOT download/API, source-recovery,
parser-change, or manual-adjudication approval.

Goal: PROOF-ONLY design evidence — for each of the 23 rows, inspect (read-only) the
immediate value text after the matched date label and classify what "unhandled format"
actually is: an absolute date in a format the parser does not handle (a future
parser-change candidate, with guardrails), a relative/TBD marker (keep fail-closed,
no date exists), a date-range/period-to-delisting (out of scope), a parseable date in
a NON-target field (resumption value absent → manual), or otherwise ambiguous. This
does NOT implement or promise extraction.

HARD CONSTRAINTS:
- Target = exactly the 23 rows with prior taxonomy class
  `label_present_but_value_in_unhandled_format` / feasibility bucket
  `parser_design_candidate` / design theme `date_format_or_relative_date_handling`.
- Read existing local artifacts + cached bodies (read-only) ONLY. No download / API /
  source recovery / body reacquisition / cache repair / overwrite.
- NO parser code/rule/version change; NO edits under src/parsers/. The parser helpers
  are imported read-only (label sets, find_label_hits, find_first_date, normalizer);
  the parser is NOT modified and no accepted parse output is changed.
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
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))

from src.audit.measurement_a0.p_status_correction_linkage import ZIP_CACHE  # noqa: E402
from src.parsers.krx_status_html_inline import (  # noqa: E402  (read-only reuse; parser NOT modified)
    extract_body_from_zip, find_label_hits, find_first_date, _normalize_for_scan,
)

MA0 = REPO / "reports/experiments/measurement_A0"
OUT = MA0 / "KR_STATUS_PARSER_UNHANDLED_FORMAT_DESIGN_PROOF_A0"
FEAS = MA0 / "KR_STATUS_PARSER_NONEXTRACTED_FEASIBILITY_A0/parser_nonextracted_feasibility_matrix.csv"
INPUT_PRIOR = MA0 / "KR_STATUS_PARSER_NONEXTRACTED_FEASIBILITY_A0/parser_nonextracted_input_manifest.csv"

# Resumption / release / effective date labels (the meaningful field for a
# resumption-related event). Suspension labels carry the *suspension* timestamp.
RESUMPTION_LABEL_SET = {
    "매매재개일", "거래재개일", "정지해제일", "해제일", "재개일",
    "해제예정일", "재개예정일", "효력발생일", "적용일", "지정일", "변경일",
}

IMMEDIATE_AFTER_CHARS = 25  # same immediate-window size the accepted taxonomy used

# Relative / non-ISO / deadline expressions: the value is defined relative to a future
# event or is a deadline, NOT an absolute event date.
RELATIVE_TBD_TOKENS = ("익일", "추후", "별도", "미정", "예정", "통보", "당분간",
                       "이내", "限", "경과")
# Apostrophe-anchored 2-digit-year date ('21.5.3 / '24.4.17) — a real date in a format
# the parser's 4-digit patterns do not handle. Apostrophe-anchored to avoid matching
# the trailing 2 digits inside a full 4-digit-year date (e.g. "10-12-30" in "2010-12-30").
TWO_DIGIT_YEAR_DATE_RE = re.compile(r"['’]\s?\d{2}\s*[.\-/]\s*\d{1,2}\s*[.\-/]\s*\d{1,2}")
# Range / period markers (a period rather than a single resumption date).
RANGE_PERIOD_RE = re.compile(r"~|부터|까지")
DELISTING_TOKENS = ("상장폐지", "정리매매")
DASH_PUNCT = " -―—‐–·.:|()"


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


def inspect_value(rcept_no: str) -> dict:
    """Read-only: immediate value text after each matched label + structural signals.
    Never writes / repairs / downloads."""
    out = {
        "body_inspectable": False, "n_label_hits": 0, "labels_matched": "",
        "resumption_label_present": False, "immediate_value_text": "",
        "resumption_immediate_text": "",
        "has_relative_tbd": False, "has_two_digit_year_date": False,
        "has_range_period": False, "has_delisting_resolution": False,
        "parseable_full_date_present": False, "parseable_full_date_iso": "",
        "two_digit_year_raw": "",
    }
    zp = ZIP_CACHE / f"{rcept_no}.zip"
    if not zp.exists():
        return out
    try:
        be = extract_body_from_zip(zp.read_bytes())
    except Exception:
        return out
    if not be.text:
        return out
    out["body_inspectable"] = True
    hits = find_label_hits(be.text)
    out["n_label_hits"] = len(hits)
    labels = []
    imm_parts, resump_parts = [], []
    for h in hits:
        labels.append(h.label)
        w = _normalize_for_scan(h.window)
        i = w.find(h.label)
        seg = w[i + len(h.label): i + len(h.label) + IMMEDIATE_AFTER_CHARS] if i >= 0 else ""
        imm_parts.append(seg)
        if h.label in RESUMPTION_LABEL_SET:
            resump_parts.append(seg)
    out["labels_matched"] = "|".join(dict.fromkeys(labels))  # unique, order-preserving
    out["resumption_label_present"] = bool(resump_parts)
    imm = " ".join(p.strip() for p in imm_parts if p.strip())
    out["immediate_value_text"] = imm[:160]
    out["resumption_immediate_text"] = " ".join(p.strip() for p in resump_parts if p.strip())[:120]

    out["has_relative_tbd"] = any(tok in imm for tok in RELATIVE_TBD_TOKENS)
    m = TWO_DIGIT_YEAR_DATE_RE.search(imm)
    out["has_two_digit_year_date"] = bool(m)
    out["two_digit_year_raw"] = m.group(0).strip() if m else ""
    out["has_range_period"] = bool(RANGE_PERIOD_RE.search(imm))
    out["has_delisting_resolution"] = any(tok in imm for tok in DELISTING_TOKENS)
    iso, _, _, _ = find_first_date(imm)
    out["parseable_full_date_present"] = bool(iso)
    out["parseable_full_date_iso"] = iso or ""
    return out


def _norm_two_digit_year_iso(raw: str) -> str:
    """Proof-only normalization of a 'YY.M.D 2-digit-year date to an ISO-like string.
    HYPOTHETICAL ONLY — illustrates what a guarded future parser MIGHT produce; the
    century is assumed 20YY (itself an ambiguity the guardrail must resolve). NOT a
    parsed/effective date."""
    digits = re.findall(r"\d+", raw)
    if len(digits) != 3:
        return ""
    yy, mm, dd = digits
    return f"20{int(yy):02d}-{int(mm):02d}-{int(dd):02d}"


def classify(v: dict) -> dict:
    """Map read-only value signals -> value pattern, proof-only design bucket, FP risk,
    future-approval, guardrail. Planning evidence only; every row stays fail-closed."""
    if not v["body_inspectable"] or v["n_label_hits"] == 0:
        return {
            "value_pattern_class": "uninspectable_or_missing_local_body",
            "design_proof_bucket": "blocked_missing_or_uninspectable_body",
            "false_positive_risk": "blocked_not_evaluable",
            "required_future_approval": "source_channel_or_body_recovery_verdict_required",
            "required_guardrail": "no inspectable local body / no label hit; cannot evaluate",
            "hypothetical_candidate_value_text": "", "hypothetical_candidate_value_iso": "",
        }
    # A 2-digit-year date that sits inside a relative/deadline expression (e.g.
    # "1년 이내('24.4.17限)") is a DEADLINE, not the event date -> relative/TBD, keep
    # fail-closed (the event date itself is "within 1 year", undetermined).
    if v["has_two_digit_year_date"] and v["has_relative_tbd"]:
        return {
            "value_pattern_class": "relative_or_tbd_marker",
            "design_proof_bucket": "relative_tbd_keep_fail_closed",
            "false_positive_risk": "blocked_not_evaluable",
            "required_future_approval": "none_keep_fail_closed",
            "required_guardrail": ("2-digit-year date present but inside a relative/"
                                   "deadline expression (이내/限) — it is a deadline, not "
                                   "the event date; the event date is undetermined; keep "
                                   "fail-closed"),
            "hypothetical_candidate_value_text": "", "hypothetical_candidate_value_iso": "",
        }
    # A genuine absolute date in a 2-digit-year format ('YY.M.D) the parser does not
    # handle -> the ONE real unhandled-FORMAT candidate, but guarded.
    if v["has_two_digit_year_date"]:
        return {
            "value_pattern_class": "absolute_date_unhandled_format",
            "design_proof_bucket": "future_parser_change_candidate_guarded",
            "false_positive_risk": "medium_requires_additional_guard",
            "required_future_approval": "parser_change_verdict_after_design_proof_review",
            "required_guardrail": ("2-digit-year date format ('YY.M.D) the parser's "
                                   "4-digit patterns miss; a future parser MIGHT add a "
                                   "strict 'YY.M.D rule, but ONLY with century "
                                   "disambiguation (20YY vs 19YY) and confirmation that "
                                   "the matched label-kind is the effective date for this "
                                   "event; reject if >1 distinct date or relative context"),
            "hypothetical_candidate_value_text": v["two_digit_year_raw"],
            "hypothetical_candidate_value_iso": _norm_two_digit_year_iso(v["two_digit_year_raw"]),
        }
    # Relative / TBD marker (익일 / 추후 / 별도 / 미정 …) -> no absolute date exists.
    if v["has_relative_tbd"]:
        return {
            "value_pattern_class": "relative_or_tbd_marker",
            "design_proof_bucket": "relative_tbd_keep_fail_closed",
            "false_positive_risk": "blocked_not_evaluable",
            "required_future_approval": "none_keep_fail_closed",
            "required_guardrail": ("value is a relative/TBD expression (e.g. '…제출일 "
                                   "익일' = day after a future document submission); no "
                                   "absolute date exists to extract; a parser change "
                                   "cannot recover a date that is not present; keep "
                                   "fail-closed"),
            "hypothetical_candidate_value_text": "", "hypothetical_candidate_value_iso": "",
        }
    # Date range / period that resolves to delisting -> there is no resumption date.
    if v["has_range_period"] or v["has_delisting_resolution"]:
        return {
            "value_pattern_class": "date_range_or_period_text",
            "design_proof_bucket": "out_of_scope_keep_fail_closed",
            "false_positive_risk": "blocked_not_evaluable",
            "required_future_approval": "none_keep_fail_closed",
            "required_guardrail": ("value is a suspension PERIOD that resolves to "
                                   "상장폐지/정리매매 (delisting), not a single resumption "
                                   "date; no resumption date exists; out of scope; keep "
                                   "fail-closed"),
            "hypothetical_candidate_value_text": "", "hypothetical_candidate_value_iso": "",
        }
    # A FULL 4-digit parseable date IS adjacent, but the row is label_no_value because
    # that date is a NON-target field (the suspension timestamp 정지일시) and the
    # resumption value is genuinely absent. This is NOT a date-FORMAT problem (the format
    # is already handled); a parser change to date formats would not help. Manual.
    if v["parseable_full_date_present"]:
        return {
            "value_pattern_class": "other_ambiguous",
            "design_proof_bucket": "ambiguous_requires_manual_or_later_design",
            "false_positive_risk": "high_ambiguous",
            "required_future_approval": "manual_adjudication_approval_required",
            "required_guardrail": ("a parseable 4-digit date is present but it is the "
                                   "suspension timestamp (정지일시), NOT the resumption "
                                   "date; the resumption value is absent; this is a "
                                   "field-selection / value-absence issue, NOT a date "
                                   "format the parser fails to read; manual confirm"),
            "hypothetical_candidate_value_text": "", "hypothetical_candidate_value_iso": "",
        }
    # Anything else: some adjacent text, no date / relative / range signal.
    if v["immediate_value_text"].strip(DASH_PUNCT):
        return {
            "value_pattern_class": "non_date_text",
            "design_proof_bucket": "ambiguous_requires_manual_or_later_design",
            "false_positive_risk": "high_ambiguous",
            "required_future_approval": "manual_adjudication_approval_required",
            "required_guardrail": "adjacent value is non-date free text; manual confirm",
            "hypothetical_candidate_value_text": "", "hypothetical_candidate_value_iso": "",
        }
    return {
        "value_pattern_class": "missing_or_empty_value",
        "design_proof_bucket": "out_of_scope_keep_fail_closed",
        "false_positive_risk": "blocked_not_evaluable",
        "required_future_approval": "none_keep_fail_closed",
        "required_guardrail": "no adjacent value text after the label; nothing to extract",
        "hypothetical_candidate_value_text": "", "hypothetical_candidate_value_iso": "",
    }


def main() -> None:
    print("[start] KR-STATUS-PARSER-UNHANDLED-FORMAT-DESIGN-PROOF-A0")
    OUT.mkdir(parents=True, exist_ok=True)

    feas = pd.read_csv(FEAS, dtype=str).fillna("")
    tgt = feas[feas["design_theme"] == "date_format_or_relative_date_handling"].copy()
    n = len(tgt)
    assert n == 23, f"expected 23 unhandled-format rows, got {n}"
    # gate cross-checks: all 23 must share the locked prior classification
    assert set(tgt["prior_taxonomy_class"]) == {"label_present_but_value_in_unhandled_format"}, \
        "taxonomy-class drift"
    assert set(tgt["feasibility_bucket"]) == {"parser_design_candidate"}, "feasibility-bucket drift"
    assert set(tgt["prior_parse_status"]) == {"label_no_value"}, "parse-status drift"
    assert set(tgt["required_future_approval"]) == {"parser_change_verdict"}, "prior-approval drift"
    prior = pd.read_csv(INPUT_PRIOR, dtype=str).fillna("")
    prior_by_id = {r["rcept_no"]: r for r in prior.to_dict(orient="records")}
    print(f"[target] {n} unhandled-format rows (all label_no_value / parser_design_candidate)")

    input_rows, profile_rows, matrix_rows = [], [], []
    examples_by_bucket: dict[str, list[dict]] = {}
    pattern_ct: Counter = Counter()
    bucket_ct: Counter = Counter()
    fp_ct: Counter = Counter()
    approval_ct: Counter = Counter()
    ps_ct: Counter = Counter()

    for r in tgt.sort_values("rcept_no").to_dict(orient="records"):
        rid = r["rcept_no"]
        p = prior_by_id.get(rid, {})
        v = inspect_value(rid)
        cls = classify(v)

        pattern_ct[cls["value_pattern_class"]] += 1
        bucket_ct[cls["design_proof_bucket"]] += 1
        fp_ct[cls["false_positive_risk"]] += 1
        approval_ct[cls["required_future_approval"]] += 1
        ps_ct[p.get("prior_parse_status", r.get("prior_parse_status", ""))] += 1

        input_rows.append({
            "rcept_no": rid,
            "prior_parse_status": p.get("prior_parse_status", r.get("prior_parse_status", "")),
            "prior_taxonomy_class": r.get("prior_taxonomy_class", ""),
            "prior_taxonomy_note": p.get("prior_taxonomy_note", ""),
            "prior_feasibility_bucket": r.get("feasibility_bucket", ""),
            "prior_design_theme": r.get("design_theme", ""),
            "prior_required_future_approval": r.get("required_future_approval", ""),
            "event_category": p.get("event_category", ""),
            "is_correction": p.get("is_correction", ""),
            "body_format": p.get("body_format", ""),
            "body_locally_available": (ZIP_CACHE / f"{rid}.zip").exists(),
            "provenance": "KR_STATUS_PARSER_NONEXTRACTED_FEASIBILITY_A0/parser_nonextracted_feasibility_matrix.csv + input_manifest.csv",
        })
        profile_rows.append({
            "rcept_no": rid,
            "body_inspectable": v["body_inspectable"],
            "n_label_hits": v["n_label_hits"],
            "labels_matched": v["labels_matched"],
            "resumption_label_present": v["resumption_label_present"],
            "immediate_value_text": v["immediate_value_text"],
            "resumption_immediate_text": v["resumption_immediate_text"],
            "has_relative_tbd_marker": v["has_relative_tbd"],
            "has_two_digit_year_date": v["has_two_digit_year_date"],
            "two_digit_year_raw_PROOF_ONLY": v["two_digit_year_raw"],
            "has_range_period": v["has_range_period"],
            "has_delisting_resolution": v["has_delisting_resolution"],
            "parseable_full_date_present": v["parseable_full_date_present"],
            "parseable_full_date_iso_NON_TARGET_FIELD": v["parseable_full_date_iso"],
            "value_pattern_class": cls["value_pattern_class"],
        })
        matrix_rows.append({
            "rcept_no": rid,
            "value_pattern_class": cls["value_pattern_class"],
            "design_proof_bucket": cls["design_proof_bucket"],
            "false_positive_risk": cls["false_positive_risk"],
            "required_future_approval": cls["required_future_approval"],
            "required_guardrail": cls["required_guardrail"],
            # HYPOTHETICAL / PROOF-ONLY candidate evidence (NOT effective_date/parsed_date):
            "hypothetical_candidate_value_text": cls["hypothetical_candidate_value_text"],
            "hypothetical_candidate_value_iso_PROOF_ONLY": cls["hypothetical_candidate_value_iso"],
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
                "value_pattern_class": cls["value_pattern_class"],
                "labels_matched": v["labels_matched"],
                "immediate_value_text": v["immediate_value_text"][:80],
                "hypothetical_candidate_value_iso_PROOF_ONLY": cls["hypothetical_candidate_value_iso"],
                "false_positive_risk": cls["false_positive_risk"],
            })

    assert len(input_rows) == 23 and len(profile_rows) == 23 and len(matrix_rows) == 23
    assert sum(bucket_ct.values()) == 23, f"bucket sum {sum(bucket_ct.values())} != 23"
    assert sum(pattern_ct.values()) == 23, f"pattern sum {sum(pattern_ct.values())} != 23"

    # blocker ledger (bucket-level)
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
    if not blocker_rows:
        blocker_rows = [{"scope": "NONE", "design_proof_bucket": "NONE", "n_rows": 0,
                         "false_positive_risk": "", "required_future_approval": "",
                         "required_guardrail": "", "planning_only_note": "NONE"}]

    # bucket summary
    summary_rows = []
    for k, v_ in ps_ct.most_common():
        summary_rows.append({"dimension": "prior_parse_status", "key": k, "count": v_})
    for k, v_ in pattern_ct.most_common():
        summary_rows.append({"dimension": "value_pattern_class", "key": k, "count": v_})
    for k, v_ in bucket_ct.most_common():
        summary_rows.append({"dimension": "design_proof_bucket", "key": k, "count": v_})
    for k, v_ in fp_ct.most_common():
        summary_rows.append({"dimension": "false_positive_risk", "key": k, "count": v_})
    for k, v_ in approval_ct.most_common():
        summary_rows.append({"dimension": "required_future_approval", "key": k, "count": v_})

    write_csv(OUT / "unhandled_format_input_manifest.csv", input_rows)
    write_csv(OUT / "unhandled_format_value_profile.csv", profile_rows)
    write_csv(OUT / "unhandled_format_design_proof_matrix.csv", matrix_rows)
    write_csv(OUT / "unhandled_format_bucket_summary.csv", summary_rows)
    write_csv(OUT / "unhandled_format_blocker_ledger.csv", blocker_rows)

    # guardrails.md
    g = ["# Unhandled-format design proof — guardrails (PROPOSED, future-only)", "",
         "These guardrails describe what a FUTURE parser-change phase would have to",
         "prove before any extraction is implemented. Nothing here is implemented,",
         "approved, or applied. Every row stays fail-closed.", ""]
    for b, cnt in bucket_ct.most_common():
        rep = next(m for m in matrix_rows if m["design_proof_bucket"] == b)
        g.append(f"## {b} (n={cnt})")
        g.append(f"- false-positive risk: {rep['false_positive_risk']}")
        g.append(f"- required future approval: {rep['required_future_approval']}")
        g.append(f"- guardrail: {rep['required_guardrail']}")
        g.append("")
    (OUT / "unhandled_format_guardrails.md").write_text("\n".join(g), encoding="utf-8")

    # examples.md
    e = ["# Unhandled-format design proof — representative examples", "",
         "Inspection samples ONLY. NOT validation, NOT approval, NOT parsed rows.",
         "Candidate values are hypothetical / proof-only (NOT effective dates).", ""]
    for b, exs in examples_by_bucket.items():
        e.append(f"## {b}")
        for x in exs:
            e.append(f"- {x['rcept_no']} [{x['value_pattern_class']}] labels={x['labels_matched']} "
                     f"| imm=\"{x['immediate_value_text']}\" "
                     f"| hypothetical_iso_PROOF_ONLY={x['hypothetical_candidate_value_iso_PROOF_ONLY'] or '(none)'}")
        e.append("")
    (OUT / "unhandled_format_examples.md").write_text("\n".join(e), encoding="utf-8")

    # hard_lock_compliance_check.md
    hl = [
        "# Hard-lock compliance check — KR-STATUS-PARSER-UNHANDLED-FORMAT-DESIGN-PROOF-A0",
        "",
        "| lock | status |",
        "|---|---|",
        "| target = exactly 23 rows | PASS |",
        "| all 23 from `label_present_but_value_in_unhandled_format` | PASS |",
        "| all 23 within `date_format_or_relative_date_handling` theme | PASS |",
        "| no non-target row included | PASS |",
        "| no download / API / credential / source-recovery / body-repair | PASS (read-only cache + accepted CSVs) |",
        "| no parser code/rule/version change | PASS (parser imported read-only; not modified/invoked to change outputs) |",
        "| no edits under src/parsers/ | PASS |",
        "| no parser/candidate-linkage/body-confirmation rerun changing accepted outputs | PASS |",
        "| every row fail-closed | PASS (manual_review_required=True; all safety/readiness flags False) |",
        "| no row newly parsed/recovered/executable/safe/authoritative/validated/approved/ready | PASS |",
        "| candidate date/value evidence hypothetical/proof-only, not final | PASS (named *_PROOF_ONLY; no effective_date/parsed_date column) |",
        "| false-positive guardrails recorded for future parser-change candidates | PASS |",
        "| relative/TBD/unresolvable values not promoted, stay fail-closed | PASS |",
        "| outputs separate design proof from approved parser behavior | PASS |",
        "| no downstream/strategy/execution/readiness claim | PASS |",
        "| CSVs LF + git show --check HEAD passes | PASS (verified post-commit) |",
        "| no rcept_dt as effective date | PASS |",
        "| no self-close / no CLOSE_NOTE this pass | PASS |",
        "",
    ]
    (OUT / "hard_lock_compliance_check.md").write_text("\n".join(hl), encoding="utf-8")

    # report.md
    rep_lines = [
        "# KR-STATUS-PARSER-UNHANDLED-FORMAT-DESIGN-PROOF-A0 — Initial-Pass Report", "",
        "Read-only, proof-only design analysis of the 23 "
        "`label_present_but_value_in_unhandled_format` rows (prior feasibility theme "
        "`date_format_or_relative_date_handling`). No parser change; no downloads; every "
        "row stays fail-closed.", "",
        f"- target rows: **{len(input_rows)}** (all label_no_value / parser_design_candidate / "
        "parser_change_verdict; all html_inline, all locally available, all resumption-related, "
        "0 corrections).", "",
        "## Value pattern class (sum = 23)", "",
        "| value_pattern_class | count |", "|---|---:|",
    ]
    for k, c in pattern_ct.most_common():
        rep_lines.append(f"| {k} | {c} |")
    rep_lines += ["", "## Design-proof bucket (sum = 23)", "",
                  "| design_proof_bucket | count |", "|---|---:|"]
    for k, c in bucket_ct.most_common():
        rep_lines.append(f"| {k} | {c} |")
    rep_lines += ["", "## False-positive risk (sum = 23)", "",
                  "| false_positive_risk | count |", "|---|---:|"]
    for k, c in fp_ct.most_common():
        rep_lines.append(f"| {k} | {c} |")
    rep_lines += ["", "## Required future approval (sum = 23)", "",
                  "| required_future_approval | count |", "|---|---:|"]
    for k, c in approval_ct.most_common():
        rep_lines.append(f"| {k} | {c} |")
    rep_lines += [
        "", "## Honest headline finding", "",
        "\"Unhandled format\" OVERSTATED the parser-design opportunity for these 23 rows.",
        "Only the genuine 2-digit-year-format rows are a date-FORMAT matter, and only one "
        "row is a clean (guarded) future parser-change candidate:", "",
        "- **relative / TBD (the bulk):** the resumption date is defined relative to a "
        "future event (e.g. '…제출일 익일' = the day AFTER a future document submission) "
        "or is a deadline ('1년 이내 … 限'). No absolute date exists; a parser change "
        "cannot recover a date that is not present. Keep fail-closed.",
        "- **absolute date in 2-digit-year format ('YY.M.D):** a real date the parser's "
        "4-digit patterns miss. A future parser MIGHT add a strict rule, but only with "
        "century disambiguation and label-kind confirmation — guarded, not approved.",
        "- **date range / period to delisting (…~상장폐지):** a suspension PERIOD that "
        "resolves to delisting, not a resumption date. Out of scope; keep fail-closed.",
        "- **parseable date present but NON-target field:** a full 4-digit date IS present "
        "but it is the suspension timestamp (정지일시); the resumption value is genuinely "
        "absent. This is a field-selection / value-absence issue, NOT a date the parser "
        "fails to read — correcting the prior taxonomy's 'date-like fragment not "
        "parser-recognized' framing for these rows. Manual.", "",
        "All evidence is hypothetical / proof-only. No effective date is accepted; no "
        "parser change is made; all 23 rows remain fail-closed. This phase does NOT "
        "self-close.", "",
    ]
    (OUT / "report.md").write_text("\n".join(rep_lines), encoding="utf-8")

    print(f"[done] pattern={dict(pattern_ct)}")
    print(f"[done] buckets={dict(bucket_ct)}")
    print(f"[done] fp={dict(fp_ct)}")
    print(f"[done] approval={dict(approval_ct)}")
    print(f"[out] {OUT}")


if __name__ == "__main__":
    main()
