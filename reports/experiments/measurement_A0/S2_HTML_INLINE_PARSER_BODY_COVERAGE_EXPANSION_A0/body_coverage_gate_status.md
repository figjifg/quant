# Body-Coverage Gate Status

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0

## Gate state: **READY_FOR_NEXT_A0_REVIEW**

### Rationale

acquired 4996 bodies; coverage shift on target rows 46.5%; holdout success 100.0%; wrong+missed=0; parser behavior preserved; correction policy unchanged.

## Permitted enum (Referee-fixed)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `BODY_COVERAGE_EXPANDED_BUT_INCOMPLETE`
- `BODY_COVERAGE_EXPANDED_AND_VALIDATED_FOR_AVAILABLE_ROWS`
- `BODY_COVERAGE_REQUIRES_MORE_WORK`
- `READY_FOR_NEXT_A0_REVIEW`

## Numerical inputs

| metric | value |
|---|---:|
| target body_unavailable rows | 10744 |
| download_success | 4996 |
| html_inline | 4996 |
| structured_xml | 0 |
| attachment_only | 0 |
| zip_unparseable | 4 |
| api_no_document | 0 |
| not_attempted (budget) | 5744 |
| body_available on target (after) | 5000 |
| body_unavailable on target (after) | 5744 |
| coverage shift on target | 46.5% |
| holdout sample | 84 |
| holdout success rate | 100.0% |
| holdout FP | 0 |
| holdout wrong_date | 0 |
| holdout missed_date | 0 |
| holdout correction_not_forced_manual_review | 0 |
| defects | 5748 |

## Important boundary

- Execution simulation is NOT opened.
- Strategy testing is NOT opened.
- Performance diagnostics is NOT opened.
- No card is strategy-ready.
- Parser scope unchanged (1.1.0 used as-is).
- `body_unavailable` rows remaining MUST NOT be treated as parsed or safe.
