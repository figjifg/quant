# KR-LISTED-UNIVERSE-COVERAGE-A0 — Final Close Note

Date: 2026-05-24  
Verdict source: Referee final close verdict, 2026-05-24.  
Initial pass commit accepted: `dbd847b` on origin/main.

## Verdict

**CLOSED AS LISTED-UNIVERSE-SOURCE-ACQUIRED / PARTIAL LIFECYCLE / NOT SURVIVORSHIP-SAFE.**

- Decision: option **A** (close as listed-universe source reconciled).
- More precisely: monthly best-available source acquired; lifecycle coverage remains
  PARTIAL; survivorship-safe claim explicitly REJECTED.
- No additional reconciliation pass required now.
- No strategy testing reopened.
- No execution simulation opened.
- No performance diagnostics reopened.
- No production / paper / P08 / live readiness / shadow-track work touched.

## Accepted deliverables (12)

1. `listed_universe_referee_lock.md`
2. `source_inventory.md` (10 sources surveyed)
3. `official_listed_universe_source_report.md`
4. `listed_lifecycle_coverage_table.csv` (3,653 rows)
5. `panel_vs_official_reconciliation_summary.md`
6. `panel_vs_official_reconciliation_ledger.csv`
7. `permanent_id_coverage_update.md`
8. `delisted_merged_renamed_coverage.md`
9. `survivorship_safety_assessment.md`
10. `listed_universe_defect_ledger.csv` (519 rows)
11. `listed_universe_gate_status.md`
12. `listed_universe_final_summary.md`

## Accepted source

- Method: pykrx `get_market_ticker_list(date, market)` with KRX_ID/KRX_PW auth (loaded
  from local .env, NOT committed).
- Granularity: **monthly first-trading-day**, 2010-01 → 2026-05.
- Snapshots: 197.
- Markets: KOSPI + KOSDAQ.
- Unique tickers ever listed: 3,653.
- Total snapshot-rows: 441,359.
- Storage: `data/acquired/krx_listed_universe/krx_listed_monthly_snapshots_2010_2026.csv`
  (gitignored; reproducible via build script).

## Accepted reconciliation

- Official / best-available universe: **3,653 tickers**.
- Repo panel union: **925 tickers**.
- Matched: **925**.
- Panel-only: **0**.
- Official-only: **2,728**.
- Coverage of official by panel: **25.3%**.
- Disappeared without W001 v2 terminal event: **519**.
- Defect ledger: **519 rows**.

## Accepted survivorship verdict

**NOT SURVIVORSHIP-SAFE.**

- Lifecycle coverage remains partial.
- Repo panel = liquidity-biased dynamic_top100, not full all-market universe.
- 74.7% of official ever-listed universe absent from panel.
- Missing names concentrated in lower-liquidity / failed / delisted small caps.
- Merger linkage / rename history / code reuse mapping: NOT in repo.
- W001 v2 terminal event coverage is partial.
- No survivorship-safe claim authorised.

## Accepted permanent ID update

- DART corp_code IDs: **stable**.
- KRX_TICKER_xxxxxx fallback IDs: temporary, ticker-based.
- 50 fallback IDs present in official monthly snapshots.
- Acceptable for measurement-layer audit; **blocks full strategy pass**.
- Rename / code reuse / relisting ambiguity remains.

## Accepted gate state

**PARTIAL** (per Referee-permitted enum).

## Accepted limitations

- Monthly snapshot resolution → only approximate listing/delisting timing.
- KONEX excluded.
- Merger linkage missing.
- Rename history missing.
- Code reuse cannot be resolved.
- Intraday executable status not covered.
- Source does NOT solve execution feasibility.
- Source does NOT solve DART body / corporate-action event-log gaps.
- Source does NOT reopen any strategy.

## Possible future phases (none active)

| Phase id | Purpose | Status |
|---|---|---|
| `KR-EXECUTABLE-STATUS-COVERAGE-A0` | Acquire / validate official executable-status / halt / limit-lock source | NOT approved (**Referee-recommended next** for execution feasibility) |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle; merger linkage; rename history; code reuse | NOT approved |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | Patch the 4 remaining ops blockers | NOT approved |
| `KR-CLOSED-STRATEGY-CODEPATH-QUARANTINE-A0` | Optional follow-up before any strategy reopen | NOT approved (lower priority) |

Referee-recommended next candidate (if user chooses to continue):
**`KR-EXECUTABLE-STATUS-COVERAGE-A0`** — calendar reconciled + listed-universe
acquired; execution feasibility now needs executable-status source. Must NOT
auto-start.

Backtesting remains **premature**. Future strategy review must explicitly account for
the listed-universe limitation: repo panel is dynamic_top100 / liquidity-biased, not
full all-market survivorship-safe universe.

## Continuing hard locks

- No return backtest.
- No NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD.
- No post-event drift / migration return / turnover return / resume return / reversal
  return / flow-return.
- No raw jump alpha.
- No price-only mean reversion.
- No generic value / quality / momentum / RS ranking.
- No DART body alpha test.
- No overhang filter alpha test.
- No flow strategy testing.
- No execution simulation.
- No executable assumption from panel presence.
- No survivorship-safe claim unless explicitly supported.
- No use of ALLOW_WITH_GUARD fields without documented guard.
- No use of invalid OHLCV rows without quarantine.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## End condition

`KR-LISTED-UNIVERSE-COVERAGE-A0` is **closed as LISTED-UNIVERSE-SOURCE-ACQUIRED /
PARTIAL LIFECYCLE / NOT SURVIVORSHIP-SAFE**. No active work remains. Await explicit
user / Referee decision for any future executable-status, lifecycle refinement, ops
patch, parser, or strategy phase.
