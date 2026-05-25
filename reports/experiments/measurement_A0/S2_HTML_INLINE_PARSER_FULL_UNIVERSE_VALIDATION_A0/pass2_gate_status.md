# Pass-2 Gate Status

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0 (Pass 2)

## Gate state: **READY_FOR_NEXT_A0_REVIEW**

### Rationale

Pass-2 holdout success 99.4% ≥ 90%; period_change fix rate 95.0% (19/20 revisits corrected); FP=0; correction policy unchanged; wrong+missed=1.

## Permitted enum (Referee-fixed)

- `FULL_UNIVERSE_VALIDATED_FOR_SUSPENSION_RESUMPTION_ONLY`
- `FULL_UNIVERSE_VALIDATION_REQUIRES_MORE_WORK`
- `FULL_UNIVERSE_PARSER_APPLIED_BUT_NOT_VALIDATED`
- `PARTIAL`
- `DATA_SOURCE_FAIL`
- `READY_FOR_NEXT_A0_REVIEW`

## Numerical inputs

| metric | Pass 1 | Pass 2 |
|---|---:|---:|
| universe | 17924 | 17924 |
| in-scope rows parsed | 12,187 | 12187 |
| extracted | 1327 | 1331 |
| period_change rows in universe | (not tracked) | 3030 |
| period_change rows taking 1.1.0 path | n/a | 320 |
| negative-control FP | 0 | 0 |
| correction high_validated (allowed) | 35 | 35 |
| correction blocked to manual review | 131 | 131 |
| holdout sample | 184 | 180 |
| holdout success rate | 89.1% | 99.4% |
| holdout FP | 0 | 0 |
| holdout wrong_date | 20 | 1 |
| holdout missed_date | 0 | 0 |
| holdout correction_not_forced_manual_review | 0 | 0 |
| Pass-1 wrong rows revisited | n/a | 20 |
| Pass-1 wrong rows now correct | n/a | 19 |
| Pass-1 wrong rows still wrong | n/a | 1 |
| period_change fix rate | n/a | 95.0% |
| defect delta rows | n/a | 23 |

## Important boundary

- Execution simulation is NOT opened.
- Strategy testing is NOT opened.
- Performance diagnostics is NOT opened.
- No card is strategy-ready.
- Parser scope unchanged beyond the 1.1.0 period_change_disclosure fix.
