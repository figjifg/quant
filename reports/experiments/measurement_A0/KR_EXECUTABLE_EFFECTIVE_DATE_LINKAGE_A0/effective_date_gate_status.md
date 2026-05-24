# Effective-Date Linkage Gate Status

Date: 2026-05-25  
Phase: KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0

## Gate state: **PARTIAL**

### Rationale

sample audit ran but extraction rate (1.8%) is too low for any generalisation

## Permitted enum (Referee-fixed)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `EFFECTIVE_DATE_SAMPLE_AUDITED_BUT_NOT_GENERALIZED`
- `EFFECTIVE_DATE_LINKAGE_RULES_DEFINED_BUT_EXECUTION_STILL_CLOSED`
- `READY_FOR_NEXT_A0_REVIEW`

## Numerical inputs

| metric | value |
|---|---:|
| samples audited | 113 |
| extraction rate | 1.8% |
| total defects | 5 |

## Important boundary

- Strategy testing is NOT opened.
- Execution simulation is NOT opened.
- `rcept_dt` is NOT promoted to effective_date.
- Future use requires explicit body-extracted dates OR fail-closed defaults.
