# KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0 — Referee Lock

Date: 2026-05-24  
Verdict source: Referee verdict opening this phase, 2026-05-24.  
Predecessor: KR-OHLCV-QUARANTINE-PATCH-PHASE CLOSED AS PATCHED-PARTIAL / RESIDUAL
BLOCKERS PRESERVED (commit `1e95c10`).

## Scope (Referee-fixed)

- Measurement-layer infrastructure audit only.
- Verify that `valid_ohlcv_mask` and invalid OHLCV guards propagate through actual
  runtime data flows.
- No strategy testing.
- No performance diagnostics.
- No production / paper / P08 / live readiness / shadow-track work.

## Reason

- Patch phase installed static guards and shared guard utilities.
- Runtime mask propagation was explicitly NOT verified there.
- Static scan only checks local guard proximity; it cannot prove masks survive actual
  data loading, transformation, universe building, feature construction, or backtest
  entry.
- The next measurement-layer question is whether invalid OHLCV rows can actually leak
  through runtime pipelines.

## Primary source-of-truth (read-only)

- `src/utils/ohlcv_quarantine.py`
- `reports/experiments/measurement_A0/KR_OHLCV_QUARANTINE_PATCH_PHASE/defect_patch_plan.csv`
- `reports/experiments/measurement_A0/KR_OHLCV_QUARANTINE_PATCH_PHASE/remaining_reopen_blockers.csv`
- `reports/experiments/measurement_A0/KR_OHLCV_QUARANTINE_PATCH_PHASE/static_rescan_summary.md`
- `reports/experiments/measurement_A0/KR_OHLCV_QUARANTINE_ENFORCEMENT_A0/invalid_ohlcv_row_contract.md`

These inputs are NOT modified by this phase.

## Allowed tasks (8)

1. Runtime pipeline inventory.
2. Mask propagation test design.
3. Synthetic invalid-row tests with S1-S6 + missing-mask signatures.
4. Real-data spot checks (known invalid rows from prior audit).
5. Backtest entry fail-closed check — failure-mode test only, no backtest.
6. Universe path check.
7. Feature path check — no alpha / momentum / reversal / RS / ranking computation.
8. Remaining blocker review — classify runtime status without delete / downgrade.

## Required outputs (9)

1. `runtime_mask_referee_lock.md` (this file)
2. `runtime_pipeline_inventory.csv`
3. `synthetic_invalid_row_test_report.md`
4. `real_invalid_row_spot_check.md`
5. `backtest_entry_fail_closed_check.md`
6. `universe_path_mask_propagation_check.md`
7. `feature_path_guard_check.md`
8. `residual_blocker_runtime_status.csv`
9. `runtime_mask_propagation_summary.md`

## Pass criteria

- All relevant runtime data paths inventoried.
- Synthetic invalid rows are blocked, masked, annotated, or fail-closed.
- Known real invalid rows do not pass into downstream paths as valid price observations.
- Backtest entry fails closed when `valid_ohlcv_mask` is missing.
- Universe construction cannot include invalid OHLCV rows without guard.
- Feature paths cannot use raw return-like fields without documented guard.
- Remaining blockers receive runtime status but are NOT deleted or downgraded.
- No strategy metric generated.

## Fail gates

- Any invalid OHLCV row reaches a runtime path as a valid price observation.
- Any runtime path reconstructs or uses raw OHLCV after quarantine without guard.
- Backtest entry accepts Korean stock panel data without `valid_ohlcv_mask`.
- Universe construction accepts invalid OHLCV rows silently.
- Feature code uses `Change`, `daily_return`, raw close/open/high/low, or trading value
  without guard.
- Any return / NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD produced.
- Any strategy test started.
- Any production / paper / P08 / live readiness / shadow-track work touched.

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
- No executable assumption from panel presence.
- No survivorship-safe claim without official listed universe.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## Important boundary

- Runtime verification, NOT strategy validation.
- Passing this phase does NOT reopen any strategy.
- Passing this phase does NOT make P08 / paper / production / live eligible.
- Passing this phase only confirms OHLCV quarantine guards propagate through tested
  runtime paths.

## End condition

- Return runtime mask propagation A0 report only.
- Do not recommend strategy testing.
- Do not recommend production or paper tracking.
