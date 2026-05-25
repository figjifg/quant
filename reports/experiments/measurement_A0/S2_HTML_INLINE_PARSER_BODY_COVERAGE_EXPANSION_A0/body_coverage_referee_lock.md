# S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0 — Referee Lock

Date: 2026-05-25  
Verdict source: Referee verdict opening this phase, 2026-05-25.  
Predecessor: `S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0` CLOSED (close-
housekeeping commit `5e7caec`; Pass 1 `20fbdf6` + Pass 2 `38acaf9`).

## Scope (Referee-fixed)

- Measurement-layer body-coverage expansion A0 only.
- Increase OPENDART document.xml body availability for in-scope status disclosures.
- Initial scope limited to:
  - `suspension_related`
  - `resumption_related`
  - HTML-inline body candidates
  - `body_unavailable` rows from
    `S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0`.
- Use the already validated parser version `krx_status_html_inline-1.1.0` only
  for coverage measurement.
- No new parser feature expansion.
- No delisting / liquidation / managed / alert parser.
- No DART body alpha. No overhang.
- No all-event event log / C2/C3 wiring.
- No strategy testing / performance / execution sim.
- No production / paper / P08 / live / shadow.

## Allowed tasks (9)

1. Body-unavailable target universe construction (from prior full-universe outputs).
2. Prior cache inventory (count cached ZIPs, valid vs unparseable, in-scope hits).
3. Coverage expansion plan with priority buckets P0-P5.
4. Controlled OPENDART body acquisition with throttling + error taxonomy
   (`download_success` / `api_no_document` / `zip_unparseable` / `html_inline` /
   `structured_xml` / `attachment_only` / `unavailable` / `retry_needed` /
   `rate_limited` / `credential_or_api_error`).
5. Re-apply parser 1.1.0 to newly available bodies.
6. Body coverage delta metrics (before vs after; suspension/resumption split;
   pre/post-2018 split; correction split; priority bucket split).
7. Validation sample on newly acquired bodies.
8. Defect ledger.
9. Coverage gate status update.

## Required outputs (12)

1. `body_coverage_referee_lock.md` (this file)
2. `body_unavailable_target_universe.csv`
3. `cache_inventory_summary.md`
4. `body_acquisition_plan.md`
5. `body_acquisition_attempt_log.csv`
6. `body_coverage_delta_summary.md`
7. `post_acquisition_parser_outputs.csv`
8. `new_body_validation_sample.csv`
9. `new_body_validation_summary.md`
10. `body_coverage_defect_ledger.csv`
11. `body_coverage_gate_status.md`
12. `body_coverage_final_summary.md`

## Gate enum (Referee-permitted)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `BODY_COVERAGE_EXPANDED_BUT_INCOMPLETE`
- `BODY_COVERAGE_EXPANDED_AND_VALIDATED_FOR_AVAILABLE_ROWS`
- `BODY_COVERAGE_REQUIRES_MORE_WORK`
- `READY_FOR_NEXT_A0_REVIEW`

## Pass-criteria

- Body-unavailable target universe documented.
- Existing cache inventoried.
- Acquisition attempt log produced.
- Coverage before vs after quantified.
- Newly acquired bodies parsed with existing parser only.
- New body validation sample completed (or infeasibility documented).
- `body_unavailable` remaining preserved (not silently dropped).
- Defect ledger produced.
- Gate status explicitly stated.
- No strategy test / execution sim / performance metric produced.

## Fail / partial gates

- Acquisition cannot run → DATA_SOURCE_FAIL or PARTIAL.
- Body coverage improves only marginally → PARTIAL or REQUIRES_MORE_WORK.
- Many attachment-only / unavailable → PARTIAL with source-limitation note.
- Parser behavior regresses on new bodies → REQUIRES_MORE_WORK.
- Correction policy violated → FAIL.
- `body_unavailable` dropped or treated as safe → FAIL.
- `rcept_dt` used as effective_date fallback → FAIL.
- Any strategy metric → protocol violation.

## Hard prohibitions

(Unchanged. See `docs/next_actions.md`.)

## Important boundary

- Body-coverage expansion, NOT parser expansion.
- Passing this phase does NOT reopen strategy testing.
- Passing this phase does NOT open execution simulation automatically.
- Passing this phase does NOT complete S2 globally.

## End condition

- Return body-coverage expansion A0 report only.
- Referee will decide whether to:
  - A. close as body coverage expanded,
  - B. require another coverage pass,
  - C. open correction-linkage full-universe validation,
  - D. open delisting / liquidation manual expansion,
  - E. keep all strategy research closed.
