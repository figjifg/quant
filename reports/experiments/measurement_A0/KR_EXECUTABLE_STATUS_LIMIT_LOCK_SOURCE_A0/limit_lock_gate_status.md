# Limit-Lock Gate Status

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0

## Gate state: **PARTIAL**

### Rationale

no direct KRX daily limit-lock log available in repo or via pykrx; this phase derives a semi-official candidate set via KRX historical price-limit rule (2 matched + 334 rule-only candidates vs 39 repo-only candidates). Result is candidate-only; close-at-limit vs locked is NOT distinguishable from daily data. Execution simulation stays CLOSED.

## Permitted enum (Referee-fixed)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `OFFICIAL_SOURCE_ACQUIRED_BUT_NOT_FULLY_RECONCILED`
- `LIMIT_LOCK_SOURCE_RECONCILED_BUT_EXECUTION_STILL_CLOSED`
- `READY_FOR_NEXT_A0_REVIEW`

## Numerical inputs

| metric | value |
|---|---:|
| Matched (W001 + rule agree) | 2 |
| Rule-only candidates | 334 |
| W001-only candidates (no rule support) | 39 |
| Total defects | 9 |
| Limit candidates overlapping invalid OHLCV / suspension states | 206 |

## Important boundary

- Execution simulation is NOT opened.
- Strategy testing is NOT opened.
- Limit candidate label remains `candidate_proxy_only` / `semi_official_rule_derived`.
- Close-at-limit vs locked is NOT distinguishable from daily data.
