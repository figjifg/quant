# KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0 — Final Close Note

Date: 2026-05-24  
Verdict source: Referee final close verdict, 2026-05-24.  
Initial pass commit accepted: `0d2b4aa` on origin/main.

## Verdict

**CLOSED AS RUNTIME-VERIFIED FOR TESTED PATHS / RESIDUAL BLOCKERS PRESERVED.**

- Decision: option **A** (close as runtime-verified).
- More precisely: tested runtime paths verified; residual blockers preserved.
- Not a strategy pass. Not a production-readiness pass. Not a full-market
  execution-readiness pass.
- No additional runtime pass required now.
- No residual blocker patch phase auto-started.
- No strategy testing reopened.
- No performance diagnostics reopened.
- No production / paper / P08 / live readiness / shadow-track work touched.

## Accepted scope

- Measurement-layer infrastructure audit only.
- Runtime verification only.
- No strategy testing.
- No performance diagnostics.
- No production / paper / P08 / live / shadow.

## Accepted deliverables (9)

1. `runtime_mask_referee_lock.md`
2. `runtime_pipeline_inventory.csv` — 9 KR runtime nodes
3. `synthetic_invalid_row_test_report.md`
4. `real_invalid_row_spot_check.md`
5. `backtest_entry_fail_closed_check.md`
6. `universe_path_mask_propagation_check.md`
7. `feature_path_guard_check.md`
8. `residual_blocker_runtime_status.csv` — 45 residual blockers classified
9. `runtime_mask_propagation_summary.md`

## Accepted runtime findings

- **Synthetic invalid-row tests: 10/10 passed** (S1-S5 + missing-mask coverage across
  guard utility, equity_panel loader, universe builder, backtest engine entry,
  sector_aggregator, market_flow loader).
- **Real invalid-row spot check** on
  `kiwoom_dynamic_top100_2010_2016_panel.csv` (1,093,386 rows):
  - 11,425 invalid rows detected.
  - Exact match with prior P1 OHLCV invariant audit nonpositive finding.
  - `apply_ohlcv_quarantine(mode="filter")` drops 11,425 rows.
- **Backtest entry fail-closed**:
  - `run_candidate_backtest` raises `OhlcvQuarantineError` when `valid_ohlcv_mask` is
    missing.
  - Annotated panel accepted at the quarantine gate.
- **Universe path fail-closed**:
  - `build_execution_universe` raises `ValueError` when `valid_ohlcv_mask` is missing.
  - Accepts annotated panel; filters invalid rows internally.
- **Feature guard check**:
  - `src/features/stock_rs_score.py` records
    `require_guarded_field_use("daily_return", ...)` at runtime.
  - Other feature builders remain `upstream_guarded` under the patch-phase decision.
- **Residual blockers**:
  - 45 entries classified by `runtime_status` (closed strategy paths, closed ops
    paths, engine-internal dormant paths, ad-hoc script paths).
  - None deleted, none downgraded.
  - All retain `reopen_blocker=true`.

## No source-code patching

- No source-code patches were required or performed in this verification phase.
- All findings are observational based on real execution of the patch-phase guards.

## Runtime verification is limited to tested paths

This phase confirms runtime propagation for:
- the guard utility (`src/utils/ohlcv_quarantine.py`),
- the equity panel loader (`src/data/equity_panel.py`),
- the universe builder (`src/data/universe.py`),
- the sector aggregator's `_read_panel` (`src/data/sector_aggregator.py`),
- the market_flow loader (`src/data/market_flow.py`),
- the backtest engine entry (`src/backtest/engine.py:run_candidate_backtest`),
- the patched feature builder (`src/features/stock_rs_score.py`).

It does NOT certify:
- all possible future strategy paths,
- the 45 residual blockers being safe to reactivate,
- any P08 / paper / production / live readiness work,
- full-market execution readiness,
- any return / NAV / Sharpe / alpha / strategy metric.

## Residual blockers — preserved (Referee directive)

45 rows remain blockers for any future strategy or ops reopen. They are NOT deleted,
NOT suppressed, NOT downgraded, NOT reinterpreted.

`residual_blocker_runtime_status.csv` enumerates all 45 with runtime classification:
- `runtime_dormant_strategy_path` (closed strategies),
- `runtime_dormant_ops_path` (closed ops, production locked),
- `runtime_dormant_backtest_internal` (engine internals — unreachable without gated
  entry),
- `runtime_dormant_script` (ad-hoc scripts).

## Possible future phases (none active)

| Phase id | Purpose | Status |
|---|---|---|
| `KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE` | Address the 45 residual blockers | NOT approved (most natural next if priority = reducing blockers before strategy work) |
| `KR-CLOSED-STRATEGY-CODEPATH-QUARANTINE-A0` | Direct audit of closed-strategy paths before any reopen | NOT approved |
| `KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0` | Acquire authoritative KRX calendar | NOT approved (most natural next if priority = execution-simulation readiness) |
| `KR-LISTED-UNIVERSE-COVERAGE-A0` | DATA BACKLOG, source not acquired | NOT approved |
| `KR-EXECUTABLE-STATUS-COVERAGE-A0` | DATA BACKLOG, source not acquired | NOT approved |

Referee note: do NOT auto-start any future phase. Strategy testing remains **premature**.

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

`KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0` is **closed as RUNTIME-VERIFIED FOR TESTED PATHS
/ RESIDUAL BLOCKERS PRESERVED**. No active work remains. Await explicit user / Referee
decision for any future residual blocker, calendar source, listed-universe,
executable-status, parser, or strategy phase.
