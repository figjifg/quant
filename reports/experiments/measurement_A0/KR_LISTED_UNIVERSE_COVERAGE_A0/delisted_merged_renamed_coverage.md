# Delisted / Merged / Renamed Coverage

Date: 2026-05-24  
Phase: KR-LISTED-UNIVERSE-COVERAGE-A0

## Coverage from existing sources

- Delisted tickers (W001 v2 listing_status_terminal `terminal_status='delisted'`): **466**
- Suspended-last-known tickers: **788**

## Gaps

- **Merger linkage**: NOT in repo. When ticker A is merged into ticker B,
  the repo has no mapping A→B. This blocks survivorship-safe re-construction
  of holdings histories.
- **Rename history**: NOT in repo. Permanent_id_master captures *current*
  name only.
- **Relisting / code reuse**: NOT in repo. Same KRX ticker code can be reused
  after a delisting; the repo cannot currently distinguish.
- **Split / spin-off**: NOT in repo. Corporate-action overlay (S1 adjusted
  OHLC) captures price effect but not identity remapping.

## What would resolve these gaps

- Per-ticker corporate-action ledger (merger / split / rename / relisting)
  from a single authoritative source. Candidates: KRX corporate action API,
  KOSCOM event feed, OPENDART body parse (which is CLOSED AS PARTIAL).
- Until then, these gaps remain reopen blockers for any strategy work.

## Hard locks (preserved)

- No survivorship-safe claim.
- No strategy reopen.
