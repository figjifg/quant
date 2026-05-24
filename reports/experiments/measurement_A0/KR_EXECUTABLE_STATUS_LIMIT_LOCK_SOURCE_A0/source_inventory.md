# Limit-Lock Source Inventory

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0

## Sources surveyed

| source_id | role | is_official? | upper/lower? | close_at_limit vs locked? | limitations |
|---|---|---|---|---|---|
| `krx_historical_price_limit_rule` | official rule | official KRX rule | yes (computed: upper = prev_close × (1 + lim_pct); lower = prev_close × (1 - lim_pct)) | no — rule gives the limit price, not whether trading was locked at it | (a) gives only the daily price limit, not whether the close was actually locked at limit; (b) does NOT capture single-stock circuit breakers (단일가매매); (c) does NOT capture limit-up/limit-down lock release; (d) first-day-of-listing rule differs (no daily limit on day 1 for IPOs); (e) limit calculation uses prev_close — corporate-action days adjust prev_close (KRX reference price) |
| `w001_v2_limit_lock_candidate` | OHLCV-pattern proxy (41 rows) | proxy (NOT official) | no (binary label only) | no (candidate based on OHLCV pattern; cannot prove lock) | (a) candidate-only; (b) does not specify upper or lower direction; (c) 41 rows is implausibly low for 1.1M-row panel — likely incomplete derivation; (d) no source backing in repo |
| `pykrx_get_market_price_change` | etrnal endpoint test result | API only — NOT a limit-lock source | no (returns price-change, not limit status) | no | pykrx does NOT expose a daily limit-lock list; only OHLCV change ratios. Tested in this phase — no relevant endpoint found. |
| `krx_data_system_단일가매매_endpoint` | candidate official source — not acquired | candidate official | potentially yes (KRX-internal data) | potentially yes | would require KRX 정보데이터시스템 manual scraping with separate licensing; not attempted in this audit phase |
| `panel_ohlcv_columns` | supporting evidence (OHLCV pattern derivation) | raw OHLCV (NOT limit-lock proof) | via close vs prev_close × (1±lim_pct) comparison | no (cannot determine lock from close alone) | OHLCV pattern alone is candidate-only; quarantine signatures (S1-S6) must be excluded first |

## Headline finding

**No direct daily limit-lock source available in repo or via pykrx.**

Best-available source for this phase is the **KRX historical price-limit
rule** itself, applied to panel OHLCV. This computes the *limit price* per
(date, ticker) and lets us flag rows where `close ≈ limit_price` as a
**candidate** for limit-lock. The candidate label is NOT official because:

- Close-at-limit does NOT prove the stock was lock-held at the limit; it may
  have traded normally at the limit price.
- An actual *lock* (단일가매매 lock-up) is determined by KRX intraday data,
  not by daily OHLCV.
- This audit uses the rule-derived candidate ONLY to expand the W001 v2
  41-row sparse candidate set; the result remains `candidate_proxy_only`.

## KRX historical price-limit rule (used for candidate derivation)

| period | KOSPI | KOSDAQ |
|---|---|---|
| ≤ 2015-06-14 | ±15% | ±15% (since 2005-09-01) |
| ≥ 2015-06-15 | ±30% | ±30% |

**Rule application**:
- `upper_limit_price = prev_close × (1 + lim_pct)`
- `lower_limit_price = prev_close × (1 - lim_pct)`
- KRX rounds to the appropriate tick; this audit uses ±0.1% tolerance to
  compare close vs the rule-derived limit price.

**Out of scope**:
- First-day-of-listing IPO rule (no daily limit on day 1 for KOSPI200 IPOs).
- Single-stock circuit breakers (단일가매매 sidecar).
- Volatility interruption (VI).
- ETF/ETN limit rules differ (this phase covers stocks only).

## Hard locks (preserved)

- No credential committed.
- No execution simulation.
- Candidate label remains `candidate_proxy_only`.
