# Full-Universe Validation Gate Status

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0

## Gate state: **FULL_UNIVERSE_VALIDATION_REQUIRES_MORE_WORK**

### Rationale

holdout success rate 89.1% below 85% bar.

## Permitted enum (Referee-fixed)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `FULL_UNIVERSE_PARSER_APPLIED_BUT_NOT_VALIDATED`
- `FULL_UNIVERSE_VALIDATED_FOR_SUSPENSION_RESUMPTION_ONLY`
- `FULL_UNIVERSE_VALIDATION_REQUIRES_MORE_WORK`
- `READY_FOR_NEXT_A0_REVIEW`

## Numerical inputs

| metric | value |
|---|---:|
| total universe | 17924 |
| in-scope (suspension+resumption) | 12187 |
| out-of-scope (negative control) | 5737 |
| in-scope with cached body | 1402 |
| in-scope `body_unavailable` | 10751 |
| in-scope `extracted` | 1327 |
| extraction rate overall | 10.9% |
| extraction rate given body | 94.7% |
| negative-control FP (load-bearing) | 0 |
| negative-control safe (no in-scope field extracted) | 5737 |
| negative-control parse_status=out_of_scope_category | 82 |
| negative-control parse_status=body_unavailable (still safe) | 5650 |
| correction in-scope rows | 166 |
| correction high_validated (allowed) | 35 |
| correction blocked to manual review | 131 |
| holdout sample size | 184 |
| holdout success rate | 89.1% |
| holdout FP | 0 |
| holdout wrong+missed | 20 |
| holdout correction_not_forced_manual_review | 0 |
| holdout body_unavailable | 0 |
| defects | 10846 |

## Important boundary

- Execution simulation is NOT opened.
- Strategy testing is NOT opened.
- Performance diagnostics is NOT opened.
- No card is strategy-ready.
- Parser scope unchanged (suspension/resumption HTML-inline only).
- Correction policy unchanged (high_validated only is design-supported).
