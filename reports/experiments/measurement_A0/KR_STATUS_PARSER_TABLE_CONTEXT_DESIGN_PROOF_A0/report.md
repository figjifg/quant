# KR-STATUS-PARSER-TABLE-CONTEXT-DESIGN-PROOF-A0 — Initial-Pass Report

Date: 2026-05-26
Phase opened by: Referee verdict (via relay), authorized by user's explicit decision to open a LOCAL-ONLY table-context parser-design PROOF phase.
Executor: Claude Code. Referee: Codex.

## Phase name and scope

Local-only, read-only PROOF of whether table/structure-aware extraction is design-feasible for the 170 needs_table_context_design rows, plus false-positive risk and required guardrails. NO parser change; NO src/parsers edits; parser imported read-only (label sets + date detector) and NOT invoked to change outputs. All candidate evidence is HYPOTHETICAL/PROOF-ONLY. Every row fail-closed. No self-close; no CLOSE_NOTE this pass.

## Exact 170-row accounting

- target rows: 170 (asserted == 170); all from feasibility_bucket=needs_table_context_design (prior taxonomy label_present_but_attachment_or_table_context_required; 0 attachment). No non-target row.

## Structure class (read-only profile)

| structure_class | count |
|---|---:|
| `label_in_table_value_empty_or_dash` | 170 |

## Design-proof bucket counts (sum to 170)

| design_proof_bucket | count |
|---|---:|
| `out_of_scope_keep_fail_closed` | 170 |
| **total** | **170** |

## False-positive risk counts

| false_positive_risk | count |
|---|---:|
| `blocked_not_evaluable` | 170 |

## Required-future-approval counts

| required_future_approval | count |
|---|---:|
| `none_keep_fail_closed` | 170 |

## Design-proof conclusion (planning evidence only) — HONEST HEADLINE

- **KEY FINDING: the prior `needs_table_context_design` feasibility label was OVER-optimistic for these rows.** All 170 / 170 -> `out_of_scope_keep_fail_closed`. Read-only table inspection shows the matched (resumption / release-date) label's value cell is an explicit `-` (empty/dash) — the resumption/release date is NOT YET DETERMINED in these suspension disclosures. 0 / 170 had a parseable date in the matched label's value cell.
- Therefore table/structure-aware extraction does NOT recover a date here: there is no value to recover (the cell is `-`). A future parser would correctly read the `-` and still produce nothing. These 170 are NOT a parser-design opportunity and remain fail-closed.
- Bucket distribution: future_parser_change_candidate_low_ambiguity 0 / future_parser_change_candidate_guarded 0 / ambiguous_requires_manual_or_later_design 0 / blocked_missing_or_uninspectable_structure 0 / out_of_scope_keep_fail_closed 170.
- Aside (NOT actioned): many of these disclosures DO carry a *suspension* timestamp in an adjacent cell (e.g. '매매거래정지 일시 | YYYY-..-.. HH:MM') that the parser's current label set misses due to token spacing. Extracting that is a DIFFERENT field + a label-pattern theme (not table-context) and would need its own separate design + parser-change verdict. Recorded as an observation only.
- Net: this design proof REDUCES the apparent parser-design surface — the 170 table-context rows are confirmed to have no extractable value (explicit `-`) and stay fail-closed. See table_context_guardrails.md.

## Blockers: 1 bucket-level entries (table_context_blocker_ledger.csv)

Each bucket records its false_positive_risk, required_future_approval, required_guardrail, and a planning_only_note (design-proof evidence only; NOT current parser behavior; NOT approval; row stays fail-closed; parser change needs a separate verdict).

## Defects

- None. Non-extracted rows remain fail-closed by design (expected).

## Hard-lock confirmations

- Target = exactly 170; no non-target row. Read-only of cached bodies + accepted artifacts.
- Parser imported read-only (label sets + find_first_date); NOT invoked to change outputs; NO src/parsers edits; no parser code/rule/version change; no parser/candidate/body rerun.
- Candidate date/value evidence is HYPOTHETICAL/PROOF-ONLY (hypothetical_candidate_value_iso_PROOF_ONLY; is_proof_only_not_parser_output=True); no effective date accepted/finalized; no rcept_dt as effective date.
- No manual adjudication/validation/approval; no row promoted; every row fail-closed (manual_review_required=True; executable_or_safe / downstream_authoritative / parsed / recovered / validated / approved / effective_date_accepted / strategy_ready = False).
- No downloads / API / source recovery / body repair. No downstream / C2-C3 / event-log / executable-status table / strategy / backtest / execution / performance / production / paper / live / P08 / shadow.
- CSVs written with LF line endings (git show --check expected to pass). No self-close; no CLOSE_NOTE; not moved to Closed/Frozen.

## Gate self-assessment

- All 15 gate conditions intended to hold (170 exact; all from needs_table_context_design; 0 attachment; no non-target; no download/API/source-recovery/body-repair; no parser change; no src/parsers edits; no candidate/body rerun; all fail-closed; no promotion; candidate evidence hypothetical/proof-only; FP guardrails recorded; design proof separated from approved behavior; no downstream/strategy/execution claim; CSV LF + git show --check). Self-assessment: CLOSE-READY for review.

## Decision requested from Referee

Executor does NOT self-close. Verdict options: A close as table-context design proof complete (planning evidence recorded; all rows fail-closed) / B another proof pass / C open a future parser-CHANGE phase for the low-ambiguity subset (needs its own user + Referee parser-change verdict; src/parsers edits forbidden until then) / D keep all strategy/execution closed.
