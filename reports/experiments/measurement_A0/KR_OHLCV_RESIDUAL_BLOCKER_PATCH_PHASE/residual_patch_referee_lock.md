# KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE — Referee Lock

Date: 2026-05-24  
Verdict source: Referee verdict opening this phase, 2026-05-24.  
Predecessor: KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0 CLOSED AS RUNTIME-VERIFIED FOR
TESTED PATHS / RESIDUAL BLOCKERS PRESERVED (commit `08c43c6`).

## Scope (Referee-fixed)

- Measurement-layer infrastructure patch phase only.
- Patch or explicitly hard-block the 45 residual blockers.
- No strategy testing.
- No performance diagnostics.
- No production / paper / P08 / live readiness / shadow.

## 45 residual blockers (initial distribution)

By runtime_status (from runtime-phase classification):

| runtime_status | count |
|---|---:|
| runtime_dormant_strategy_path | 40 |
| runtime_dormant_ops_path | 4 |
| runtime_other (future_work) | 1 |

By severity:

| severity | count |
|---|---:|
| high (INVALID_ROW_LEAK origin) | 18 |
| medium (MISSING_GUARD origin) | 27 |

By file (top concentrations):

| file | defects |
|---|---:|
| src/strategies/p002_d013_execution.py | 14 |
| src/strategies/b004_regime_gate.py | 10 |
| src/strategies/p003_d013_cost_capacity.py | 4 |
| src/strategies/c003_monthly_macro_gate.py | 4 |
| src/strategies/baselines.py | 4 |
| src/strategies/d004_position_sizing.py | 4 |
| src/ops/nav_update.py | 4 |
| src/data/pit_sector_aggregator.py | 1 |

## Patch status taxonomy

- `patched` — explicit local guard or fail-closed assertion added in this phase.
- `upstream_guarded` — already covered by runtime-verified upstream gate, documented
  with cited evidence.
- `still_reopen_blocker` — path remains unsafe or intentionally inactive.
- `audit_only_no_patch_needed` — path does not consume OHLCV values (evidence
  required).
- `not_patched_requires_future_work` — patch deferred to a separate phase.
- `false_positive_static_scan` — verified false positive (evidence required).

## Pass criteria

- All 45 residual blockers have updated `patch_status`.
- Any patched path has evidence.
- Any upstream_guarded path cites the upstream guard.
- Any still_reopen_blocker remains visible.
- The 1 future_work item resolved or explicitly scoped.
- No strategy path reopened.
- No ops/live/paper path activated.
- No performance metric generated.
- No blocker deleted, suppressed, or downgraded without evidence.

## Fail gates

- Any residual blocker removed without evidence.
- Any closed strategy path treated as active or safe-to-use.
- Any ops/paper/live path activated.
- Any invalid OHLCV row enters a reopened or reopenable path without guard.
- Any return / NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD produced.
- Any strategy test started.
- Any production / paper / P08 / live readiness / shadow-track work touched.
- Any patch claims strategy-readiness.

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

- Residual blocker hardening.
- Passing this phase does NOT reopen any strategy.
- Passing this phase does NOT authorize performance diagnostics.
- Passing this phase does NOT make P08 / paper / production / live readiness eligible.
- Expected improvement: fewer residual blockers OR clearer blocker classification.

## End condition

- Return residual blocker patch phase report only.
- Do not recommend strategy testing.
- Do not recommend production or paper tracking.
- Referee will decide whether to:
  - A. close as residual blockers reduced,
  - B. require another residual patch pass,
  - C. open KRX calendar source acquisition,
  - D. keep all strategy research closed.
