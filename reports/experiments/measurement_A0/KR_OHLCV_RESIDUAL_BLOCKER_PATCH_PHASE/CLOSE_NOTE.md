# KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE — Final Close Note

Date: 2026-05-24  
Verdict source: Referee final close verdict, 2026-05-24.  
Initial pass commit accepted: `3942904` on origin/main.

## Verdict

**CLOSED AS RESIDUAL-BLOCKERS-REDUCED / OPS BLOCKERS PRESERVED.**

- Decision: option **A** (close as residual blockers reduced).
- More precisely: 40 of 45 residual blockers patched; 1 prior `future_work` item
  resolved as `false_positive_static_scan`; 4 ops blockers preserved per production
  lock.
- Not a clean full pass. Not a strategy pass. Not production readiness.
- No additional residual patch pass required now.
- No KRX calendar source acquisition auto-started.
- No strategy testing reopened.
- No performance diagnostics reopened.
- No production / paper / P08 / live readiness / shadow-track work touched.

## Accepted deliverables (9)

1. `residual_patch_referee_lock.md`
2. `residual_blocker_inventory.csv` (45 rows)
3. `residual_patch_plan.csv` (45 rows with `residual_patch_status` + evidence)
4. `patched_residual_delta.csv` (45 rows pre vs post)
5. `residual_static_rescan_summary.md`
6. `residual_runtime_smoke_check.md` (6/6 PASS)
7. `remaining_residual_blockers.csv` (4 ops rows preserved)
8. `future_work_item_resolution.md` (1 row resolved)
9. `residual_patch_final_summary.md`

Plus `rescan/` subdirectory with the 4 post-rescan snapshots.

## Accepted code artifacts

- `src/utils/ohlcv_quarantine.py` — new helper `assert_panel_has_valid_mask(df, *, context)`
  (lightweight fail-closed gate).
- `tests/test_ohlcv_quarantine.py` — **22/22 tests passing** (3 new tests for the
  helper).
- 6 closed-strategy files patched with entry-function asserts:
  - `src/strategies/baselines.py:run_baseline`
  - `src/strategies/b004_regime_gate.py:run_b004_variants`
  - `src/strategies/c003_monthly_macro_gate.py:run_c003_variants`
  - `src/strategies/d004_position_sizing.py:run_d004_variants`
  - `src/strategies/p002_d013_execution.py:run_p002_execution_backtest`
  - `src/strategies/p003_d013_cost_capacity.py:run_capacity_backtest`

## Accepted patch_status distribution (45 blockers)

| status | count | rationale |
|---|---:|---|
| patched | 40 | 6 closed-strategy entry guards covered 40 blockers |
| still_reopen_blocker | 4 | `src/ops/nav_update.py` (production-locked; no ops patch authorised) |
| false_positive_static_scan | 1 | `pit_sector_aggregator.py:215` (column-name in selection list; upstream-filtered) |
| **total** | **45** | |

## Accepted runtime smoke result

- **6/6 patched closed-strategy entry functions** raise `OhlcvQuarantineError` when
  invoked without `valid_ohlcv_mask`.
- Defense-in-depth on top of the already-verified backtest engine entry gate.

## Residual lock — 4 ops blockers preserved

- `src/ops/nav_update.py` rows remain `reopen_blocker=true`.
- Block any paper/live/ops reopen unless separately scoped and patched.
- NOT deleted, NOT suppressed, NOT downgraded, NOT reinterpreted.
- Closed strategies remain CLOSED even though entry guards were added.

## Possible future phases (none active)

| Phase id | Purpose | Status |
|---|---|---|
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | Patch the 4 remaining ops blockers | NOT approved (touches ops/paper/live-related code) |
| `KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0` | Acquire authoritative KRX calendar | NOT approved (**Referee-recommended next direction** if priority = execution-sim readiness) |
| `KR-LISTED-UNIVERSE-COVERAGE-A0` | DATA BACKLOG, source not acquired | NOT approved |
| `KR-EXECUTABLE-STATUS-COVERAGE-A0` | DATA BACKLOG, source not acquired | NOT approved |
| `KR-CLOSED-STRATEGY-CODEPATH-QUARANTINE-A0` | Optional follow-up | NOT approved (lower priority — entry guards already added) |

Referee-recommended next candidate (if user chooses to continue):
**`KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0`** — major remaining blocker for execution
simulation. Must NOT auto-start.

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
- No executable assumption from panel presence.
- No survivorship-safe claim without official listed universe.
- No use of ALLOW_WITH_GUARD fields without documented guard.
- No use of invalid OHLCV rows without quarantine.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## End condition

`KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE` is **closed as RESIDUAL-BLOCKERS-REDUCED / OPS
BLOCKERS PRESERVED**. No active work remains. Await explicit user / Referee decision
for any future ops patch, calendar source, listed-universe, executable-status, parser,
or strategy phase.
