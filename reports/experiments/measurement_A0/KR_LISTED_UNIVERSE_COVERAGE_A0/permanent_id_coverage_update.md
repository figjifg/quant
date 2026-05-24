# Permanent ID Coverage Update

Date: 2026-05-24  
Phase: KR-LISTED-UNIVERSE-COVERAGE-A0

## Prior state (W001 v2 permanent_id_master.csv)

| source | count |
|---|---:|
| `dart_corp_code` | 783 |
| `krx_ticker_fallback` | 50 |

## Fallback IDs cross-checked against acquired official universe

- Total tickers in permanent_id_master with `krx_ticker_fallback` source: **50**
- Of those, present in newly-acquired official monthly snapshots: **50**
- Of those, NOT present in official snapshots: **0**

## Interpretation

- `krx_ticker_fallback` IDs were assigned when no DART corp_code match was
  found at the time of W001 v2 derivation. The newly-acquired official
  universe lets us check whether these fallback tickers existed on KRX at
  all.
- Fallback tickers present in official snapshots = real KRX tickers without
  a DART corp_code mapping (could be ETFs, REITs, or DART-unindexed names).
- Fallback tickers absent from official snapshots = either out-of-window
  delistings or panel typos.

## Remaining issue

- KRX_TICKER_xxxxxx fallback IDs remain **temporary** (ticker-based). They
  are NOT stable across rename or code-reuse events.
- Stable permanent IDs require:
  - successful DART corp_code lookup, OR
  - a KRX-stable issuer ID (not currently available in repo).
- The fallback IDs are usable for current panel work but should be re-mapped
  before any future strategy reopen.

## Status

- 783 DART-corp-code IDs: **stable**
- 50 KRX-ticker-fallback IDs: **temporary** (acceptable for measurement-layer audit; blocks full pass for strategy reopen)

## Hard locks (preserved)

- No strategy reopen authorised by this update.
- No survivorship-safe claim.
