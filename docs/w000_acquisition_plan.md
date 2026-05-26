# W000 Data Infrastructure — Acquisition Plan (autonomous track)

Status: ACTIVE autonomous data track, opened 2026-05-26 by explicit user decision
("W000 외부 취득까지 자율 — 다운로드 사전승인"). Executor = Claude Code. This grounds the
W000 backlog (`docs/w000_data_infrastructure_backlog.md`) in actual local coverage +
source feasibility, audit-first, BEFORE acquiring.

## Authorization scope + guardrails

- **Download/API pre-approved** for W000 data acquisition (this is the standing approval).
- Still HARD-LOCKED (cannot auto-override): no modifying `data/raw/` or
  `research_input_data/` (raw protection); raw acquired artifacts go under
  `data/acquired/**` (gitignored) with a committed inventory/lineage; no P08_IEF30 weight
  change; no strategy/backtest/execution/paper/live claims; W000 Hard Rule = acquiring
  data does NOT reopen Q-family / sector / event / long-short research (each needs its own
  ticket + verdict).
- Audit-first: each acquired dataset documents source, method, adjustment policy,
  effective-date/timing policy, coverage, and known gaps. Fail-closed on ambiguity.
- Check-in points (NOT autonomous): a source needs a PAID vendor we don't have; a finding
  changes P08; reopening the standby'd KR-status measurement (DART body parser).

## Local tooling + credentials available

- Python libs: `yfinance`, `pykrx`, `requests` (FinanceDataReader / pandas_datareader /
  exchange_calendars NOT installed).
- Keys in `research_input_data/.env` (used per-call, never printed/committed): KRX
  (AUTH/API/ID/PW), KIS (한국투자증권), KIWOOM (키움), OPENDART, FRED, BOK (한국은행),
  DATA_GO_KR (공공데이터포털).

## Per-item status (from local gap-audit 2026-05-26)

| # | Item | ROI | Local coverage now | Gap | Feasibility / source |
|---|---|---|---|---|---|
| 1 | PIT sector membership | P0 | `krx_pit_sector_classifications.csv` 2010–2026 (3,631 tickers); daily stock→sector mapping (`stock_*_pit*.csv`) **only 2010–2018** | extend daily PIT mapping **2018→2026** | likely LOCAL join of classification onto panel dates; pykrx/KRX only if classification dates missing |
| 2 | Korean total return | P0 | `adjusted_ohlc_all_tickers_2018_2026.csv` (1.58M rows, adj_open/high/low/close + adj_return_pct) | confirm whether adj is **dividend-inclusive** (true TR) or split/rights only; if not TR, add dividends + ex-date policy | pykrx 수정주가 / KRX / KIS dividend data; BOK for index TR |
| 3 | Execution data | P1 | none (paper/live not started) | spread / volume participation / slippage / partial-fill | likely INFEASIBLE without broker fills; KIS/KIWOOM quotes have limited history → flag for decision |
| 4 | Survivorship-safe US universe | P1 | none | S&P 500/100 historical PIT membership | free PIT membership sources limited → flag for source decision (may need a specific dataset) |
| 5 | DART body parser | P2 | KR-status measurement layer (extensive, CLOSED/STANDBY) | structured buyback/cancellation/dividend amounts | = the standby'd measurement work; DO NOT reopen without a new decision |
| 6 | KRX borrow / short-sale | P3 | none | borrowable universe / borrow fee / short-sale restriction per date | KRX publishes short-sale data; pykrx/KRX API feasible; lowest ROI → defer |

## Execution order (ROI × feasibility)

1. **Item 1 — PIT sector daily mapping 2018→2026** (P0, likely local, addresses a concrete
   gap). FIRST.
2. **Item 2 — Korean total-return verification + dividend backfill** (P0).
3. **Item 6 — KRX short-sale/borrow** (quick public acquisition, low ROI) — opportunistic.
4. **Items 3, 4 — surface for source decision** (execution data likely infeasible locally;
   US PIT membership may need a chosen dataset).
5. **Item 5 — remains STANDBY** (KR-status measurement; do not reopen here).

Each completed item: dataset under `data/acquired/w000_<item>/` (gitignored) + a committed
lineage/inventory CSV + a short coverage note appended here. No strategy use.
