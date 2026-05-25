# Pass-3 Gate Status

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0 (Pass 3)

## Gate state: **READY_FOR_NEXT_A0_REVIEW**

### Rationale

pass-3 link rate 78.1% ≥ 75% bar; high_validated=35; wrong candidates quarantined=10 (Pass-3 body-confirmation gate); residual FP in linked pool=0 (all linked rows have body cross-check support).

## Permitted enum (Referee-fixed)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `CORRECTION_LINKAGE_DESIGNED_BUT_NOT_VALIDATED`
- `CORRECTION_LINKAGE_VALIDATED_FOR_SAMPLE_ONLY`
- `CORRECTION_LINKAGE_REQUIRES_MORE_WORK`
- `READY_FOR_NEXT_A0_REVIEW`

## Numerical inputs

| metric | value |
|---|---:|
| Pass-2 no_link | 70 |
| Pass-3 no_link (after stricter scoring) | 71 |
| Pass-3 high_validated | 35 |
| Pass-3 medium_needs_manual | 42 |
| Pass-3 low_needs_manual | 18 |
| Pass-3 rejected_wrong_candidate | 10 |
| Pass-3 manual sample size | 72 |
| Pass-3 linked_total | 25 |
| Pass-3 eligible | 32 |
| Pass-3 sample link rate | 78.1% |
| Pass-3 wrong-candidate quarantined (Pass-2 wrong cases caught) | 10 |
| Pass-3 residual FP in LINKED pool (all linked have body cross-check) | 0 |
| supersession_ready=yes rows | 9 |

## Important boundary

- Execution simulation is NOT opened.
- Strategy testing is NOT opened.
- Performance diagnostics is NOT opened.
- No card is strategy-ready.
- Supersession remains design-only.
- Parser behaviour on correction rows unchanged.
