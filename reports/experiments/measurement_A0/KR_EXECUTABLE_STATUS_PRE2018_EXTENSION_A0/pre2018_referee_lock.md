# KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0 — Referee Lock

Date: 2026-05-24  
Verdict source: Referee verdict opening this phase, 2026-05-24.  
Predecessor: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0 CLOSED AS LIMIT-LOCK-PROXY-
RECONCILED (commit `9d9e1c5`).

## Scope (Referee-fixed)

- Measurement-layer executable-status source extension only.
- Extend or attempt to extend executable-status coverage 2010-01-01 → 2017-12-31.
- No strategy testing.
- No performance diagnostics.
- No execution simulation.
- No production / paper / P08 / live readiness / shadow.

## Reason

- KR-EXECUTABLE-STATUS-COVERAGE-A0 closed PARTIAL.
- Primary historical gap: `pre_2018_status_coverage_gap` defect.
- S3 KRX status events cover 2018+ only.
- Repo contains earlier equity panels including 2010-2016 dynamic_top100.
- Any future use of 2010-2017 data requires status evidence.

## Allowed tasks (8)

1. Source feasibility check.
2. Attempt pre-2018 acquisition.
3. Normalise event taxonomy.
4. Reconcile with 2010-2017 repo panels.
5. Reconcile with executable-status coverage gap (update defect).
6. Build pre-2018 coverage table.
7. Build defect ledger.
8. Gate status update.

## Required outputs (12)

1. `pre2018_referee_lock.md` (this file)
2. `source_feasibility_report.md`
3. `acquisition_attempt_log.csv`
4. `pre2018_status_source_report.md`
5. `pre2018_status_coverage_table.csv`
6. `pre2018_taxonomy_mapping.md`
7. `pre2018_panel_reconciliation_summary.md`
8. `pre2018_panel_reconciliation_ledger.csv`
9. `pre2018_gap_closure_assessment.md`
10. `pre2018_defect_ledger.csv`
11. `pre2018_gate_status.md`
12. `pre2018_final_summary.md`

## Gate enum (Referee-permitted)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `PRE2018_SOURCE_ACQUIRED_BUT_NOT_FULLY_RECONCILED`
- `PRE2018_STATUS_RECONCILED_BUT_EXECUTION_STILL_CLOSED`
- `READY_FOR_NEXT_A0_REVIEW`

Do NOT mark execution simulation open. Do NOT mark strategy testing open. Do NOT mark
any card strategy-ready.

## Pass criteria

- Pre-2018 source feasibility documented.
- Acquisition attempt logged.
- Acquired or unavailable source status explicitly stated.
- Any acquired events mapped into the executable-status taxonomy.
- 2010-2017 panel linkage assessed.
- `pre_2018_status_coverage_gap` updated with evidence.
- Defect ledger produced.
- Gate status explicitly stated.
- No strategy test / execution sim / performance metric produced.

## Fail / partial gates

- No source for pre-2018 status events → DATA_SOURCE_FAIL or `source_unavailable`.
- Only partial years acquired → PARTIAL.
- Ambiguous report names → `requires_manual_review`.
- Effective dates undetermined → NO executable readiness claim.
- Panel disappearance used as status proof → FAIL.
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
- No OHLCV signature treated as suspension proof.
- No rule-derived limit candidate treated as official lock evidence.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## Important boundary

- Pre-2018 executable-status source extension A0.
- Passing this phase does NOT reopen strategy testing.
- Passing this phase does NOT open execution simulation automatically.
- Only reduces or documents the historical executable-status coverage gap.
- Execution-simulation readiness still requires separate Referee review.

## End condition

- Return pre-2018 executable-status extension A0 report only.
- Do not recommend strategy testing.
- Do not recommend production or paper tracking.
- Referee will decide whether to:
  - A. close as pre-2018 source acquired or source-unavailable documented,
  - B. require another pre-2018 source attempt,
  - C. open official limit-lock source acquisition,
  - D. open lifecycle daily refinement,
  - E. keep all strategy research closed.
