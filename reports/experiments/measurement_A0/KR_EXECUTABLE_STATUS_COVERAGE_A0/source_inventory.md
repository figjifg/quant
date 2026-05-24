# Executable-Status Source Inventory

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-COVERAGE-A0

## Sources surveyed

| source_id | role | date range | market | label coverage | official? | limitations |
|---|---|---|---|---|---|---|
| `s3_krx_status_events_2018_2026` | semi-official primary (OPENDART pblntfty=I 거래소공시 filtered) | 2018-01-01 → 2026-05-06 | KOSPI + KOSDAQ (OPENDART corp_cls Y/K) | suspension / resumption / delisting / managed / liquidation / investment_alert (regex from report_nm) | semi-official (DART 거래소공시 published by exchange; canonical for event-driven status changes) | (a) does NOT capture intraday halts; (b) does NOT capture limit-lock; (c) report_nm regex labelling is approximate; (d) DART body parsing CLOSED AS PARTIAL — exact effective dates not always extractable; (e) 2018+ only; (f) 53.1% coverage of disappeared tickers per ACQUISITION_SUMMARY |
| `s3_dart_pblntfty_I_all_2018_2026` | raw OPENDART 거래소공시 dump | 2018-01-01 → 2026-05-06 | KOSPI+KOSDAQ+KONEX+etc | any pblntfty=I — broader than status events | official (OPENDART) | raw — needs filtering; status_events.csv is the filtered version |
| `w001_v2_panel_with_tradable_state` | derived proxy (panel-level) | 2018-01-02 → 2026-05-06 (panel window) | panel-selected tickers (dynamic_top100) | executable / panel_absence / true_suspension / delisting_transition / limit_lock_candidate / data_missing | proxy (derived) | (a) TRAD_000001 critical defect: panel_absence != officially_delisted; (b) limit_lock_candidate is OHLCV-pattern-derived, not KRX-official; (c) covers only panel tickers — not full universe |
| `w001_v2_listing_status_events` | DART-derived status events (consolidated) | 2018-01-02 → 2026-05-06 | panel ticker subset | suspension / resumption / delisting / managed / surveillance / none | semi-official derivation | same as S3 — DART body coverage is partial; rename + merger linkage missing |
| `w001_v2_listing_status_terminal` | derived terminal status (per-ticker last known) | n/a (per-ticker snapshot) | panel tickers with terminal events | delisted / suspended_last_known / none | semi-official derivation | 47% of historic disappearances unresolved (no DART terminal event captured) |
| `kr_listed_universe_lifecycle_coverage` | listed-universe lifecycle context | 2010-01-04 → 2026-05-22 (monthly resolution) | KOSPI + KOSDAQ | delisted_with_terminal / still_listed / disappeared_no_terminal | best-available official + W001 v2 join | monthly resolution; no intraday status; no limit-lock |
| `equity_panel_ohlcv_signatures` | proxy (OHLCV-pattern derived) | 2010-01-04 → 2026-05-06 | panel tickers | S1-S6 invalid signatures (OHL=0/close>0 etc) | proxy (NOT executable status) | OHLCV signatures DO NOT prove suspension/halt; require external official source |

## Source hierarchy used in this phase

1. **Primary (semi-official)**: `s3_krx_status_events_2018_2026.csv` — OPENDART
   pblntfty=I (거래소공시) is the canonical exchange-disclosure source. Status
   events are filed by KRX/KOSDAQ market authority via DART.
2. **Secondary (semi-official derivation)**: W001 v2 `listing_status_events` +
   `listing_status_terminal` — consolidated/canonicalised versions of S3.
3. **Proxy (derived)**: W001 v2 `tradable_state` — date-level panel proxy.
   Not authoritative.
4. **Context (lifecycle)**: KR-LISTED-UNIVERSE-COVERAGE-A0 lifecycle table.
5. **Supporting evidence ONLY**: OHLCV signature audit (S1-S6). Cannot prove
   status; can only cross-check.

## NOT acquired in this phase

- KRX 정보데이터시스템 매매거래정지 endpoint (direct intraday halt list) —
  no pykrx wrapper; would require custom HTTP scraping with auth.
- KOSCOM real-time halt/limit feed — commercial license.
- pykrx managed-stock list — not exposed as a callable API in installed pykrx.
- Intraday halt windows — out of scope for date-level audit.
- Limit-lock authoritative list — only OHLCV-derived candidates available.

## Hard locks (preserved)

- No credential committed.
- No execution simulation.
- No strategy test.
- No executable claim from panel presence.
