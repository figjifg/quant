# Correction Universe Summary

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0

## Universe construction

Combined 2010+ KRX exchange-status event universe from:
- post-2018 S3: `data/acquired/round4/s3_krx_status/krx_status_events_2018_2026.csv`
- pre-2018 OPENDART: `data/acquired/round5_dart_pre2018/krx_status_events_2010_2017.csv`

Correction-flag detection regex (per parser):
`[기재정정] | [첨부정정] | [첨부추가] | [변경] | [정정]`

## Total events: **17924**
## Correction-flagged events: **538**

## Correction-marker breakdown (all categories)

| marker | count |
|---|---:|
| `[기재정정]` | 534 |
| `[첨부추가]` | 2 |
| `[첨부정정]` | 2 |

## Correction-flagged by event_category

| category | count |
|---|---:|
| `delisting` | 272 |
| `suspension_related` | 115 |
| `other` | 88 |
| `resumption_related` | 51 |
| `managed` | 12 |

## Correction-flagged by period

| period | count |
|---|---:|
| `post_2018` | 372 |
| `pre_2018` | 166 |

## In-scope correction subset (suspension_related + resumption_related): **166**

| period | count |
|---|---:|
| `pre_2018` | 81 |
| `post_2018` | 85 |

## Out-of-scope corrections (not addressed in this phase)

Delisting / liquidation / managed / investment_alert / short_term_overheated /
other categories — out of scope. They remain manual_review_required and are NOT
linkage-validated by this phase.
