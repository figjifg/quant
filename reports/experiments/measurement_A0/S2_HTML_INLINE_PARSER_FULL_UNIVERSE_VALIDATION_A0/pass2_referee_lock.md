# S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0 — Pass 2 Referee Lock

Date: 2026-05-25
Verdict source: Referee verdict opening Pass 2, 2026-05-25.
Pass 1 commit: `20fbdf6` (accepted as evidence; phase NOT closed).

## State

**PASS 2 REQUIRED / FULL_UNIVERSE_VALIDATION_REQUIRES_MORE_WORK** — Pass 1 found
0 negative-control false positives but 20 wrong_date defects in holdout, all
`period_change_disclosure`. Targeted fix + revalidation required.

## Pass-2 scope

- Measurement-layer full-universe parser validation only.
- suspension_related + resumption_related only.
- HTML-inline body only.
- Allowed parser feature change: `period_change_disclosure` after-change period
  selection ONLY. No other parser feature expansion.

## Pass-2 levers

- Patch `src/parsers/krx_status_html_inline.py`:
  - Add `PERIOD_CHANGE_RE` (detects `기간변경` in report_nm).
  - Add `select_after_change_period_hit()` helper using body markers
    `변경전 / 변경 전 / 정정전 / 정정 전 / 당초` (before) and
    `변경후 / 변경 후 / 정정후 / 정정 후 / 변경된 / 정정된` (after).
  - In `suspension_related` branch: if report_nm contains `기간변경`, prefer
    after-change period.
- Parser version bumped 1.0.0 → 1.1.0.
- 8 new unit tests (34 total / 34 passing).

## Pass-2 outputs (12)

1. `pass2_referee_lock.md` (this file)
2. `pass2_period_change_parser_fix.md`
3. `pass2_unit_test_summary.md`
4. `pass2_full_universe_parser_outputs.csv`
5. `pass2_parse_coverage_summary.md`
6. `pass2_negative_control_check.md`
7. `pass2_correction_policy_check.md`
8. `pass2_holdout_validation_sample.csv`
9. `pass2_holdout_validation_summary.md`
10. `pass2_defect_delta.csv`
11. `pass2_gate_status.md`
12. `pass2_final_summary.md`

## Pass-2 pass-criteria

- All / most 20 Pass-1 wrong_date period_change rows corrected.
- No material new wrong_date / false_positive introduced.
- Negative-control FP remain 0.
- Correction-flagged rows still forced to manual review.
- Pass-3 high_validated-only correction policy unchanged.
- Gate status explicitly stated.

## Pass-2 gate enum (Referee-permitted)

- `FULL_UNIVERSE_VALIDATED_FOR_SUSPENSION_RESUMPTION_ONLY`
- `FULL_UNIVERSE_VALIDATION_REQUIRES_MORE_WORK`
- `FULL_UNIVERSE_PARSER_APPLIED_BUT_NOT_VALIDATED`
- `PARTIAL`
- `DATA_SOURCE_FAIL`
- `READY_FOR_NEXT_A0_REVIEW`

## Pass-1 artifacts preserved

Pass-1 outputs (12) remain untouched.

## Hard prohibitions

(Unchanged. See `docs/next_actions.md`.)
