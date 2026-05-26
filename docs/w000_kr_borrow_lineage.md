# W000 Item 6 — KRX Securities-Lending (Borrow) Data (lineage / coverage record)

Acquired 2026-05-26 under the W000 autonomous data track (download/API pre-approval).
Committed record of record; raw CSVs live under `data/acquired/w000_kr_borrow/`
(gitignored).

## Source + method

- Source: **DATA.GO.KR 금융위원회 주식대차정보**,
  `GetStocLendBorrInfoService_V2 / getStItemLendAndBorrStatu_V2` (per-ticker daily
  lending/borrow status). Auth: `DATA_GO_KR_API_KEY` (read in-process, never
  printed/committed).
- Method: one API call per trading date (basDt), `numOfRows=10000` returns all listed
  stocks in a single page (~2,400 rows/date). Filtered to KR7 ISINs; ticker derived from
  ISIN chars 3:9 (KR7005930003 → 005930). Script:
  `src/data/w000_kr_borrow_acquire.py` (checkpointed per date + resumable; the API is
  ~3s/call so the full pull is ~100 min).
- Chosen because pykrx shorting/fundamental endpoints are currently broken (KRX returns
  empty: "Expecting value: line 1 column 1").
- Fields: `borrow_contracted_shares` (lnbCclStckCnt 대차체결주식수, newly contracted),
  `borrow_balance_shares` (lnbRmanStckCnt 대차잔여주식수, **outstanding borrow balance**),
  `borrow_repaid_shares` (lnbRdptStckCnt 상환주식수).

## Coverage

- 2,052 trading dates queried, **all status=ok**; borrow data present on **2,019 dates**
  (2018-01-02 .. 2026-05-08).
- **4,757,456 rows**, **3,154 tickers** (full KR-listed lending universe, broader than the
  833-ticker research set).
- `borrow_balance_shares` 100% non-null; 99.93% of rows have balance > 0.
- Research-universe overlap: **831/833** TR tickers have borrow data (the 2 missing align
  with the delisted no_data names from item 2).

## Known caveats (fail-closed, documented — NOT silently patched)

- **Partial coverage: BALANCE side only.** This API provides borrow contracted/balance/
  repaid SHARES. It does **NOT** provide borrow FEE / short-rebate rate, the short-sale
  RESTRICTION (공매도 제한) list, or forced BUY-IN events — those remain a residual
  W000 item-6 gap and would need a different source (KRX paid feed / 한국예탁결제원 / etc.).
- 33 of 2,052 queried dates returned no lending rows (early dates / non-data days).
- Research-grade infra dataset, not an authoritative trading feed.

## Hard-lock confirmations (W000 track)

- Raw CSVs under `data/acquired/w000_kr_borrow/` are gitignored; this doc is the committed
  record. No `data/raw/` or `research_input_data/` modification.
- W000 Hard Rule: DATA INFRASTRUCTURE only — acquiring it does NOT reopen the closed
  Korean long-short (W001 v2) research. No strategy/backtest/execution use. No P08 weight
  change. API key never printed/committed/logged.

## sha256 (acquired artifacts, 2026-05-26)

```
77c0ef27f95c4167a39e69dce5d4f5fc35e6dfb4f93ed7fd95e6104e116ab0a0  kr_borrow_balance_2018_2026.csv
b12f6ba29aee331904a9e34de77cf0037818e983d56b937c455ff37d88c18325  acquisition_manifest.csv
```
