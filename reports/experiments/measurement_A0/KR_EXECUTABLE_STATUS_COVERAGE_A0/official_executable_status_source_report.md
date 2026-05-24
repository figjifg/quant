# Official Executable-Status Source Report

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-COVERAGE-A0

## Acquired source

- Primary semi-official source: `data/acquired/round4/s3_krx_status/krx_status_events_2018_2026.csv`
- Method: OPENDART list.json filtered to `pblntfty=I` (거래소공시) reports with status-relevant `report_nm` patterns (S3 acquisition, Round 4)
- Date range: **2018-01-02 → 2026-05-06**
- Row count: **10774**
- Unique tickers: **1855**

## Category distribution

| category | event count |
|---|---:|
| `suspension_related` | 4978 |
| `delisting` | 2790 |
| `resumption_related` | 1940 |
| `other` | 762 |
| `managed` | 290 |
| `investment_alert` | 13 |
| `liquidation` | 1 |

## Per-year coverage

| year | event count |
|---|---:|
| 2018 | 905 |
| 2019 | 1045 |
| 2020 | 1346 |
| 2021 | 1507 |
| 2022 | 1342 |
| 2023 | 1115 |
| 2024 | 1250 |
| 2025 | 1459 |
| 2026 | 805 |

## What this source covers

- KRX/KOSDAQ market authority disclosures filed via DART (pblntfty=I = 거래소공시).
- Date-level granularity (filing date = rcept_dt).
- Suspension / resumption / delisting / managed / liquidation /
  investment-alert / short-term-overheated event types.

## What this source does NOT cover

- Intraday halts (no time-of-day resolution).
- Limit-lock (upper/lower limit closes) — only OHLCV proxy available.
- Pre-2018 events (S3 acquisition window starts 2018).
- Effective dates of events (rcept_dt is filing date; actual suspension
  start/end may differ; S2 body parse needed for exact dates and S2 is
  CLOSED AS PARTIAL).
- KONEX market (excluded by corp_cls filter).

## Hard locks (preserved)

- No credential committed.
- No strategy testing.
- No execution simulation.
- This source does NOT certify execution feasibility for any specific date.
