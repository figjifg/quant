# W000 Item 2 — Korean Total-Return Data (lineage / coverage record)

Acquired 2026-05-26 under the W000 autonomous data track (user decision "W000 외부 취득까지
자율 — 다운로드 사전승인"). This is the COMMITTED record of record; the raw acquired CSVs
live under `data/acquired/w000_korean_total_return/` (gitignored).

## Why this exists

The pre-existing adjusted OHLC (`data/acquired/round4/s1_adjusted_ohlc/`) is from pykrx
`get_market_ohlcv(adjusted=True)` = **split/rights-adjusted ONLY, NOT dividend-inclusive**.
True total return (dividend-reinvested) was missing, and pykrx fundamental (DPS) is
currently broken (KRX endpoint returns empty). So total return was acquired from yfinance.

## Source + method

- Source: **yfinance** (Yahoo Finance), `Ticker(<code>.KS|.KQ).history(auto_adjust=False)`,
  2018-01-01 .. 2026-05-10.
- Script: `src/data/w000_korean_total_return_acquire.py` (reproducible; `.KS` first,
  `.KQ` fallback for mislabeled/KOSDAQ names).
- Universe: 833 tickers = the research universe in `adjusted_ohlc_all_tickers_2018_2026.csv`
  (all latest-snapshot KOSPI), mapped to Yahoo symbols.
- Fields captured per ticker-day: `close` (unadjusted), `adj_close` (Yahoo split+dividend
  adjusted = **total-return price series**), `volume`; plus dividend events (ex-date +
  amount) and split events.

## Adjustment / timing convention

- `adj_close` is Yahoo's back-adjusted close: dividends are reinvested at the **ex-date**
  and splits applied, so cumulative `adj_close` return = total return.
- The dividend ledger records each cash dividend at its **ex-date** (PIT-correct: a
  dividend is only known/realized from its ex-date forward). For backtests, total return
  on day t = `adj_close[t]/adj_close[t-1] - 1`.
- `close` is unadjusted (use for split-adjustment cross-checks, not returns).

## Coverage (acquisition_manifest.csv)

- 833 universe tickers attempted: **811 ok / 22 no_data** (delisted names Yahoo lacks —
  e.g. 001140, 152330, 450140; these remain a known gap, fail-closed: NOT fabricated).
- Prices: **1,554,803 rows**, 811 tickers, 2018-01-02 .. 2026-05-08, `adj_close` 100% non-null.
- Dividends: **4,898 events** across **655 tickers**, ex-dates 2018-12-27 .. 2026-03-24.
- Splits: **499 events**.

## Validation

- Cross-check vs the independent pykrx split-adjusted series: 1,552,831 overlapping
  ticker-days, **median rel diff 0.0000; 88.1% agree <2%, 90.9% <5%** (residual = split
  back-adjustment timing differences between the two vendors — expected, confirms the
  data is real & consistent, not garbage).
- TR-vs-PR sanity (000020, 2018→2026): total return -32.40% vs price return -40.53% =
  **+8.13% dividend uplift** — confirms `adj_close` meaningfully captures dividends.

## Known caveats (fail-closed, documented — NOT silently patched)

- 22 delisted tickers have no Yahoo data → total return unavailable for them (gap).
- Yahoo Korean data can have occasional bad ticks / gaps; this dataset is a research-grade
  total-return proxy, NOT an authoritative vendor feed.
- Universe was the 833-ticker KOSPI research set; KOSDAQ-heavy names outside it are not
  covered. Pre-2018 not covered.

## Hard-lock confirmations (W000 track)

- Raw CSVs under `data/acquired/w000_korean_total_return/` are gitignored; this lineage
  doc is the committed record. No `data/raw/` or `research_input_data/` modification.
- W000 Hard Rule: this is DATA INFRASTRUCTURE only — acquiring it does NOT reopen any
  closed Korean-equity research (E/F/G/R/S). No strategy / backtest / execution use.
- No P08_IEF30 weight change.

## sha256 (acquired artifacts, 2026-05-26)

```
06bab913a4ef4eabe352432c4e1926204262492010417e0c39abf31c990cb8c6  kr_total_return_prices_2018_2026.csv
d4e017a5044da50e3d6b1a38ad3c022ac48a732628577f437611159ca51bd8d7  kr_dividend_ledger.csv
59442a651870fa49a720759d4f6d324adb3d950a7ec4ba8bf03b4590bfa92c89  kr_split_ledger.csv
da4c98e6034938530a90aa2f2bb3a42901aefe5b12bbc9659514aaeb1634bc07  acquisition_manifest.csv
```
