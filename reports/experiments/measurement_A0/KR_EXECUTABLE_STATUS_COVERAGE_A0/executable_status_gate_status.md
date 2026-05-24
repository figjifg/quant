# Executable-Status Gate Status

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-COVERAGE-A0

## Gate state: **PARTIAL**

### Rationale

S3 source acquired (semi-official; date-resolution, 2018+ only); 63/10774 events matched against W001 v2 derivation. Intraday halts, limit-lock authoritative log, and pre-2018 status events are NOT covered. Execution simulation stays CLOSED.

## Permitted enum (Referee-fixed)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `OFFICIAL_SOURCE_ACQUIRED_BUT_NOT_FULLY_RECONCILED`
- `EXECUTABLE_STATUS_RECONCILED_BUT_EXECUTION_STILL_CLOSED`
- `READY_FOR_NEXT_A0_REVIEW`

## Numerical inputs

| metric | value |
|---|---:|
| S3 events reconciled | 10774 |
| Matched (W001 v2 agrees with S3) | 63 |
| Official-status-but-panel-absent | 9551 |
| Official-vs-repo disagreement (high severity) | 0 |
| Total defects | 4 |

## Important boundary

- Strategy testing is NOT opened.
- Execution simulation is NOT opened.
- No executable claim from panel presence.
- Intraday halt + limit-lock authoritative coverage MISSING.
- Pre-2018 status coverage MISSING.
