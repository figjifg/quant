# Execution-Simulation Gate Status

Date: 2026-05-24  
Phase: KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0

## Gate state: **CALENDAR_SOURCE_RECONCILED_BUT_EXECUTION_STILL_CLOSED**

### Rationale

acquired official calendar reconciled against repo union with small residuals (0 t+1 mismatches, 12 official-only, 0 repo-only); execution simulation remains CLOSED pending separate Referee verdict

## Numerical inputs

| metric | value |
|---|---:|
| t+1 next-day matches | 4021 |
| t+1 next-day mismatches | 0 |
| official-only dates | 12 |
| repo-only dates | 0 |
| anomaly rows | 12 |

## What this gate state means

Per Referee-permitted enum, allowed gate states are:

- `CLOSED`
- `PARTIAL`
- `CALENDAR_SOURCE_ACQUIRED_BUT_NOT_FULLY_RECONCILED`
- `CALENDAR_SOURCE_RECONCILED_BUT_EXECUTION_STILL_CLOSED`
- `READY_FOR_NEXT_A0_REVIEW`

**Execution simulation is NOT opened.** **Strategy testing is NOT opened.**
Whatever gate state this phase reports, it does not authorise any value-
bearing pipeline to run.

## Hard locks (preserved)

- No execution simulation.
- No strategy test.
- No production / paper / P08 / live readiness.
