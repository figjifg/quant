# Pre-2018 Executable-Status Source Report

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0

## Acquired source

- Endpoint: OPENDART `list.json` pblntfty=I (거래소공시).
- Date range: **20100104 → 20171228**.
- Raw rows: **300829**.
- Filtered status events: **7150**.
- Storage: `data/acquired/round5_dart_pre2018/` (gitignored; reproducible via build script).

## Category distribution (filtered status events)

| category | count |
|---|---:|
| `suspension_related` | 3211 |
| `resumption_related` | 2058 |
| `delisting` | 1683 |
| `managed` | 178 |
| `short_term_overheated` | 10 |
| `investment_alert` | 8 |
| `liquidation` | 2 |

## Coverage vs the Round-4 S3 baseline

- Round 4 S3 acquisition: 425,294 raw / 10,774 filtered (2018-2026).
- This phase pre-2018: 300829 raw / 7150 filtered (2010-2017).
- Combined post-2010 baseline now available for reconciliation against the
  2010-2017 equity panels.

## Limitations

- Same as Round 4 S3: rcept_dt = filing date, not always status effective date.
- DART body parsing remains PARTIAL (S2 phase closed PARTIAL); exact effective
  dates may differ from rcept_dt.
- Intraday halts NOT captured.
- Limit-lock authoritative log NOT captured.
- Effective status duration NOT captured at date level.

## Hard locks (preserved)

- No credential committed.
- No execution simulation.
- No strategy testing.
- This source does NOT certify execution feasibility for any specific date.
