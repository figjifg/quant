# Listed-Universe Source Inventory

Date: 2026-05-24  
Phase: KR-LISTED-UNIVERSE-COVERAGE-A0

## Sources surveyed

| source_id | role | market | id_cols | listing field | delisting field | provenance | limitations |
|---|---|---|---|---|---|---|---|
| `krx_monthly_snapshots_pykrx` | official (monthly resolution) | KOSPI + KOSDAQ | ticker, market, snapshot_date | first_seen_in_snapshots (derived) | last_seen_in_snapshots (derived; precision = ±1 month) | pykrx stock.get_market_ticker_list with KRX_ID auth — acquired in this phase | monthly granularity; delisting/listing date precision ±1 month; KONEX not included |
| `s4_krx_listed_companies_master` | 5-snapshot sample (partial) | KOSPI + KOSDAQ | snapshot_date, ticker, market, name | snapshot_date (not actual listing date) | absent | Round 4 S4 acquisition via pykrx (5 sample dates) | only 5 snapshot dates — too sparse to be a continuous source |
| `s4_krx_ever_listed_table` | 5-snapshot union | KOSPI + KOSDAQ | ticker | first_snapshot (not actual listing date) | last_snapshot (not actual delisting date) | Round 4 S4 acquisition (5 sample union) | sample-only; first/last_snapshot dates are sample bookends, not real listing/delisting dates |
| `w001_v2_permanent_id_master` | derived identity resolution | panel tickers + DART corp_code matches | ticker, permanent_id, permanent_id_source, corp_code_dart | krx_first_snapshot (NOT actual listing date — sample bookend) | krx_last_snapshot (NOT actual delisting date — sample bookend) | W001 v2 derivation from S4 + DART corp_code mapping | lifecycle dates are sample bookends; KRX_TICKER_xxxxxx fallback IDs are temporary |
| `w001_v2_listing_status_events` | DART-derived status events | tickers with DART events | ticker, rcept_dt, category, rcept_no | absent | category=delisting + rcept_dt | OPENDART pblntfty=I filtered (S3) | filtered from pblntfty=I disclosures; 53.1% coverage of disappeared tickers per ACQUISITION_SUMMARY.md |
| `w001_v2_listing_status_terminal` | derived terminal status | panel tickers with terminal events | ticker, terminal_status, terminal_date | absent | terminal_date | W001 v2 derivation from listing_status_events | covers only DART-flagged terminal events; 47% of historic disappearances unresolved |
| `equity_panel_kiwoom_2010_2016` | vendor dynamic_top100 selection | Top 100 by liquidity per day; KOSPI+KOSDAQ mix | 날짜, 종목코드 | first row appearance (not actual listing date — selection-bias) | absent | Kiwoom vendor | selection bias; not survivorship-safe; current and prior top 100 only |
| `equity_panel_dynamic_top100_2017_2024` | vendor dynamic_top100 | Top 100 by liquidity per day | 날짜, 종목코드 | first appearance (selection-bias) | absent | Kiwoom vendor | selection bias; not survivorship-safe |
| `equity_panel_dynamic_top100_2018_2024` | vendor dynamic_top100 | Top 100 by liquidity per day | 날짜, 종목코드 | first appearance (selection-bias) | absent | Kiwoom vendor | selection bias |
| `equity_panel_krx_2025_2026` | KRX-tagged dynamic_top100 | Top 100 by liquidity per day; post-NXT | 날짜, 종목코드 | first appearance (selection-bias) | absent | KRX integrated panel | selection bias |

## Newly acquired in this phase

- `krx_monthly_snapshots_pykrx` — monthly first-trading-day snapshots of
  `pykrx.stock.get_market_ticker_list` for KOSPI + KOSDAQ, 2010-01 → 2026-05.
  Requires KRX_ID/KRX_PW (user-owned credentials, loaded from local .env, NOT
  committed). Monthly granularity is sufficient to detect listing/delisting
  to within ±1 month; refinement to daily resolution is a future-phase option.

## Sources NOT in this phase's scope

- KONEX market (excluded from this audit).
- ETF/ETN universe (separate inventory).
- Pre-2010 listings (out of audit window).
- Intraday halt / shortened session metadata (in `KR-EXECUTABLE-STATUS-BACKLOG`).
