# Official Listed-Universe Source Report

Date: 2026-05-24  
Phase: KR-LISTED-UNIVERSE-COVERAGE-A0

## Acquired source

- Method: pykrx `get_market_ticker_list` per (date, market)
- Endpoint: KRX via pykrx with KRX_ID auth
- Granularity: **monthly** (first trading day of each month)
- Date range: **2010-01-04 → 2026-05-04**
- Snapshot count: **197**
- Markets: KOSPI + KOSDAQ
- Unique tickers ever seen: **3653**
  - KOSPI: 1249
  - KOSDAQ: 2426
- Storage: `data/acquired/krx_listed_universe/krx_listed_monthly_snapshots_2010_2026.csv` (gitignored)

## Why this is the best available source

- pykrx `get_market_ticker_list(date)` returns the exact list of tickers KRX
  considered listed on that date. With KRX_ID auth this works back to 2010.
- This is the **closest to authoritative** for daily listed-universe.
- Monthly granularity is a conservative compromise (~204 snapshots vs ~4000
  daily) — it detects listing/delisting to within ±1 month, which is
  sufficient for survivorship-safety audit but NOT for execution-day
  precision (separate executable-status phase).

## Limitations

- Monthly granularity (±1 month precision on listing/delisting dates).
- KONEX excluded.
- Does not include corporate-action linkage (merger/split target ticker),
  rename history, or ticker reuse mapping.
- Pre-2010 out of scope.
- Intraday halts / shortened sessions not captured (separate phase).

## Hard locks (preserved)

- No credential committed.
- No survivorship-safe claim made here — see `survivorship_safety_assessment.md`.
- No execution simulation run.
- No strategy testing.
