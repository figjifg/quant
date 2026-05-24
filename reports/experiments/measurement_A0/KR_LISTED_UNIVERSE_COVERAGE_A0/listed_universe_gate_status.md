# Listed-Universe Gate Status

Date: 2026-05-24  
Phase: KR-LISTED-UNIVERSE-COVERAGE-A0

## Gate state: **PARTIAL**

### Rationale

official universe acquired (monthly resolution) and reconciled against repo panels, but coverage gaps are substantial: panel is materially survivor-biased (2728 official-only tickers absent from panel), and 519 tickers disappeared without a terminal event. Strategy work remains CLOSED.

## Permitted enum (Referee-fixed)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `OFFICIAL_SOURCE_ACQUIRED_BUT_NOT_FULLY_RECONCILED`
- `LISTED_UNIVERSE_RECONCILED_BUT_STRATEGY_STILL_CLOSED`
- `READY_FOR_NEXT_A0_REVIEW`

## Numerical inputs

| metric | value |
|---|---:|
| Official universe size | 3653 |
| Union panel size | 925 |
| Matched | 925 |
| Panel-only | 0 |
| Official-only | 2728 |
| Disappeared without terminal | 519 |
| Total defects | 519 |

## Important boundary

- Strategy testing is NOT opened.
- Execution simulation is NOT opened.
- Survivorship-safe claim is NOT made (see `survivorship_safety_assessment.md`).
