# KR-STATUS-PARSER-NONEXTRACTED-FEASIBILITY-A0 — Initial-Pass Report

Date: 2026-05-26
Phase opened by: Referee verdict (via relay), authorized by user's explicit decision to open a LOCAL-ONLY parser feasibility / design-triage phase.
Executor: Claude Code. Referee: Codex.

## Phase name and scope

Local-only feasibility / design-triage over the 711 parser non-extracted rows. Reads the accepted taxonomy ledger only; assigns read-only, non-authoritative feasibility buckets + design themes + blocker reasons + required-future-approval types. PLANNING EVIDENCE ONLY. No parser change, no downloads, no adjudication, no downstream/execution. Every row stays fail-closed. No self-close; no CLOSE_NOTE this pass.

## Exact 711-row accounting

- input rows: 711 (asserted == 711); no non-target row.
- prior parse-status split: no_label_match 511 + label_no_value 200 (= 711).
- prior taxonomy split: only_generic_or_contextual_label 499 + label_present_but_attachment_or_table_context_required 170 + label_present_but_value_in_unhandled_format 23 + correction_disclosure_manual_only 18 + title_body_mismatch 1 (= 711).

## Feasibility bucket counts (sum to 711)

| feasibility_bucket | count |
|---|---:|
| `parser_design_candidate` | 522 |
| `needs_table_context_design` | 170 |
| `correction_workflow_only` | 18 |
| `out_of_scope_or_keep_fail_closed` | 1 |
| **total** | **711** |

## Design theme counts

| design_theme | count |
|---|---:|
| `contextual_or_label_pattern_expansion` | 499 |
| `table_or_structure_aware_extraction` | 170 |
| `date_format_or_relative_date_handling` | 23 |
| `correction_adjudication_workflow_not_parser_design` | 18 |
| `n_a_body_off_topic` | 1 |

## Required-future-approval counts

| required_future_approval | count |
|---|---:|
| `parser_change_verdict_after_design_proof` | 499 |
| `parser_change_verdict` | 193 |
| `manual_adjudication_approval` | 18 |
| `none_keep_fail_closed` | 1 |

## Taxonomy -> feasibility mapping (deterministic)

| prior taxonomy class | feasibility bucket | count |
|---|---|---:|
| only_generic_or_contextual_label | parser_design_candidate | 499 |
| label_present_but_attachment_or_table_context_required | needs_table_context_design (all table; 0 attachment) | 170 |
| label_present_but_value_in_unhandled_format | parser_design_candidate | 23 |
| correction_disclosure_manual_only | correction_workflow_only | 18 |
| title_body_mismatch | out_of_scope_or_keep_fail_closed | 1 |

Note: parser_design_candidate (522) = 499 contextual/label-pattern (feasibility UNCERTAIN, high FP risk) + 23 unhandled-format (feasibility medium). "Candidate" means a row to be STUDIED by a future parser-design phase — NOT that it will be fixed or that any extraction is approved.

## Blockers: 4 bucket-level entries (see parser_nonextracted_blocker_ledger.csv)

Each bucket records its blocker_reason, the required_future_approval, and a PLANNING-ONLY flag `future_parser_design_route_possible` (True for the parser-design-route buckets, False for correction/out-of-scope). That flag is explicitly NOT current sufficiency and NOT approval — every row stays blocked/fail-closed and any parser change needs a separate user + Referee verdict (the ledger also carries a `planning_only_note` saying exactly this). No row-level blocker beyond these bucket entries.

## Defects

- None. (Unrecovered/non-extracted rows remain fail-closed by design; that is the expected residual state, not a defect.)

## Hard-lock confirmations

- Target = exactly 711; no non-target row; splits 511+200 and 499+170+23+18+1 preserved (asserted).
- Read-only of the accepted taxonomy ledger; parser NOT invoked; no parser code/rule/version change; no parser/candidate/body rerun; no accepted parse output changed.
- No downloads / API / credentials / source recovery / body reacquisition / cached-file repair. No manual adjudication / validation / approval.
- Feasibility/design labels are PLANNING EVIDENCE ONLY; outputs clearly separate planning/design feasibility from approved parser behavior.
- No row newly marked parsed/recovered/executable/safe/authoritative/validated/approved/strategy-ready/execution-ready/production-ready; every row fail-closed.
- No downstream / C2-C3 / event-log / executable-status table / strategy / execution / production / paper / live / P08 / shadow. No rcept_dt as effective date. No self-close; no CLOSE_NOTE; not moved to Closed/Frozen.

## Gate self-assessment

- All 11 gate conditions intended to hold (711 exact; 511+200; 499+170+23+18+1; no non-target; no download/API/source-recovery; no parser change; no candidate/body rerun; all fail-closed; no readiness/approval promotion; planning clearly separated from approved behavior; no downstream/strategy/execution claim). Self-assessment: CLOSE-READY for Referee review.

## Decision requested from Referee

Executor does NOT self-close. Initial-pass report submitted; awaiting Referee review. Verdict options: A close as feasibility/design-triage complete (planning evidence recorded; all rows fail-closed) / B another feasibility pass / C open a future parser-design phase for a specific theme (needs its own user + Referee verdict; parser changes still forbidden until then) / D keep all strategy/execution closed.
