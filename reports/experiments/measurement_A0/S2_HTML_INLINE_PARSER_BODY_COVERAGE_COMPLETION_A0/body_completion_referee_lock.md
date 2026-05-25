# S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0 — Referee Lock

Date: 2026-05-25  
Verdict source: Referee verdict opening this phase, 2026-05-25.  
Predecessor: `S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0` CLOSED (commit
`0d48ba4`; initial pass `1d8a67f`).

## Scope (Referee-fixed)

- Measurement-layer body-coverage completion A0 only.
- Attempt the remaining body_unavailable rows from the prior expansion phase.
- Initial scope limited to:
  - `suspension_related`
  - `resumption_related`
  - HTML-inline body candidates
  - remaining body_unavailable rows only.
- Parser `krx_status_html_inline-1.1.0` used as-is.
- No new parser feature expansion.
- No delisting / liquidation / managed / alert parser.
- No DART body alpha. No overhang.
- No all-event event log / C2/C3 wiring.
- No strategy testing / performance / execution sim.
- No production / paper / P08 / live / shadow.

## Allowed tasks (10)

1. Remaining target universe construction.
2. Cache re-inventory.
3. Completion acquisition plan.
4. Controlled OPENDART download with full error taxonomy.
5. Re-apply parser 1.1.0 to newly available bodies.
6. Completion coverage metrics.
7. Validation sample on newly acquired completion bodies.
8. Residual body_unavailable classification.
9. Defect ledger.
10. Gate status update.

## Required outputs (13)

1. `body_completion_referee_lock.md` (this file)
2. `remaining_body_unavailable_target.csv`
3. `cache_reinventory_summary.md`
4. `completion_acquisition_plan.md`
5. `completion_acquisition_attempt_log.csv`
6. `completion_coverage_delta_summary.md`
7. `completion_parser_outputs.csv`
8. `completion_validation_sample.csv`
9. `completion_validation_summary.md`
10. `residual_body_unavailable_classification.csv`
11. `body_completion_defect_ledger.csv`
12. `body_completion_gate_status.md`
13. `body_completion_final_summary.md`

## Gate enum (Referee-permitted)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `BODY_COVERAGE_COMPLETED_WITH_RESIDUALS`
- `BODY_COVERAGE_COMPLETED_AND_VALIDATED_FOR_AVAILABLE_ROWS`
- `BODY_COVERAGE_REQUIRES_MORE_WORK`
- `READY_FOR_NEXT_A0_REVIEW`

## Pass-criteria

- Remaining body_unavailable target universe documented.
- Cache re-inventoried.
- Completion acquisition attempt log produced.
- Coverage before vs after quantified.
- Newly acquired bodies parsed with existing parser only.
- Completion validation sample completed.
- Residual body_unavailable rows explicitly classified.
- body_unavailable remaining preserved (not silently dropped).
- Defect ledger produced.
- Gate status explicitly stated.
- No strategy test / execution sim / performance metric produced.

## Fail / partial gates

- Acquisition cannot run → DATA_SOURCE_FAIL or PARTIAL.
- Many rows remain not_attempted again → REQUIRES_MORE_WORK or PARTIAL.
- Residual mostly source failures → COMPLETED_WITH_RESIDUALS + classify defects.
- Parser regresses on new bodies → REQUIRES_MORE_WORK.
- Correction policy violated → FAIL.
- `body_unavailable` dropped or treated as safe → FAIL.
- `rcept_dt` used as effective_date fallback → FAIL.
- Any strategy metric → protocol violation.

## Hard prohibitions

(Unchanged. See `docs/next_actions.md`.)

## Important boundary

- Body-coverage completion, NOT parser expansion.
- Passing this phase does NOT reopen strategy testing.
- Passing this phase does NOT open execution simulation automatically.
- Passing this phase does NOT complete S2 globally.

## End condition

- Return body-coverage completion A0 report only.
- Referee will decide whether to:
  - A. close as body coverage completed with residuals,
  - B. require another coverage pass,
  - C. open correction-linkage full-universe validation,
  - D. open delisting / liquidation manual expansion,
  - E. keep all strategy research closed.
