# Pass-2 Gate Status

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0 (Pass 2)

## Gate state: **CORRECTION_LINKAGE_REQUIRES_MORE_WORK**

### Rationale

pass-2 link rate 55.1% improves but still below 60% bar; additional work needed.

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
| pass-1 no_link count | 123 |
| pass-2 no_link count (after expansion) | 70 |
| no_link reduction | 53 |
| pass-2 candidates by confidence — high | 36 |
| pass-2 candidates by confidence — medium | 42 |
| pass-2 candidates by confidence — low | 18 |
| pass-2 candidates cross-category | 7 |
| pass-2 manual sample size | 80 |
| pass-2 linked_unambiguous + linked_likely | 43 |
| pass-2 eligible (n − no_original_found) | 78 |
| pass-2 sample link rate | 55.1% |
| pass-2 wrong-candidate risk flagged | 12 |

## Window sensitivity (pass-2)

| window (days) | corrections-with-any-candidate | high | medium | low | no_link |
|---:|---:|---:|---:|---:|---:|
| 30 | 77 | 30 | 22 | 14 | 100 |
| 90 | 93 | 29 | 33 | 19 | 85 |
| 180 | 100 | 30 | 35 | 22 | 79 |
| 365 | 111 | 36 | 42 | 18 | 70 |
| 730 | 122 | 37 | 48 | 21 | 60 |

## Important boundary

- Execution simulation is NOT opened.
- Strategy testing is NOT opened.
- Performance diagnostics is NOT opened.
- No card is strategy-ready.
- Supersession remains design-only.
- Parser behaviour on correction rows unchanged (still forces manual review).
