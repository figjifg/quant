"""KR-STATUS-PARSER-NONEXTRACTED-FEASIBILITY-A0 — builder.

Referee directive (2026-05-26, via relay), authorized by the user's explicit decision
to open a LOCAL-ONLY parser feasibility / design-triage phase. NOT download/API
approval, NOT parser-change approval, NOT manual-adjudication approval, NOT
downstream/execution/strategy/production approval.

Goal: a feasibility / design-triage classification over the 711 parser non-extracted
rows — assign read-only, NON-AUTHORITATIVE feasibility buckets + design themes +
blocker reasons + required-future-approval types, as PLANNING EVIDENCE ONLY.

This phase READS existing accepted local artifacts only (the parser non-extracted
taxonomy ledger). It:
- does NOT download / call APIs / use credentials / recover source / repair bodies,
- does NOT change parser code / rules / version, and does NOT rerun the parser,
  candidate linkage, or body confirmation (no accepted parse output changes),
- does NOT manually adjudicate / validate / approve any row,
- does NOT create CLOSE_NOTE.md (Executor does not self-close this phase),
- newly marks no row parsed / recovered / executable / safe / authoritative /
  validated / approved / strategy-ready / execution-ready / production-ready.

INTERPRETATION RULE (per directive): feasibility/design labels here are PLANNING
EVIDENCE ONLY. They do NOT mean a row is parsed/recovered/safe/validated/approved/
usable. A future parser-change phase, if any, requires a separate user + Referee
verdict. Every row stays fail-closed.
"""
from __future__ import annotations

import csv as _csv
import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
MA0 = REPO / "reports/experiments/measurement_A0"
OUT = MA0 / "KR_STATUS_PARSER_NONEXTRACTED_FEASIBILITY_A0"
TAX = MA0 / "KR_STATUS_PARSER_NONEXTRACTED_LOCAL_TAXONOMY_A0/parser_nonextracted_taxonomy_ledger.csv"

# Accepted splits (reconciliation targets).
PARSE_STATUS_EXPECT = {"no_label_match": 511, "label_no_value": 200}
TAXONOMY_EXPECT = {
    "only_generic_or_contextual_label": 499,
    "label_present_but_attachment_or_table_context_required": 170,
    "label_present_but_value_in_unhandled_format": 23,
    "correction_disclosure_manual_only": 18,
    "title_body_mismatch": 1,
}


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
        w = _csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})


def triage(taxonomy_class: str, root_cause_note: str) -> dict:
    """Map an accepted taxonomy class -> read-only, non-authoritative feasibility
    triage. Returns feasibility_bucket / design_theme / design_feasibility /
    blocker_reason / required_future_approval. Planning evidence only."""
    note = (root_cause_note or "").lower()
    if taxonomy_class == "only_generic_or_contextual_label":
        return {
            "feasibility_bucket": "parser_design_candidate",
            "design_theme": "contextual_or_label_pattern_expansion",
            "design_feasibility": "uncertain_high_fp_risk",
            "blocker_reason": "no exact date label in body (domain tokens present); "
                              "contextual date extraction without a label risks false "
                              "positives; a future parser-design phase must prove safety first",
            "required_future_approval": "parser_change_verdict_after_design_proof",
        }
    if taxonomy_class == "label_present_but_attachment_or_table_context_required":
        if "attachment" in note:
            return {
                "feasibility_bucket": "needs_attachment_or_source_channel",
                "design_theme": "attachment_or_source_channel_parsing",
                "design_feasibility": "low_out_of_html_inline_scope",
                "blocker_reason": "value in attachment / out of html-inline scope; needs "
                                  "attachment parsing or a different source channel",
                "required_future_approval": "parser_change_verdict_and_or_source_channel_verdict",
            }
        return {
            "feasibility_bucket": "needs_table_context_design",
            "design_theme": "table_or_structure_aware_extraction",
            "design_feasibility": "medium",
            "blocker_reason": "label is a table/column header; date value sits in a "
                              "non-adjacent cell lost during HTML->text flattening; needs "
                              "structure/table-aware extraction design",
            "required_future_approval": "parser_change_verdict",
        }
    if taxonomy_class == "label_present_but_value_in_unhandled_format":
        return {
            "feasibility_bucket": "parser_design_candidate",
            "design_theme": "date_format_or_relative_date_handling",
            "design_feasibility": "medium",
            "blocker_reason": "label present but value in relative/non-ISO/unhandled "
                              "format; needs date-format handling expansion",
            "required_future_approval": "parser_change_verdict",
        }
    if taxonomy_class == "correction_disclosure_manual_only":
        return {
            "feasibility_bucket": "correction_workflow_only",
            "design_theme": "correction_adjudication_workflow_not_parser_design",
            "design_feasibility": "n_a_not_a_parser_design_target",
            "blocker_reason": "correction disclosure; not addressable by parser design "
                              "alone; belongs to the correction adjudication workflow",
            "required_future_approval": "manual_adjudication_approval",
        }
    if taxonomy_class == "title_body_mismatch":
        return {
            "feasibility_bucket": "out_of_scope_or_keep_fail_closed",
            "design_theme": "n_a_body_off_topic",
            "design_feasibility": "n_a_keep_fail_closed",
            "blocker_reason": "body does not discuss the status event in recognizable "
                              "terms (possible categorization/source issue); not a "
                              "parser-design target",
            "required_future_approval": "none_keep_fail_closed",
        }
    return {
        "feasibility_bucket": "ambiguous_requires_later_decision",
        "design_theme": "unclassified",
        "design_feasibility": "unknown",
        "blocker_reason": f"taxonomy class {taxonomy_class} not mapped",
        "required_future_approval": "later_decision",
    }


def main() -> None:
    print("[start] KR-STATUS-PARSER-NONEXTRACTED-FEASIBILITY-A0")
    OUT.mkdir(parents=True, exist_ok=True)

    tax = pd.read_csv(TAX, dtype=str).fillna("")
    n = len(tax)
    assert n == 711, f"expected 711 rows, got {n}"
    ps_ct = Counter(tax["parse_status"])
    tx_ct = Counter(tax["root_cause_class"])
    for k, v in PARSE_STATUS_EXPECT.items():
        assert ps_ct.get(k, 0) == v, f"parse_status {k} {ps_ct.get(k)} != {v}"
    for k, v in TAXONOMY_EXPECT.items():
        assert tx_ct.get(k, 0) == v, f"taxonomy {k} {tx_ct.get(k)} != {v}"
    print(f"[control] split verified: {dict(ps_ct)} / {dict(tx_ct)}")

    input_rows: list[dict] = []
    matrix_rows: list[dict] = []
    examples_by_bucket: dict[str, list[dict]] = {}
    fb_ct: Counter = Counter()
    theme_ct: Counter = Counter()
    approval_ct: Counter = Counter()
    # cross-tabs
    ps_fb: Counter = Counter()
    tx_fb: Counter = Counter()

    for r in tax.to_dict(orient="records"):
        rid = r["rcept_no"]
        ps = r["parse_status"]
        tcls = r["root_cause_class"]
        t = triage(tcls, r.get("root_cause_note", ""))
        fb = t["feasibility_bucket"]
        fb_ct[fb] += 1
        theme_ct[t["design_theme"]] += 1
        approval_ct[t["required_future_approval"]] += 1
        ps_fb[(ps, fb)] += 1
        tx_fb[(tcls, fb)] += 1

        input_rows.append({
            "rcept_no": rid,
            "rcept_dt": r.get("rcept_dt", ""),
            "stock_code": r.get("stock_code", ""),
            "event_category": r.get("event_category", ""),
            "prior_parse_status": ps,
            "prior_taxonomy_class": tcls,
            "prior_taxonomy_note": r.get("root_cause_note", ""),
            "body_format": r.get("body_format", ""),          # html_inline (body locally present)
            "body_text_len": r.get("body_text_len", ""),
            "n_label_hits": r.get("n_label_hits", ""),
            "body_locally_available": (r.get("body_format", "") == "html_inline"),
            "is_correction": r.get("is_correction", ""),
            "provenance": "KR_STATUS_PARSER_NONEXTRACTED_LOCAL_TAXONOMY_A0/parser_nonextracted_taxonomy_ledger.csv",
        })

        matrix_rows.append({
            "rcept_no": rid,
            "prior_parse_status": ps,
            "prior_taxonomy_class": tcls,
            "feasibility_bucket": fb,
            "design_theme": t["design_theme"],
            "design_feasibility": t["design_feasibility"],
            "blocker_reason": t["blocker_reason"],
            "required_future_approval": t["required_future_approval"],
            # fail-closed flags — only explicit false / fail-closed markers (no approval/readiness fields):
            "fail_closed": True,
            "manual_review_required": True,
            "executable_or_safe": False,
            "downstream_authoritative": False,
            "parsed_clean_and_usable": False,
            "validated": False,
            "approved": False,
            "strategy_ready": False,
            "is_planning_evidence_only": True,
        })

        ex = examples_by_bucket.setdefault(fb, [])
        if len(ex) < 5:
            ex.append({
                "feasibility_bucket": fb, "rcept_no": rid, "prior_parse_status": ps,
                "prior_taxonomy_class": tcls, "body_text_len": r.get("body_text_len", ""),
                "n_label_hits": r.get("n_label_hits", ""),
                "design_theme": t["design_theme"],
            })

    assert sum(fb_ct.values()) == 711, f"feasibility sum {sum(fb_ct.values())} != 711"

    # blocker ledger (bucket-level)
    blocker_rows = []
    for fb, cnt in fb_ct.most_common():
        # representative blocker reason for the bucket (from first matrix row of bucket)
        rep = next(m for m in matrix_rows if m["feasibility_bucket"] == fb)
        blocker_rows.append({
            "scope": "bucket", "feasibility_bucket": fb, "n_rows": cnt,
            "blocker_reason": rep["blocker_reason"],
            "required_future_approval": rep["required_future_approval"],
            "parser_design_alone_sufficient": fb in ("parser_design_candidate", "needs_table_context_design"),
        })

    # bucket summary (counts by parse_status, taxonomy, feasibility bucket, theme)
    summary_rows = []
    for k, v in ps_ct.most_common():
        summary_rows.append({"dimension": "prior_parse_status", "key": k, "count": v})
    for k, v in tx_ct.most_common():
        summary_rows.append({"dimension": "prior_taxonomy_class", "key": k, "count": v})
    for k, v in fb_ct.most_common():
        summary_rows.append({"dimension": "feasibility_bucket", "key": k, "count": v})
    for k, v in theme_ct.most_common():
        summary_rows.append({"dimension": "design_theme", "key": k, "count": v})
    for k, v in approval_ct.most_common():
        summary_rows.append({"dimension": "required_future_approval", "key": k, "count": v})
    for (t_, fb), v in sorted(tx_fb.items()):
        summary_rows.append({"dimension": "taxonomy_x_feasibility", "key": f"{t_} -> {fb}", "count": v})

    write_csv(OUT / "parser_nonextracted_input_manifest.csv", input_rows)
    write_csv(OUT / "parser_nonextracted_feasibility_matrix.csv", matrix_rows)
    write_csv(OUT / "parser_nonextracted_bucket_summary.csv", summary_rows)
    write_csv(OUT / "parser_nonextracted_blocker_ledger.csv", blocker_rows or [
        {"scope": "all", "feasibility_bucket": "NONE", "n_rows": 0,
         "blocker_reason": "NONE", "required_future_approval": "NONE",
         "parser_design_alone_sufficient": ""}])

    examples = [e for lst in examples_by_bucket.values() for e in lst]
    write_examples(OUT / "parser_nonextracted_examples.md", examples_by_bucket)
    write_themes(OUT / "parser_design_candidate_themes.md", fb_ct, theme_ct)
    write_hard_lock_check(OUT / "hard_lock_compliance_check.md")
    write_report(OUT / "report.md", ps_ct, tx_ct, fb_ct, theme_ct, approval_ct, len(blocker_rows))

    print(json.dumps({
        "rows": 711,
        "parse_status_split": dict(ps_ct),
        "taxonomy_split": dict(tx_ct),
        "feasibility_buckets": dict(fb_ct),
        "feasibility_sum": sum(fb_ct.values()),
        "design_themes": dict(theme_ct),
        "required_future_approval": dict(approval_ct),
        "blocker_buckets": len(blocker_rows),
    }, indent=2, default=str))


def write_examples(path: Path, examples_by_bucket: dict) -> None:
    lines = ["# Parser Non-Extracted Feasibility — Inspection Examples", "",
             "Date: 2026-05-26",
             "Phase: KR-STATUS-PARSER-NONEXTRACTED-FEASIBILITY-A0", "",
             "**These rows are INSPECTION SAMPLES ONLY — not validation, not approval, "
             "not parsed/recovered/safe. Feasibility/design labels are planning evidence "
             "only.** A future parser-change phase, if any, needs a separate user + "
             "Referee verdict.", ""]
    for fb, ex in examples_by_bucket.items():
        lines.append(f"## {fb} (showing {len(ex)} samples)")
        lines.append("")
        lines.append("| rcept_no | prior_parse_status | prior_taxonomy_class | body_text_len | n_label_hits | design_theme |")
        lines.append("|---|---|---|---:|---:|---|")
        for e in ex:
            lines.append(f"| {e['rcept_no']} | {e['prior_parse_status']} | {e['prior_taxonomy_class']} | {e['body_text_len']} | {e['n_label_hits']} | {e['design_theme']} |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_themes(path: Path, fb_ct: Counter, theme_ct: Counter) -> None:
    path.write_text(f"""# Parser-Design Candidate Themes (DESIGN-ONLY — NOT APPROVED)

Date: 2026-05-26
Phase: KR-STATUS-PARSER-NONEXTRACTED-FEASIBILITY-A0

**Future design themes only. No parser rule is implemented here, and NO design is
approved. Any actual parser change requires a separate user + Referee parser-change
verdict (and, where noted, a design phase to prove safety first).**

## Candidate themes (planning evidence only)

| design theme | rows | feasibility | what a future design phase WOULD study (not now) |
|---|---:|---|---|
| `contextual_or_label_pattern_expansion` | {theme_ct.get('contextual_or_label_pattern_expansion', 0)} | uncertain (high false-positive risk) | whether a label-free / contextual date extractor can be made SAFE for the 499 generic/contextual rows; must prove low FP before any change |
| `table_or_structure_aware_extraction` | {theme_ct.get('table_or_structure_aware_extraction', 0)} | medium | structure/table-aware parsing so a header label can be tied to a non-adjacent value cell (lost in current HTML->text flattening) |
| `date_format_or_relative_date_handling` | {theme_ct.get('date_format_or_relative_date_handling', 0)} | medium | additional date formats / relative-date ("익일/추후/별도/미정") handling, with explicit rules for unresolvable relatives |
| `correction_adjudication_workflow_not_parser_design` | {theme_ct.get('correction_adjudication_workflow_not_parser_design', 0)} | n/a | correction rows are NOT a parser-design target; route to manual adjudication workflow (separate approval) |
| `n_a_body_off_topic` | {theme_ct.get('n_a_body_off_topic', 0)} | n/a | body off-topic; keep fail-closed (not a parser-design target) |

## Feasibility-bucket roll-up

| feasibility_bucket | rows |
|---|---:|
""" + "\n".join(f"| `{k}` | {v} |" for k, v in fb_ct.most_common()) + f"""
| **total** | **{sum(fb_ct.values())}** |

## Boundary

- These themes are planning evidence. No row is parsed/recovered/safe/validated/
  approved/usable. Parser code/rules/version are unchanged. A future parser-change
  phase requires a separate user + Referee verdict.
""", encoding="utf-8")


def write_hard_lock_check(path: Path) -> None:
    path.write_text("""# Hard-Lock Compliance Check (Parser Non-Extracted Feasibility)

Date: 2026-05-26
Phase: KR-STATUS-PARSER-NONEXTRACTED-FEASIBILITY-A0

| hard lock | status |
|---|---|
| Read existing local artifacts only; no new data | PASS (reads the accepted taxonomy ledger) |
| Target = exactly 711 rows (no non-target row) | PASS (asserted) |
| parse-status split 511 + 200 preserved | PASS (asserted) |
| taxonomy split 499 + 170 + 23 + 18 + 1 preserved | PASS (asserted) |
| NO downloads / API / credentials / source recovery | PASS |
| NO parser code / rule / version change | PASS (parser not invoked) |
| NO parser / candidate-linkage / body-confirmation rerun (no accepted parse output changed) | PASS |
| NO body reacquisition / cached-file repair | PASS |
| NO manual adjudication / validation / approval | PASS |
| NO row newly marked parsed/recovered/executable/safe/authoritative/validated/approved/ready | PASS |
| NO downstream / C2-C3 / event-log / executable-status table | PASS |
| NO strategy / backtest / execution / performance / production / paper / live / P08 / shadow | PASS |
| NO rcept_dt as effective date or fallback | PASS |
| Feasibility/design labels are PLANNING EVIDENCE ONLY (not approval/readiness) | PASS |
| Every row fail-closed | PASS |
| No CLOSE_NOTE; not self-closed; not moved to Closed/Frozen | PASS |
""", encoding="utf-8")


def write_report(path: Path, ps_ct, tx_ct, fb_ct, theme_ct, approval_ct, n_blockers) -> None:
    lines = [
        "# KR-STATUS-PARSER-NONEXTRACTED-FEASIBILITY-A0 — Initial-Pass Report", "",
        "Date: 2026-05-26",
        "Phase opened by: Referee verdict (via relay), authorized by user's explicit "
        "decision to open a LOCAL-ONLY parser feasibility / design-triage phase.",
        "Executor: Claude Code. Referee: Codex.", "",
        "## Phase name and scope", "",
        "Local-only feasibility / design-triage over the 711 parser non-extracted rows. "
        "Reads the accepted taxonomy ledger only; assigns read-only, non-authoritative "
        "feasibility buckets + design themes + blocker reasons + required-future-approval "
        "types. PLANNING EVIDENCE ONLY. No parser change, no downloads, no adjudication, "
        "no downstream/execution. Every row stays fail-closed. No self-close; no "
        "CLOSE_NOTE this pass.",
        "", "## Exact 711-row accounting", "",
        f"- input rows: {sum(ps_ct.values())} (asserted == 711); no non-target row.",
        f"- prior parse-status split: no_label_match {ps_ct['no_label_match']} + "
        f"label_no_value {ps_ct['label_no_value']} (= {sum(ps_ct.values())}).",
        "- prior taxonomy split: " + " + ".join(f"{k} {v}" for k, v in tx_ct.most_common())
        + f" (= {sum(tx_ct.values())}).",
        "", "## Feasibility bucket counts (sum to 711)", "",
        "| feasibility_bucket | count |", "|---|---:|",
    ]
    for k, v in fb_ct.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines.append(f"| **total** | **{sum(fb_ct.values())}** |")
    lines += ["", "## Design theme counts", "", "| design_theme | count |", "|---|---:|"]
    for k, v in theme_ct.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += ["", "## Required-future-approval counts", "",
              "| required_future_approval | count |", "|---|---:|"]
    for k, v in approval_ct.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "## Taxonomy -> feasibility mapping (deterministic)",
        "",
        "| prior taxonomy class | feasibility bucket | count |",
        "|---|---|---:|",
        f"| only_generic_or_contextual_label | parser_design_candidate | {tx_ct.get('only_generic_or_contextual_label',0)} |",
        f"| label_present_but_attachment_or_table_context_required | needs_table_context_design (all table; 0 attachment) | {tx_ct.get('label_present_but_attachment_or_table_context_required',0)} |",
        f"| label_present_but_value_in_unhandled_format | parser_design_candidate | {tx_ct.get('label_present_but_value_in_unhandled_format',0)} |",
        f"| correction_disclosure_manual_only | correction_workflow_only | {tx_ct.get('correction_disclosure_manual_only',0)} |",
        f"| title_body_mismatch | out_of_scope_or_keep_fail_closed | {tx_ct.get('title_body_mismatch',0)} |",
        "",
        "Note: parser_design_candidate (522) = 499 contextual/label-pattern (feasibility "
        "UNCERTAIN, high FP risk) + 23 unhandled-format (feasibility medium). "
        "\"Candidate\" means a row to be STUDIED by a future parser-design phase — NOT "
        "that it will be fixed or that any extraction is approved.",
        "",
        f"## Blockers: {n_blockers} bucket-level entries (see parser_nonextracted_blocker_ledger.csv)",
        "",
        "Every bucket records why a row cannot be handled by parser design alone today "
        "and what future approval would be required. No row-level blocker beyond these.",
        "",
        "## Defects", "",
        "- None. (Unrecovered/non-extracted rows remain fail-closed by design; that is "
        "the expected residual state, not a defect.)",
        "",
        "## Hard-lock confirmations", "",
        "- Target = exactly 711; no non-target row; splits 511+200 and 499+170+23+18+1 "
        "preserved (asserted).",
        "- Read-only of the accepted taxonomy ledger; parser NOT invoked; no parser "
        "code/rule/version change; no parser/candidate/body rerun; no accepted parse "
        "output changed.",
        "- No downloads / API / credentials / source recovery / body reacquisition / "
        "cached-file repair. No manual adjudication / validation / approval.",
        "- Feasibility/design labels are PLANNING EVIDENCE ONLY; outputs clearly "
        "separate planning/design feasibility from approved parser behavior.",
        "- No row newly marked parsed/recovered/executable/safe/authoritative/validated/"
        "approved/strategy-ready/execution-ready/production-ready; every row fail-closed.",
        "- No downstream / C2-C3 / event-log / executable-status table / strategy / "
        "execution / production / paper / live / P08 / shadow. No rcept_dt as effective "
        "date. No self-close; no CLOSE_NOTE; not moved to Closed/Frozen.",
        "",
        "## Gate self-assessment", "",
        "- All 11 gate conditions intended to hold (711 exact; 511+200; 499+170+23+18+1; "
        "no non-target; no download/API/source-recovery; no parser change; no "
        "candidate/body rerun; all fail-closed; no readiness/approval promotion; "
        "planning clearly separated from approved behavior; no downstream/strategy/"
        "execution claim). Self-assessment: CLOSE-READY for Referee review.",
        "",
        "## Decision requested from Referee", "",
        "Executor does NOT self-close. Initial-pass report submitted; awaiting Referee "
        "review. Verdict options: A close as feasibility/design-triage complete (planning "
        "evidence recorded; all rows fail-closed) / B another feasibility pass / C open a "
        "future parser-design phase for a specific theme (needs its own user + Referee "
        "verdict; parser changes still forbidden until then) / D keep all "
        "strategy/execution closed.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
