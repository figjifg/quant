# Combined Status-Event Universe Summary

Date: 2026-05-25  
Phase: KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0

## Combined universe

- pre-2018 events (round5 OPENDART acquisition): 7150
- post-2018 events (round4 S3 acquisition): 10774
- **Total status events: 17924**
- Correction-flagged ([기재정정] / [첨부정정] / etc.): 538

## By category (combined)

| category | count |
|---|---:|
| `suspension_related` | 8189 |
| `delisting` | 4473 |
| `resumption_related` | 3998 |
| `other` | 762 |
| `managed` | 468 |
| `investment_alert` | 21 |
| `short_term_overheated` | 10 |
| `liquidation` | 3 |

## By category × period

| category | pre_2018 | post_2018 |
|---|---:|---:|
| `delisting` | 1683 | 2790 |
| `investment_alert` | 8 | 13 |
| `liquidation` | 2 | 1 |
| `managed` | 178 | 290 |
| `other` | 0 | 762 |
| `resumption_related` | 2058 | 1940 |
| `short_term_overheated` | 10 | 0 |
| `suspension_related` | 3211 | 4978 |

## Notes

- `other` rows from pre-2018 are pre-filtered out (already excluded in the
  round5 filtered file).
- post-2018 categorisation uses the same regex as round4 S3 and pre-2018.
- correction-flagged events may supersede prior events (handled separately
  in `correction_cancellation_effective_date_check.md`).
