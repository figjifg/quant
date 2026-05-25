"""KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0 — builder.

Referee directive REF-OPEN-005 (2026-05-26, via relay). Follows the now-closed
KR-STATUS-RESIDUAL-BLOCKER-REGISTER-A0.

Goal: classify WHY parser extraction failed for the 711 parser non-extracted rows
(511 no_label_match + 200 label_no_value), as LOCAL ROOT-CAUSE TAXONOMY supporting a
future manual-review / parser-design phase.

This is NOT parser expansion. It:
- does NOT change parser code or behaviour (it only CALLS the existing parser's
  read-only helpers extract_body_from_zip + find_label_hits),
- does NOT re-extract or assign effective_date,
- does NOT reclassify any row as extracted / parsed / safe,
- preserves original parse_status exactly (no_label_match stays no_label_match,
  label_no_value stays label_no_value),
- preserves all fail-closed flags on every row,
- reads existing local cached ZIP bodies only — NO downloads / API / repair.

Every taxonomy row stays fail-closed: manual_review_required=True,
executable_or_safe=False, downstream_authoritative=False,
parsed_clean_and_usable=False, strategy_ready=False, production_ready=False.
"""
from __future__ import annotations

import csv as _csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

REPO = Path("/home/jin/code/quant")
sys.path.insert(0, str(REPO))

from src.audit.measurement_a0.p_status_correction_linkage import ZIP_CACHE  # noqa: E402
from src.parsers.krx_status_html_inline import (  # noqa: E402
    extract_body_from_zip,
    find_label_hits,
    _normalize_for_scan,
)

MA0 = REPO / "reports/experiments/measurement_A0"
UNIV = MA0 / "S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0/universe_body_status_reconciled.csv"
ADJ = MA0 / "KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0/correction_residual_action_ledger.csv"
REGISTER = MA0 / "KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0/residual_blocker_register.csv"
OUT = MA0 / "KR_STATUS_PARSER_NONEXTRACTED_LOCAL_TAXONOMY_A0"

PRIOR = {"no_label_match": 511, "label_no_value": 200, "total": 711,
         "correction_no_label_match": 11, "correction_label_no_value": 7}

# Domain context tokens (status-event vocabulary) — used to tell
# "no recognizable label but domain-relevant" from "body not even on-topic".
DOMAIN_TOKENS = ("정지", "재개", "해제", "거래정지", "매매거래", "상장폐지",
                 "정리매매", "거래정지기간", "매매거래정지")
# Attachment / external-context markers.
ATTACHMENT_TOKENS = ("첨부", "별첨", "붙임", "첨부파일", "별도 첨부", "참조")
# Relative / non-ISO date expressions the parser cannot turn into a date.
RELATIVE_DATE_TOKENS = ("익일", "추후", "별도", "미정", "추후통보", "통보예정",
                        "별도통지", "별도 통지", "추후 통보", "예정", "당분간", "통보")
# A date-LIKE fragment adjacent to a label (year / 월 / 일 / m-d) — present but the
# parser could not normalize it to a full ISO date.
DATE_FRAGMENT_RE = re.compile(r"\d{4}|\d{1,2}\s*월|\d{1,2}\s*일|\d{1,2}\s*[-./]\s*\d{1,2}")
IMMEDIATE_AFTER_CHARS = 25
SHORT_BODY_CHARS = 60


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


def classify_no_label_match(body_text: str, body_format: str) -> tuple[str, str]:
    if body_format != "html_inline" or len(body_text.strip()) < SHORT_BODY_CHARS:
        return ("body_text_too_short_or_malformed",
                f"body_format={body_format}, len={len(body_text.strip())}")
    norm = _normalize_for_scan(body_text)
    has_domain = any(tok in norm for tok in DOMAIN_TOKENS)
    if has_domain:
        return ("only_generic_or_contextual_label",
                "domain tokens present (정지/재개/해제…) but no exact date label")
    # substantial body, no exact label, no domain token at all → categorized as
    # status event by title but body does not discuss it in recognizable terms.
    return ("title_body_mismatch",
            "substantial body but no status-event domain token / date label")


def classify_label_no_value(body_text: str, hits) -> tuple[str, str]:
    # The parser found labels but no parseable date. Inspect the IMMEDIATE window
    # right after each label (not a wide window — wide windows pick up unrelated
    # table/section digits, which over-counts 'unhandled format'). Calibrated on the
    # 193 non-correction rows: 170 are table/header context (label is a column
    # header, value sits in a non-adjacent cell lost during text flattening),
    # 18 relative-date, 5 date-fragment-but-unparseable.
    imm_parts = []
    for h in hits:
        w = _normalize_for_scan(h.window)
        i = w.find(h.label)
        if i >= 0:
            imm_parts.append(w[i + len(h.label): i + len(h.label) + IMMEDIATE_AFTER_CHARS])
    imm = " ".join(imm_parts)
    full = _normalize_for_scan(body_text)

    has_relative = any(tok in imm for tok in RELATIVE_DATE_TOKENS)
    has_fragment = bool(DATE_FRAGMENT_RE.search(imm))
    has_attachment = any(tok in full for tok in ATTACHMENT_TOKENS)

    if has_relative:
        return ("label_present_but_value_in_unhandled_format",
                "label present; relative/non-ISO expression adjacent (익일/추후/별도/미정…)")
    if has_fragment:
        return ("label_present_but_value_in_unhandled_format",
                "label present; date-like fragment adjacent but not parser-recognized format")
    if has_attachment:
        return ("label_present_but_attachment_or_table_context_required",
                "label present; attachment marker in body; value likely in attachment")
    if imm.strip(" -·.:|"):
        return ("label_present_but_attachment_or_table_context_required",
                "label appears as a header; date value not adjacent (table/structure "
                "context lost in text flattening)")
    return ("label_present_but_empty_value",
            "label present; no adjacent value text after the label")


def main() -> None:
    print("[start] KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0")
    OUT.mkdir(parents=True, exist_ok=True)

    univ = pd.read_csv(UNIV, dtype=str).fillna("")
    adj = pd.read_csv(ADJ, dtype=str).fillna("")
    corr_ids = set(adj["correction_rcept_no"])

    nonext = univ[univ["parse_status"].isin(["no_label_match", "label_no_value"])].copy()
    n = len(nonext)
    print(f"[in_scope] {n} parser non-extracted rows")
    assert n == PRIOR["total"], f"expected 711, got {n}"
    ps_ct = Counter(nonext["parse_status"])
    assert ps_ct["no_label_match"] == 511 and ps_ct["label_no_value"] == 200, \
        f"split mismatch {dict(ps_ct)}"
    print(f"[control] split preserved {dict(ps_ct)}")

    cached = {p.stem for p in ZIP_CACHE.glob("*.zip")}

    ledger: list[dict] = []
    overlap_rows: list[dict] = []
    examples_by_class: dict[str, list[dict]] = {}
    length_dist: list[dict] = []
    root_counts: Counter = Counter()
    corr_overlap_ps: Counter = Counter()

    for r in nonext.to_dict(orient="records"):
        rid = r["rcept_no"]
        parse_status = r["parse_status"]
        is_corr = rid in corr_ids

        body_text = ""
        body_format = r.get("body_format", "")
        n_hits = 0
        if rid in cached:
            try:
                be = extract_body_from_zip((ZIP_CACHE / f"{rid}.zip").read_bytes())
                body_text = be.text
                body_format = be.body_format
                hits = find_label_hits(body_text) if body_text else []
                n_hits = len(hits)
            except Exception:
                hits = []
        else:
            hits = []

        # Root cause — corrections are manual-only regardless of body reason.
        if is_corr:
            root, note = ("correction_disclosure_manual_only",
                          f"correction row; parse_status={parse_status}; manual-only")
            corr_overlap_ps[parse_status] += 1
        elif parse_status == "no_label_match":
            root, note = classify_no_label_match(body_text, body_format)
        else:  # label_no_value
            if not hits:
                root, note = ("other_nonextracted_manual_review",
                              "label_no_value but no label hits re-found locally")
            else:
                root, note = classify_label_no_value(body_text, hits)

        root_counts[root] += 1

        row = {
            "rcept_no": rid,
            "rcept_dt": r.get("rcept_dt", ""),
            "stock_code": r.get("stock_code", ""),
            "event_category": r.get("event_category", ""),
            "parse_status": parse_status,           # PRESERVED exactly
            "body_format": body_format,
            "body_text_len": len(body_text.strip()),
            "n_label_hits": n_hits,
            "is_correction": is_corr,
            "root_cause_class": root,
            "root_cause_note": note,
            # fail-closed flags — always these values:
            "manual_review_required": True,
            "executable_or_safe": False,
            "downstream_authoritative": False,
            "parsed_clean_and_usable": False,
            "strategy_ready": False,
            "production_ready": False,
            "effective_date_extracted": False,      # taxonomy only
        }
        ledger.append(row)

        length_dist.append({"rcept_no": rid, "parse_status": parse_status,
                            "body_text_len": len(body_text.strip()), "n_label_hits": n_hits})

        if is_corr:
            overlap_rows.append({
                "rcept_no": rid,
                "parse_status": parse_status,
                "root_cause_class": root,
                "body_text_len": len(body_text.strip()),
                "n_label_hits": n_hits,
                "note": "correction overlap; manual_review_required; non-authoritative",
            })

        ex = examples_by_class.setdefault(root, [])
        if len(ex) < 8:
            snippet = _normalize_for_scan(body_text)[:200]
            ex.append({
                "root_cause_class": root,
                "rcept_no": rid,
                "parse_status": parse_status,
                "is_correction": is_corr,
                "body_text_len": len(body_text.strip()),
                "n_label_hits": n_hits,
                "body_snippet_200": snippet,
            })

    assert sum(root_counts.values()) == 711, f"root sum {sum(root_counts.values())} != 711"
    assert corr_overlap_ps["no_label_match"] == 11, f"corr no_label {corr_overlap_ps['no_label_match']} != 11"
    assert corr_overlap_ps["label_no_value"] == 7, f"corr label_no_value {corr_overlap_ps['label_no_value']} != 7"

    examples = [e for lst in examples_by_class.values() for e in lst]

    # Write deliverables
    write_csv(OUT / "parser_nonextracted_taxonomy_ledger.csv", ledger)
    write_csv(OUT / "parser_nonextracted_root_cause_counts.csv",
              [{"root_cause_class": k, "count": v} for k, v in root_counts.most_common()])
    write_csv(OUT / "parser_nonextracted_correction_overlap.csv", overlap_rows)
    write_csv(OUT / "parser_nonextracted_examples.csv", examples)
    # optional
    write_csv(OUT / "body_text_length_distribution.csv", length_dist)

    write_design_backlog(OUT / "parser_design_backlog_candidates.md", root_counts)
    write_fail_closed_check(OUT / "fail_closed_policy_check.md")
    write_input_manifest(OUT / "prior_phase_input_manifest.md")
    write_hard_lock_check(OUT / "hard_lock_compliance_check.md")
    write_unresolved(OUT / "unresolved_questions.md", root_counts)
    write_summary(OUT / "parser_nonextracted_taxonomy_summary.md", ps_ct, root_counts, corr_overlap_ps)
    write_report(OUT / "report.md", ps_ct, root_counts, corr_overlap_ps)

    print(json.dumps({
        "in_scope": n,
        "split": dict(ps_ct),
        "root_cause_counts": dict(root_counts),
        "root_sum": sum(root_counts.values()),
        "correction_overlap": dict(corr_overlap_ps),
    }, indent=2, default=str))


def write_design_backlog(path: Path, root_counts: Counter) -> None:
    path.write_text(f"""# Parser-Design Backlog Candidates (DESIGN-ONLY — NOT APPROVED)

Date: 2026-05-26
Phase: KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0

**These are DESIGN-ONLY candidates derived from the local root-cause taxonomy. They
are NOT approved for any parser change. No parser code may be modified without a
separate Referee verdict opening a parser-design/expansion phase.**

| root cause | rows | hypothetical future handling (DESIGN-ONLY, NOT APPROVED) |
|---|---:|---|
| `label_present_but_value_in_unhandled_format` | {root_counts.get('label_present_but_value_in_unhandled_format', 0)} | a future phase *might* study additional date formats / relative-date handling — NOT now |
| `label_present_but_attachment_or_table_context_required` | {root_counts.get('label_present_but_attachment_or_table_context_required', 0)} | value likely in attachment/table; out of html-inline scope; needs separate verdict |
| `label_present_but_empty_value` | {root_counts.get('label_present_but_empty_value', 0)} | genuinely empty value cell; likely irrecoverable without source |
| `only_generic_or_contextual_label` | {root_counts.get('only_generic_or_contextual_label', 0)} | body on-topic but no exact date label; manual review |
| `title_body_mismatch` | {root_counts.get('title_body_mismatch', 0)} | body not on status-event topic in recognizable terms; manual review |
| `body_text_too_short_or_malformed` | {root_counts.get('body_text_too_short_or_malformed', 0)} | short/malformed body; likely source defect |
| `correction_disclosure_manual_only` | {root_counts.get('correction_disclosure_manual_only', 0)} | correction rows; manual-only; never auto-parsed |
| `other_nonextracted_manual_review` | {root_counts.get('other_nonextracted_manual_review', 0)} | unclassified; manual review |

## Hard boundary

- This table does NOT authorize parser changes, extraction upgrades, or any
  reclassification. Every row remains `no_label_match` / `label_no_value`,
  fail-closed, manual_review_required.
""", encoding="utf-8")


def write_fail_closed_check(path: Path) -> None:
    path.write_text("""# Fail-Closed Policy Check (Parser Non-Extracted Taxonomy)

Date: 2026-05-26
Phase: KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0

Every taxonomy row remains fail-closed. The root-cause class is DIAGNOSTIC ONLY and
does NOT change parse_status or any safety flag.

| check | status |
|---|---|
| original parse_status preserved (no_label_match / label_no_value) | PASS |
| 511 / 200 split preserved | PASS |
| manual_review_required=True on all 711 | PASS |
| executable_or_safe=False on all 711 | PASS |
| downstream_authoritative=False on all 711 | PASS |
| parsed_clean_and_usable=False on all 711 | PASS |
| strategy_ready=False on all 711 | PASS |
| production_ready=False on all 711 | PASS |
| effective_date_extracted=False on all 711 (taxonomy only) | PASS |
| no root_cause class implies parser success | PASS |
| no parser behaviour changed (only read-only helpers called) | PASS |
""", encoding="utf-8")


def write_input_manifest(path: Path) -> None:
    path.write_text(f"""# Prior-Phase Input Manifest

Date: 2026-05-26
Phase: KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0

## Inputs used (read-only)

- `{UNIV.relative_to(REPO)}`
  (12,187-row universe body status → the 711 no_label_match + label_no_value rows).
- `{ADJ.relative_to(REPO)}`
  (166 correction ids → correction overlap of 11 no_label + 7 label_no_value).
- `{REGISTER.relative_to(REPO)}` (blocker register; context).
- Cached bodies: `{ZIP_CACHE.relative_to(REPO)}/` (read-only; for body inspection).

## Parser helpers CALLED read-only (NOT modified)

- `src/parsers/krx_status_html_inline.py`: `extract_body_from_zip`,
  `find_label_hits`, `_normalize_for_scan`. No parser code changed.

## No network. No downloads / API / acquisition / body repair.

## New code

- `src/audit/measurement_a0/p_parser_nonextracted_local_taxonomy.py` (this phase).
""", encoding="utf-8")


def write_hard_lock_check(path: Path) -> None:
    path.write_text("""# Hard-Lock Compliance Check (Parser Non-Extracted Taxonomy)

Date: 2026-05-26
Phase: KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0

| hard lock | status |
|---|---|
| Existing local artifacts + cached bodies (read-only) only | PASS |
| NO downloads / API / acquisition / body repair | PASS |
| NO parser feature expansion / code change / extraction upgrade | PASS (only read-only helpers called) |
| NO candidate search / body confirmation rerun | PASS |
| NO effective_date extracted or assigned | PASS |
| original parse_status preserved; 511/200 split preserved | PASS |
| all 711 fail-closed (manual_review_required=True, etc.) | PASS |
| no row promoted to parsed/extracted/executable/safe/strategy-ready | PASS |
| NOT an event log / executable-status table / downstream wiring | PASS |
| NO C2/C3 / strategy / performance / execution / backtest | PASS |
| root-cause counts sum to 711; correction overlap 11/7 reconciled | PASS (asserted) |
| parser-design backlog is design-only, NOT approved | PASS |
""", encoding="utf-8")


def write_unresolved(path: Path, root_counts: Counter) -> None:
    path.write_text(f"""# Unresolved Questions (local, for later — NOT decisions)

Date: 2026-05-26
Phase: KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0

Packaged for a FUTURE human/Referee decision. This phase does NOT answer them.

1. `label_present_but_value_in_unhandled_format`
   ({root_counts.get('label_present_but_value_in_unhandled_format', 0)} rows): would
   a future parser-design phase study extra date formats / relative-date handling?
   NOT now (no parser changes authorized).
2. `label_present_but_attachment_or_table_context_required`
   ({root_counts.get('label_present_but_attachment_or_table_context_required', 0)}):
   value likely outside html-inline scope; separate feasibility verdict needed.
3. `title_body_mismatch` ({root_counts.get('title_body_mismatch', 0)}) and
   `body_text_too_short_or_malformed`
   ({root_counts.get('body_text_too_short_or_malformed', 0)}): possible
   source/categorization defects; manual review only.
""", encoding="utf-8")


def write_summary(path: Path, ps_ct: Counter, root_counts: Counter,
                  corr_overlap_ps: Counter) -> None:
    lines = [
        "# KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0 — Summary",
        "", "Date: 2026-05-26",
        "Opened by Referee directive REF-OPEN-005 (via relay).",
        "Local root-cause taxonomy for the 711 parser non-extracted rows.",
        "",
        f"## In-scope: **711** non-extracted rows "
        f"(no_label_match {ps_ct['no_label_match']} + label_no_value {ps_ct['label_no_value']})",
        "",
        "## Root-cause classes (sum to 711)",
        "",
        "| root_cause_class | count |", "|---|---:|",
    ]
    for k, v in root_counts.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines.append(f"| **total** | **{sum(root_counts.values())}** |")
    lines += [
        "",
        f"## Correction overlap: no_label_match {corr_overlap_ps['no_label_match']} + "
        f"label_no_value {corr_overlap_ps['label_no_value']} = "
        f"{sum(corr_overlap_ps.values())} (all `correction_disclosure_manual_only`)",
        "",
        "## Boundaries",
        "",
        "- Taxonomy is local/manual-review support ONLY. No parser behaviour changed.",
        "- No effective_date extracted/assigned. parse_status + 511/200 split preserved.",
        "- All 711 fail-closed; no row parsed/executable/safe/strategy-ready.",
        "- Parser-design backlog is DESIGN-ONLY, NOT approved.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, ps_ct: Counter, root_counts: Counter,
                 corr_overlap_ps: Counter) -> None:
    lines = [
        "# KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0 — Report",
        "", "Date: 2026-05-26",
        "Phase opened by: Referee directive REF-OPEN-005 (via relay).",
        "Executor: Claude Code. Referee: Codex.",
        "",
        "## Phase name and scope",
        "",
        "Measurement-layer parser non-extracted LOCAL ROOT-CAUSE TAXONOMY only. "
        "suspension_related + resumption_related status rows. Existing local "
        "artifacts + cached bodies (read-only) only. No downloads, no API, no body "
        "repair, no parser feature expansion / code change / extraction upgrade, no "
        "candidate/body rerun, no downstream wiring, no C2/C3, no event-log "
        "finalization, no executable-status table, no strategy / performance / "
        "execution work.",
        "",
        "## Inputs used (paths)",
        "",
        f"- `{UNIV.relative_to(REPO)}` (the 711 non-extracted rows).",
        f"- `{ADJ.relative_to(REPO)}` (166 correction ids → 11/7 overlap).",
        f"- Cached bodies: `{ZIP_CACHE.relative_to(REPO)}/` (read-only).",
        "- Parser read-only helpers extract_body_from_zip / find_label_hits "
        "(no parser change). See `prior_phase_input_manifest.md`.",
        "",
        "## Exact source counts",
        "",
        f"- no_label_match: **{ps_ct['no_label_match']}**",
        f"- label_no_value: **{ps_ct['label_no_value']}**",
        f"- total: **{sum(ps_ct.values())}**",
        "",
        "## Exact correction overlap",
        "",
        f"- no_label_match correction rows: **{corr_overlap_ps['no_label_match']}**",
        f"- label_no_value correction rows: **{corr_overlap_ps['label_no_value']}**",
        f"- total correction overlap: **{sum(corr_overlap_ps.values())}** (all "
        "classified `correction_disclosure_manual_only`).",
        "",
        "## Exact root-cause counts (sum to 711)",
        "",
        "| root_cause_class | count |", "|---|---:|",
    ]
    for k, v in root_counts.most_common():
        lines.append(f"| `{k}` | {v} |")
    lines.append(f"| **total** | **{sum(root_counts.values())}** |")
    lines += [
        "",
        "## Method (read-only)",
        "",
        "For each row, the cached body was loaded read-only via the parser's "
        "`extract_body_from_zip`, and labels re-found via `find_label_hits` (the SAME "
        "helpers the parser uses — not modified). Corrections → "
        "`correction_disclosure_manual_only` (manual-only regardless of body). "
        "no_label_match non-corrections classified by body content (short/malformed; "
        "domain-token-present-but-no-exact-label; or off-topic). label_no_value "
        "non-corrections classified by the after-label window (relative/unhandled "
        "date format; attachment/table context; or empty value).",
        "",
        "## Required statements",
        "",
        "- Root-cause taxonomy is LOCAL / MANUAL-REVIEW SUPPORT ONLY.",
        "- NO parser behaviour changed (only read-only helpers called).",
        "- NO effective_date was extracted or assigned.",
        "- NO row became parsed, executable, safe, strategy-ready, production-ready, "
        "or downstream-authoritative. parse_status + 511/200 split preserved.",
        "- NO downloads / API / body repair occurred.",
        "- NO strategy, backtest, execution simulation, C2/C3, event-log "
        "finalization, executable-status table, or production/paper/live/P08/shadow "
        "work occurred.",
        "",
        "## Defects / residuals (preserved, fail-closed)",
        "",
        "- All 711 rows remain non-extracted, manual_review_required, fail-closed.",
        "- The root cause is diagnostic only; a parser-design backlog "
        "(`parser_design_backlog_candidates.md`) is DESIGN-ONLY and NOT approved.",
        "",
        "## Decision requested from Referee",
        "",
        "Executor does NOT self-close. Requesting a verdict among:",
        "- **A.** close as parser non-extracted local taxonomy complete;",
        "- **B.** require another taxonomy pass (refine root-cause heuristics);",
        "- **C.** open a separate parser-design / feasibility phase for one or more "
        "root-cause classes (would need its own verdict; parser changes still "
        "forbidden until then);",
        "- **D.** keep all strategy / execution research closed (unchanged).",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
