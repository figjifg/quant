# S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0 — Referee Lock

Date: 2026-05-25  
Verdict source: Referee verdict opening this phase, 2026-05-25.  
Predecessors:
- `S2-HTML-INLINE-PARSER-REOPEN-PHASE` CLOSED (commit `03a2dc9`).
- `KR-STATUS-CORRECTION-LINKAGE-A0` CLOSED (housekeeping commit `a5b982e`;
  3-pass cycle 3d09033 / 565f0d3 / 2f890d7).

## Scope (Referee-fixed)

- Measurement-layer full-universe parser validation only.
- Validate the already-built HTML-inline parser across the broader 2010+
  OPENDART/KRX status-event universe.
- Validate only:
  - `suspension_related`
  - `resumption_related`
  - HTML-inline body
  - `effective_date` / `suspension_start` / `suspension_end` / `resumption_date` /
    `resumption_time`
  - Correction handling using the closed `KR-STATUS-CORRECTION-LINKAGE-A0`
    high_validated-only rules.
- No new parser feature expansion unless limited to defect logging.
- No delisting parser / liquidation parser / managed / alert parser.
- No DART body alpha / overhang.
- No C2/C3 wiring / all-event event log.
- No strategy testing / performance diagnostics / execution simulation.
- No production / paper / P08 / live / shadow.

## Executor note on "manual"

"Manual" holdout verification = per-sample executor-side review with BeautifulSoup
text extraction over OPENDART document.xml bodies (as accepted in prior phases).
Stops short of human reviewer.

## Allowed tasks (9)

1. Full status-event universe construction.
2. Full-universe document availability audit.
3. Apply existing parser across full in-scope population.
4. Full-universe parse coverage metrics.
5. Negative-control full-universe check.
6. Correction policy application (apply closed Pass-3 rules).
7. Stratified spot-check / holdout validation sample.
8. Full-universe defect ledger.
9. Gate status update.

## Required outputs (12)

1. `full_universe_referee_lock.md` (this file)
2. `status_event_universe_inventory.md`
3. `document_availability_audit.csv`
4. `full_universe_parser_outputs.csv`
5. `full_universe_parse_coverage_summary.md`
6. `negative_control_full_universe_check.md`
7. `correction_policy_application_summary.md`
8. `holdout_validation_sample.csv`
9. `holdout_validation_summary.md`
10. `full_universe_parser_defect_ledger.csv`
11. `full_universe_gate_status.md`
12. `full_universe_final_summary.md`

## Gate enum (Referee-permitted)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `FULL_UNIVERSE_PARSER_APPLIED_BUT_NOT_VALIDATED`
- `FULL_UNIVERSE_VALIDATED_FOR_SUSPENSION_RESUMPTION_ONLY`
- `FULL_UNIVERSE_VALIDATION_REQUIRES_MORE_WORK`
- `READY_FOR_NEXT_A0_REVIEW`

`READY_FOR_NEXT_A0_REVIEW` requires:
- Parser applied to full in-scope population.
- Negative controls show no material false positives.
- Correction policy correctly blocks non-high_validated rows.
- Holdout validation shows low wrong_date / false_positive risk.
- Correction rows remain non-authoritative.

## Pass-criteria

- Full 2010+ status-event universe inventoried.
- Full in-scope suspension / resumption population identified.
- Existing parser applied to full in-scope population.
- Parse coverage metrics reported.
- Negative controls show no material false positives.
- Correction policy blocks non-high_validated rows from authoritative use.
- Holdout validation sample completed.
- Defect ledger produced.
- Gate status explicitly stated.
- No strategy test / execution sim / performance metric produced.

## Fail / partial gates

- Parser cannot be run on full in-scope population → PARTIAL.
- Document availability poor → PARTIAL.
- Holdout validation shows material wrong_date / FP risk → REQUIRES_MORE_WORK.
- Parser extracts unsupported category dates → REQUIRES_MORE_WORK or FAIL.
- Correction rows bypass manual review → FAIL.
- `rcept_dt` used as `effective_date` fallback → FAIL.
- Parser described as strategy-ready → FAIL.
- Any strategy metric → protocol violation.

## Allowed code artifacts

- Validation script under `src/audit/measurement_a0/`.
- Reuse existing parser module.
- Minor non-functional parser version tagging allowed.
- No parser feature expansion (defects logged but not patched).
- No strategy / performance / execution / C2/C3 / production code.

## Hard prohibitions

(Unchanged. See `docs/next_actions.md`.)

## Important boundary

- Full-universe parser validation, NOT parser expansion.
- Passing this phase does NOT reopen strategy testing.
- Passing this phase does NOT open execution simulation automatically.
- Passing this phase does NOT complete S2 globally.

## End condition

- Return full-universe parser validation report only.
- Referee will decide whether to:
  - A. close as full-universe parser validated for suspension / resumption,
  - B. require another validation pass,
  - C. open correction-linkage full-universe validation,
  - D. open delisting / liquidation manual expansion,
  - E. keep all strategy research closed.
