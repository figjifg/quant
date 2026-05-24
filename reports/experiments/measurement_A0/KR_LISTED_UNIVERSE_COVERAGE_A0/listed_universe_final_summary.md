# KR-LISTED-UNIVERSE-COVERAGE-A0 — Final Summary

Date: 2026-05-24  
Predecessor: KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0 CLOSED.

## Scope respected

- Measurement-layer listed-universe / lifecycle audit only.
- No strategy testing.
- No performance diagnostics.
- No execution simulation.
- No production / paper / P08 / live / shadow.

## What was delivered

Code artifacts:
- `src/audit/measurement_a0/p_listed_universe_coverage.py`

Data artifacts:
- `data/acquired/krx_listed_universe/krx_listed_monthly_snapshots_2010_2026.csv` (gitignored; monthly first-trading-day KRX listed snapshots 2010-01-04 → 2026-05-04)

Reports (this dir, 12 outputs):
1. `listed_universe_referee_lock.md`
2. `source_inventory.md`
3. `official_listed_universe_source_report.md`
4. `listed_lifecycle_coverage_table.csv`
5. `panel_vs_official_reconciliation_summary.md`
6. `panel_vs_official_reconciliation_ledger.csv`
7. `permanent_id_coverage_update.md`
8. `delisted_merged_renamed_coverage.md`
9. `survivorship_safety_assessment.md`
10. `listed_universe_defect_ledger.csv`
11. `listed_universe_gate_status.md`
12. `calendar_source_final_summary.md` (this file actually named `listed_universe_final_summary.md`)

## Acquisition headline

- Method: pykrx `get_market_ticker_list(date, market)` with KRX_ID auth.
- Granularity: **monthly first-trading-day** across 2010-01 → 2026-05.
- Total unique tickers ever listed: **3653**.
- Coverage: KOSPI + KOSDAQ.

## Reconciliation headline

- Official universe: **3653** tickers
- Union panel: **925** tickers (25.3% of official)
- Matched: **925**
- Panel-only: **0**
- Official-only: **2728**

## Lifecycle coverage

- Tickers with W001 v2 terminal status: **1723**
- Tickers disappeared without terminal event: **519**

## Defect ledger

- Total defects: **519**
- Classes: `panel_ticker_not_in_official_source`, `disappeared_no_terminal_event`, `fallback_id_not_in_official_universe`

## Survivorship-safety verdict

**NOT SURVIVORSHIP-SAFE — partial lifecycle coverage.**

Repo panel covers ~25.3% of official ever-listed
universe. ~74.7% of historic listings are
absent from panel — primarily delisted small caps. Merger linkage, rename
history, and code reuse are not in repo. See `survivorship_safety_assessment.md`.

## Listed-universe gate state: **PARTIAL**

## Pass criteria evaluation

| criterion | status |
|---|---|
| Listed-universe source identified + documented | YES (best-available, monthly resolution) |
| Source date range + market coverage stated | YES (2010-01 → 2026-05, KOSPI+KOSDAQ) |
| Existing panel tickers reconciled against source | YES |
| Delisted/merged/renamed/relisted/code-reuse risks assessed | PARTIAL (see `delisted_merged_renamed_coverage.md`) |
| Permanent ID coverage updated | YES (see `permanent_id_coverage_update.md`) |
| Defect ledger produced | YES |
| Survivorship safety status stated | YES — explicitly NOT SURVIVORSHIP-SAFE |
| No strategy test / execution sim / performance metric produced | YES |

## Hard locks (preserved)

- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / execution sim /
  production / paper / P08 / live / shadow.
- No survivorship-safe claim.
- No card is strategy-ready.
- No credential committed.

## Awaiting Referee

Per Referee-defined exit conditions, Referee will decide whether to:
- A. close as listed-universe source reconciled,
- B. require another lifecycle reconciliation pass,
- C. open executable-status source acquisition,
- D. open ops NAV blocker patch,
- E. keep all strategy research closed.
