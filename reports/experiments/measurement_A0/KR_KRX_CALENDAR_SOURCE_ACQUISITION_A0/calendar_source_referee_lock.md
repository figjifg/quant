# KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0 — Referee Lock

Date: 2026-05-24  
Verdict source: Referee verdict opening this phase, 2026-05-24.  
Predecessor: KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE CLOSED AS RESIDUAL-BLOCKERS-REDUCED
/ OPS BLOCKERS PRESERVED (commit `16897f3`).

## Scope (Referee-fixed)

- Measurement-layer source acquisition + reconciliation only.
- Acquire or reconstruct an authoritative KRX trading calendar.
- Reconcile it against the repo's current working calendar.
- No strategy testing.
- No performance diagnostics.
- No execution simulation yet.
- No production / paper / P08 / live readiness / shadow.

## Reason

- Calendar source remained UNRESOLVED through P0-2 (KR-CALENDAR-PANEL-ALIGN-A0).
- T+1 mapping was reproducible only relative to a union working calendar, not against
  an authoritative KRX source.
- Execution-simulation gating remains CLOSED until an official calendar is acquired and
  reconciled.

## Primary source-of-truth (read-only)

- `KR_CALENDAR_PANEL_ALIGN_A0/calendar_panel_alignment_summary.md`
- `KR_CALENDAR_PANEL_ALIGN_A0/krx_calendar_source_check.md`
- `KR_CALENDAR_PANEL_ALIGN_A0/t_plus_1_mapping_reproducibility.md`

## Allowed tasks (8)

1. Define official KRX calendar acquisition candidates.
2. Acquire authoritative or best-available KRX calendar.
3. Build calendar reconciliation table.
4. Re-evaluate t+1 mapping.
5. Produce anomaly ledger.
6. Define calendar usage contract.
7. Update execution-simulation gate status (within Referee-permitted enum only).
8. Security and data handling — no key commit, no credential print.

## Required outputs (11)

1. `calendar_source_referee_lock.md` (this file)
2. `official_krx_calendar_source_report.md`
3. `acquired_calendar_inventory.csv`
4. `calendar_reconciliation_summary.md`
5. `calendar_reconciliation_ledger.csv`
6. `t_plus_1_official_mapping_check.md`
7. `t_plus_1_mapping_delta.csv`
8. `calendar_anomaly_ledger.csv`
9. `calendar_usage_contract.md`
10. `execution_simulation_gate_status.md`
11. `calendar_source_final_summary.md`

## Execution-simulation gate states (Referee-permitted)

- `CLOSED`
- `PARTIAL`
- `CALENDAR_SOURCE_ACQUIRED_BUT_NOT_FULLY_RECONCILED`
- `CALENDAR_SOURCE_RECONCILED_BUT_EXECUTION_STILL_CLOSED`
- `READY_FOR_NEXT_A0_REVIEW`

Do NOT mark execution simulation as open. Do NOT mark strategy testing as open.

## Pass criteria

- Official or best-available KRX calendar source identified and documented.
- Date range coverage stated.
- Calendar source limitations stated.
- Repo union calendar reconciled against acquired source.
- T+1 mapping rebuilt from acquired source.
- Differences from prior union-calendar mapping recorded.
- Calendar anomaly ledger produced.
- Future calendar usage contract defined.
- No strategy test or execution simulation run.

## Fail / partial gates

- No official source → DATA SOURCE FAIL / BACKLOG.
- Incomplete coverage → PARTIAL.
- Material disagreement → execution simulation remains CLOSED.
- Material t+1 mapping difference → execution simulation remains CLOSED pending follow-up.
- Unclear provenance → not pass.
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
- No survivorship-safe claim without official listed universe.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## Important boundary

- Source acquisition + calendar reconciliation.
- Passing this phase does NOT reopen strategy testing.
- Passing this phase does NOT open execution simulation automatically.
- Only removes / reduces calendar-source ambiguity.
- Execution-simulation readiness requires a separate Referee verdict after this report.

## End condition

- Return KRX calendar source acquisition A0 report only.
- Do not recommend strategy testing.
- Do not recommend production or paper tracking.
- Referee will decide whether to:
  - A. close as calendar source acquired and reconciled,
  - B. require another calendar reconciliation pass,
  - C. open listed-universe source acquisition,
  - D. open executable-status source acquisition,
  - E. keep all strategy research closed.
