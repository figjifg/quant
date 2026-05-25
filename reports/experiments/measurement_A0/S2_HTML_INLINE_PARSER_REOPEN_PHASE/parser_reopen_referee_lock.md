# S2-HTML-INLINE-PARSER-REOPEN-PHASE — Referee Lock

Date: 2026-05-25  
Verdict source: Referee verdict opening this phase, 2026-05-25.  
Predecessor: `KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE` CLOSED AS
MANUAL-AUDIT-COMPLETED / SUPPORTS HTML-INLINE PARSER REOPEN / EXECUTION STILL CLOSED
(commit `8339efb`).

## Scope (Referee-fixed)

- Measurement-layer parser reopen only.
- Narrow parser work for HTML-inline OPENDART/KRX exchange-status disclosures.
- Initial scope limited to:
  - `suspension_related` only
  - `resumption_related` only
  - `effective_date`
  - `suspension_period`
  - `resumption_date`
  - HTML-inline body only
- No delisting parser.
- No liquidation parser.
- No managed / alert parser in first pass.
- No DART body alpha.
- No overhang parser.
- No strategy testing.
- No performance diagnostics.
- No execution simulation.
- No production / paper / P08 / live / shadow.

## Pass-criteria (Referee-fixed)

- Parser handles HTML-inline body format for suspension / resumption samples.
- Parser output schema produced.
- Parser validated against manual audit sample.
- Suspension / resumption extraction rates reported.
- False positives on negative controls measured.
- Correction-flagged rows forced to manual review.
- Defect ledger produced.
- Gate status explicitly stated.
- No strategy test / execution simulation / performance metric produced.

## Fail / partial gates

- Parser cannot materially beat simple regex → PARTIAL or FAIL.
- Parser extracts unsupported-category dates incorrectly → PARTIAL + defect.
- Correction rows treated as authoritative → FAIL.
- `rcept_dt` used as `effective_date` fallback → FAIL.
- Parser result described as strategy-ready → FAIL.
- Any strategy metric produced → protocol violation.

## Parser gate enum (Referee-permitted)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `HTML_INLINE_PARSER_BUILT_BUT_NOT_VALIDATED`
- `HTML_INLINE_PARSER_VALIDATED_FOR_SUSPENSION_RESUMPTION_ONLY`
- `HTML_INLINE_PARSER_REQUIRES_MORE_WORK`
- `READY_FOR_NEXT_A0_REVIEW`

## Allowed tasks (9)

1. Parser input sample construction (reuse 195 manual-audit ZIPs + extend if needed).
2. HTML-inline parser design.
3. Parser implementation (narrow scope; module + utility + tests).
4. Parser output schema.
5. Validation against manual audit (ground truth).
6. Negative controls (delisting/liquidation/managed/alert).
7. Correction handling (flag + force manual review; no full linkage).
8. Defect ledger (10 enumerated defect classes).
9. Gate status update.

## Required outputs (12)

1. `parser_reopen_referee_lock.md` (this file)
2. `parser_input_sample_plan.csv`
3. `html_inline_parser_design.md`
4. `parser_output_schema.md`
5. `parser_validation_results.csv`
6. `parser_validation_summary.md`
7. `negative_control_results.md`
8. `correction_handling_status.md`
9. `parser_defect_ledger.csv`
10. `parser_gate_status.md`
11. `parser_final_summary.md`
12. `downstream_blockers_after_parser_reopen.md`

## Allowed code artifacts

- `src/parsers/` parser module — suspension/resumption HTML-inline only.
- `tests/` parser unit tests.
- `src/audit/measurement_a0/` sample validation script.
- NO strategy code. NO performance code. NO execution simulation wiring.
- NO C2/C3 wiring. NO production / paper / P08 / live code modification.

## Hard prohibitions

(Standard hard locks; see `docs/next_actions.md`.)

## Important boundary

- Narrow parser reopen.
- Passing this phase does NOT reopen strategy testing.
- Passing this phase does NOT open execution simulation automatically.
- Passing this phase does NOT complete S2 globally.
- Passing this phase only validates whether HTML-inline parser can extract
  suspension / resumption effective dates.

## End condition

- Return S2 HTML-inline parser reopen report only.
- Referee will decide whether to:
  - A. close as HTML-inline parser validated for suspension / resumption,
  - B. require another parser pass,
  - C. open correction-linkage A0,
  - D. open delisting / liquidation manual expansion,
  - E. keep all strategy research closed.
