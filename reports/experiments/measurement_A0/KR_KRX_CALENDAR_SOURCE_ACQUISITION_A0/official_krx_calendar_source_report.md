# Official KRX Calendar Source Report

Date: 2026-05-24  
Phase: KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0

## Acquired source

- Method: `composite_pykrx_005930_plus_market_flow_secondary`
- API: `pykrx.stock.get_market_ohlcv` (anonymous KRX endpoint via pykrx).
- Ticker used: **005930 (Samsung Electronics)** — most liquid KRX stock with
  continuous listing throughout 2010-present. Its OHLCV row dates equal the
  KRX trading-day calendar for any actively traded period (Samsung had no
  multi-day halts in the audit window).
- Date range: **2010-01-04 → 2026-05-22** (4034 dates).
- Storage: `data/acquired/krx_calendar/krx_official_calendar_2010_2026.csv`

## Why this is the best available source

Alternatives considered:

| candidate | status | reason |
|---|---|---|
| pykrx `get_index_ohlcv` (KOSPI 1001) | FAIL on this pykrx version | index_ticker_name lookup error in installed pykrx |
| pykrx `get_previous_business_days` | FAIL | API signature mismatch in installed pykrx |
| pykrx `get_market_ohlcv('005930')` | **PASS** | anonymous-accessible, full date range coverage |
| KRX `getJsonData.cmd` direct call | not attempted in this audit phase; would need separate scope |
| KRX 정보데이터시스템 휴장일 endpoint | not attempted in this audit phase |
| Existing market_flow `_krx_trading_days` files | secondary reference only — file name tagged but provenance not authoritative |

## Limitations

Composite calendar. Layer 1 = pykrx Samsung 005930 OHLCV (authoritative, covers 2014-03-03 → today; anonymous endpoint truncates pre-2014 even with KRX auth). Layer 2 = market_flow_2010_2017_krx_trading_days.csv (file-name-tagged KRX trading days, used ONLY for pre-Layer-1 gap fill per Referee-permitted secondary reference). Each date carries a `source` provenance tag.

**Specific caveats**:

- Samsung 005930 was suspended on rare occasions in its history (e.g., dividend
  record cuts, share-class events). On those days, KRX would still be open but
  Samsung's OHLCV row may be absent. The resulting calendar may UNDER-count by
  a small number of dates. Reconciliation flags these as `official_only_date`
  candidates if other sources show data.
- The 2010-12-31 / 1999-2009 era pre-conditioning is OUT OF SCOPE here.
- Calendar covers KRX (KOSPI + KOSDAQ unified — Samsung is KOSPI but its
  trading days match the unified market schedule).
- No 휴장일 / 특별 거래시간 metadata (start-of-day delay, etc.) is captured.
  Only date-level resolution.

## Storage policy

The calendar file lives at `data/acquired/krx_calendar/krx_official_calendar_2010_2026.csv`
locally. The `data/acquired/` directory is gitignored per repo data-hygiene policy, so
the raw calendar CSV is NOT tracked in git. Reproduction is by re-running
`src/audit/measurement_a0/p_krx_calendar_acquisition.py`, which detects the cached
file and reuses it when present (otherwise re-acquires via pykrx). Provenance metadata
(source method, date range, fetched_at, limitations) IS tracked in
`acquired_calendar_inventory.csv` in this report directory.

## Provenance record

Each acquired calendar artefact carries:
- `source_method`
- `endpoint`
- `ticker_used`
- `fetched_at` (ISO timestamp)
- `storage_path`
- `limitations`

These are preserved in `acquired_calendar_inventory.csv`.

## Hard locks (preserved)

- No credential committed.
- No API key printed.
- No execution simulation run.
- No strategy testing performed.
