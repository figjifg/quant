# KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0 — Referee Lock

Date: 2026-05-24  
Verdict source: Referee verdict opening this phase, 2026-05-24.  
Predecessor: KR-EXECUTABLE-STATUS-COVERAGE-A0 CLOSED AS EXECUTABLE-STATUS-SOURCE-
ACQUIRED / PARTIAL COVERAGE / EXECUTION STILL CLOSED (commit `c6c935f`).

## Scope (Referee-fixed)

- Measurement-layer limit-lock source acquisition + reconciliation audit only.
- Acquire / validate / reconcile official / best-available upper-limit / lower-limit
  status data for Korean equities.
- Focus on whether a stock was actually executable under price-limit conditions on a
  given date.
- No strategy testing.
- No performance diagnostics.
- No execution simulation.
- No production / paper / P08 / live readiness / shadow.

## Reason

- Executable-status coverage A0 found `limit_lock_proxy_only` defect: official KRX
  limit-lock log not in repo; only 41 W001 v2 OHLCV-derived candidates exist.
- Korean stock execution requires 상한가 / 하한가 handling.
- Future backtest cannot safely assume:
  - limit-up buy is executable,
  - limit-down sell is executable,
  - limit-lock candidate is definitive,
  - OHLCV pattern alone proves order executability.

## Allowed tasks (9)

1. Source inventory.
2. Official / best-available source acquisition.
3. Define limit-lock taxonomy.
4. Reconcile against W001 v2 limit_lock_candidate.
5. Conservative execution rule design (design-only, not simulation).
6. Cross-check with OHLCV quarantine.
7. Build limit-lock coverage table.
8. Build defect ledger.
9. Gate status update.

## Required outputs (12)

1. `limit_lock_referee_lock.md` (this file)
2. `source_inventory.md`
3. `official_limit_lock_source_report.md`
4. `limit_lock_taxonomy.md`
5. `limit_lock_coverage_table.csv`
6. `w001_limit_candidate_reconciliation.md`
7. `w001_limit_candidate_reconciliation_ledger.csv`
8. `conservative_execution_rule_design.md`
9. `ohlcv_limit_overlap_audit.md`
10. `limit_lock_defect_ledger.csv`
11. `limit_lock_gate_status.md`
12. `limit_lock_final_summary.md`

## Gate enum (Referee-permitted)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `OFFICIAL_SOURCE_ACQUIRED_BUT_NOT_FULLY_RECONCILED`
- `LIMIT_LOCK_SOURCE_RECONCILED_BUT_EXECUTION_STILL_CLOSED`
- `READY_FOR_NEXT_A0_REVIEW`

Do NOT mark execution simulation open. Do NOT mark strategy testing open. Do NOT mark
any card strategy-ready.

## Pass criteria

- Limit-lock source candidates identified + documented.
- Official or best-available limit source acquired or failure documented.
- Taxonomy separates official / proxy / candidate / unknown.
- W001 v2 limit_lock_candidate rows reconciled or classified as proxy-only.
- OHLCV invalid rows NOT used as sole limit-lock proof.
- Conservative future execution rule design documented.
- Defect ledger produced.
- Gate status explicitly stated.
- No strategy test / execution simulation / performance metric produced.

## Fail / partial gates

- No official source → DATA_SOURCE_FAIL / BACKLOG.
- Source cannot distinguish upper vs lower → PARTIAL.
- Source cannot distinguish close-at-limit from locked-unexecutable → PARTIAL.
- OHLCV candidate promoted to official limit status → FAIL.
- Unknown status treated as executable → FAIL.
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
- No survivorship-safe claim unless explicitly supported.
- No unknown status treated as executable.
- No panel absence treated as non-tradable.
- No OHLCV signature treated as official limit-lock proof.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## Important boundary

- Limit-lock source coverage A0.
- Passing this phase does NOT reopen strategy testing.
- Passing this phase does NOT open execution simulation automatically.
- Only reduces limit-lock / price-limit ambiguity.
- Execution-simulation readiness still requires separate Referee review.

## End condition

- Return limit-lock source coverage A0 report only.
- Do not recommend strategy testing.
- Do not recommend production or paper tracking.
- Referee will decide whether to:
  - A. close as limit-lock source acquired and reconciled,
  - B. require another reconciliation pass,
  - C. open executable-status pre-2018 extension,
  - D. open listed-universe daily lifecycle refinement,
  - E. keep all strategy research closed.
