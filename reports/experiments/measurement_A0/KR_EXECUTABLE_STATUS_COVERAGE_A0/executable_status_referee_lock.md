# KR-EXECUTABLE-STATUS-COVERAGE-A0 — Referee Lock

Date: 2026-05-24  
Verdict source: Referee verdict opening this phase, 2026-05-24.  
Predecessor: KR-LISTED-UNIVERSE-COVERAGE-A0 CLOSED AS LISTED-UNIVERSE-SOURCE-ACQUIRED
/ PARTIAL LIFECYCLE / NOT SURVIVORSHIP-SAFE (commit `f5b8407`).

## Scope (Referee-fixed)

- Measurement-layer executable-status source acquisition + coverage audit only.
- Acquire / validate / reconcile official / best-available executable-status data for
  Korean equities.
- Focus on whether a stock was actually tradable on a given date.
- No strategy testing.
- No performance diagnostics.
- No execution simulation.
- No production / paper / P08 / live readiness / shadow.

## Reason

- Calendar source reconciled (prior phase).
- Listed-universe acquired but survivorship PARTIAL (prior phase).
- Next blocker for execution-simulation readiness = executable-status coverage.
- Panel presence / volume>0 / tradable_state / dynamic_universe membership cannot
  prove actual executable status.

## Status categories required

- trading suspension
- trading resumption
- halt
- delisting transition
- liquidation / 정리매매
- managed stock / 관리종목
- investment alerts (주의 / 경고 / 위험)
- short-term overheated / 단기과열
- limit-lock / upper-limit / lower-limit (where available)

## Allowed tasks (9)

1. Source inventory.
2. Candidate official source acquisition.
3. Build executable-status taxonomy.
4. Reconcile against W001 tradable_state.
5. Reconcile against listed-universe lifecycle.
6. Reconcile against OHLCV quarantine findings.
7. Build executable-status coverage table.
8. Build defect ledger.
9. Gate status update (within Referee-permitted enum only).

## Required outputs (12)

1. `executable_status_referee_lock.md` (this file)
2. `source_inventory.md`
3. `official_executable_status_source_report.md`
4. `executable_status_taxonomy.md`
5. `executable_status_coverage_table.csv`
6. `w001_tradable_state_reconciliation.md`
7. `w001_tradable_state_reconciliation_ledger.csv`
8. `listed_lifecycle_executable_reconciliation.md`
9. `ohlcv_status_overlap_audit.md`
10. `executable_status_defect_ledger.csv`
11. `executable_status_gate_status.md`
12. `executable_status_final_summary.md`

## Gate enum (Referee-permitted)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `OFFICIAL_SOURCE_ACQUIRED_BUT_NOT_FULLY_RECONCILED`
- `EXECUTABLE_STATUS_RECONCILED_BUT_EXECUTION_STILL_CLOSED`
- `READY_FOR_NEXT_A0_REVIEW`

Do NOT mark execution simulation open. Do NOT mark strategy testing open. Do NOT mark
any card strategy-ready.

## Pass criteria

- Executable-status source candidates identified + documented.
- Best-available source acquired or source failure clearly documented.
- Taxonomy separates official / proxy / unknown / panel-or-universe-absence.
- W001 tradable_state reconciled against source where possible.
- Listed-lifecycle status cross-checked.
- OHLCV invalid rows not used as sole executable-status proof.
- Defect ledger produced.
- Gate status explicitly stated.
- No strategy test / execution simulation / performance metric produced.

## Fail / partial gates

- No official or best-available source → DATA_SOURCE_FAIL / BACKLOG.
- Source lacks halt / suspension / resumption coverage → PARTIAL.
- Panel presence or volume used as executable proof → FAIL.
- OHL=0 / `close>0` used as suspension proof → FAIL.
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
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## Important boundary

- Executable-status source coverage A0.
- Passing this phase does NOT reopen strategy testing.
- Passing this phase does NOT open execution simulation automatically.
- Only reduces tradability / halt / suspension / executable-status ambiguity.
- Execution-simulation readiness still requires separate Referee review.

## End condition

- Return executable-status coverage A0 report only.
- Do not recommend strategy testing.
- Do not recommend production or paper tracking.
- Referee will decide whether to:
  - A. close as executable-status source acquired and reconciled,
  - B. require another reconciliation pass,
  - C. open listed-universe daily lifecycle refinement,
  - D. open ops NAV blocker patch,
  - E. keep all strategy research closed.
