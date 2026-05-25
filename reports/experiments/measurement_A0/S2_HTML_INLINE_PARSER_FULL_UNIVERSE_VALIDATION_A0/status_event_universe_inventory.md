# Full Status-Event Universe Inventory

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0

## Total events: **17924**

## By event_category

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

## By period

| period | count |
|---|---:|
| `pre_2018` | 7150 |
| `post_2018` | 10774 |

## Identity coverage

| field | count present |
|---|---:|
| stock_code (≠ 000000) | 17912 |
| corp_code (non-empty) | 17924 |

## In-scope vs out-of-scope

- In-scope parser population (suspension + resumption): **12187**.
  - correction-flagged: 166
- Out-of-scope negative-control population (delisting / liquidation / managed /
  alert / short_term_overheated / other): **5737**.

## Out-of-scope breakdown

| category | count |
|---|---:|
| `delisting` | 4473 |
| `liquidation` | 3 |
| `managed` | 468 |
| `investment_alert` | 21 |
| `short_term_overheated` | 10 |
| `other` | 762 |

## Data sources

- pre-2018: `data/acquired/round5_dart_pre2018/krx_status_events_2010_2017.csv`
- post-2018: `data/acquired/round4/s3_krx_status/krx_status_events_2018_2026.csv`
