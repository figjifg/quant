# Calendar Reconciliation Summary

Date: 2026-05-24  
Phase: KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0

## Headline

- Acquired official calendar: **4034** dates
- Repo union working calendar: **4022** dates
- Total unique dates compared: **4034**
- Matched: **4022**
- Official-only (present in official, absent in repo union): **12**
- Repo-only (present in repo union, absent in official): **0**

## Subset gap (within official calendar)

- Missing in panel union (official date with no panel row): **12**
- Missing in market_flow union: **12**
- Missing in S1 adjusted OHLC (2018+ scope only): **12**

## Anomaly ledger rows: **12**

Per `calendar_reconciliation_ledger.csv` (full per-date classification) and
`calendar_anomaly_ledger.csv` (non-matched rows only).

## Interpretation

Cases where official ⊃ repo union are typically due to vendor panel coverage
filters (e.g., dynamic Top100 selection excluding small caps on a given day).
Cases where repo union ⊃ official are suspect — they may represent panel
artifacts (vendor-only rows where Samsung 005930 was halted but the panel still
has rows for other tickers). These flow into the anomaly ledger.

## Hard locks (preserved)

- No execution simulation.
- No strategy test.
- No performance metric.
