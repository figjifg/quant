# KR-LISTED-UNIVERSE-COVERAGE-A0 — Referee Lock

Date: 2026-05-24  
Verdict source: Referee verdict opening this phase, 2026-05-24.  
Predecessor: KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0 CLOSED AS CALENDAR-SOURCE-RECONCILED
(commit `777d5be`).

## Scope (Referee-fixed)

- Measurement-layer listed-universe / lifecycle coverage A0 only.
- Acquire, validate, or reconcile official / best-available listed-universe and
  lifecycle coverage for Korean equities.
- Focus on survivorship, delisting, merger, rename, relisting, ticker reuse, and
  permanent ID coverage.
- No strategy testing.
- No performance diagnostics.
- No execution simulation.
- No production / paper / P08 / live readiness / shadow.

## Reason

- Calendar source ambiguity materially reduced by the preceding phase.
- The next hard blocker for safe future backtesting is survivorship / listed-universe
  validity.
- Current repo panel alone cannot certify survivorship safety.

## Primary source-of-truth (read-only)

- `KR_LISTED_UNIVERSE_COVERAGE_BACKLOG/source_requirement_register.md`
- `data/processed/w001_v2/permanent_id_master.csv`
- `data/processed/w001_v2/listing_status_events.csv`
- `data/processed/w001_v2/listing_status_terminal.csv`
- `data/acquired/round4/s4_listed_companies/`
- `reports/experiments/round4_partial_reA0/permanent_id_fallback_validation.md`
- `reports/experiments/round4_1_v2_1/permanent_id_fallback_hardening.md`
- `KR_KRX_CALENDAR_SOURCE_ACQUISITION_A0/calendar_usage_contract.md`

## Allowed tasks (9)

1. Source inventory.
2. Official or best-available listed-universe source validation.
3. Build lifecycle coverage table.
4. Reconcile against repo panels.
5. Survivorship safety audit.
6. Date coverage audit (align with acquired KRX calendar).
7. Permanent ID coverage update.
8. Build defect ledger.
9. Gate status update (within Referee-permitted enum only).

## Required outputs (12)

1. `listed_universe_referee_lock.md` (this file)
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
12. `listed_universe_final_summary.md`

## Gate enum (Referee-permitted)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `OFFICIAL_SOURCE_ACQUIRED_BUT_NOT_FULLY_RECONCILED`
- `LISTED_UNIVERSE_RECONCILED_BUT_STRATEGY_STILL_CLOSED`
- `READY_FOR_NEXT_A0_REVIEW`

Do NOT mark strategy testing open. Do NOT mark execution simulation open. Do NOT mark
universe survivorship-safe unless evidence supports.

## Pass criteria

- Listed-universe source identified and documented.
- Source date range and market coverage stated.
- Existing panel tickers reconciled against official or best-available source.
- Delisted / merged / renamed / relisted / code-reuse risks assessed.
- Permanent ID coverage updated.
- Defect ledger produced.
- Survivorship safety status explicitly stated.
- No strategy test, execution simulation, or performance metric produced.

## Fail / partial gates

- No official or best-available source → DATA_SOURCE_FAIL / BACKLOG.
- Lifecycle source lacks delisting / terminal status → PARTIAL.
- Ticker reuse unresolved → PARTIAL or FAIL for affected names.
- Current panel shown to be survivor-only → strategy research remains CLOSED.
- Delisted or merged names missing materially → strategy research remains CLOSED.
- Any strategy metric produced → protocol violation.

## Hard prohibitions

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
- No survivorship-safe claim unless this A0 explicitly supports it.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## Important boundary

- Listed-universe / lifecycle source coverage A0.
- Passing this phase does NOT reopen strategy testing.
- Passing this phase does NOT open execution simulation automatically.
- Only reduces survivorship / lifecycle ambiguity.
- Execution-simulation readiness still needs executable-status coverage + separate
  Referee review.

## End condition

- Return listed-universe coverage A0 report only.
- Do not recommend strategy testing.
- Do not recommend production or paper tracking.
- Referee will decide whether to:
  - A. close as listed-universe source reconciled,
  - B. require another lifecycle reconciliation pass,
  - C. open executable-status source acquisition,
  - D. open ops NAV blocker patch,
  - E. keep all strategy research closed.
