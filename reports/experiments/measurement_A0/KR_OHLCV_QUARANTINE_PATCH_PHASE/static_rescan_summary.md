# Static Rescan Summary

Date: 2026-05-24  
Phase: KR-OHLCV-QUARANTINE-PATCH-PHASE.  
Method: Re-run `src/audit/measurement_a0/p_ohlcv_quarantine_enforcement.py` after patches.

## Headline delta

- **Pre-phase total flagged defects** (INVALID_ROW_LEAK + MISSING_GUARD): 143
- **Post-rescan total flagged defects**: 146
- Delta: +3

## Classification distribution

| classification | pre | post | delta |
|---|---:|---:|---:|
| PASS | 58 | 72 | +14 |
| GUARDED | 346 | 352 | +6 |
| MISSING_GUARD | 92 | 95 | +3 |
| INVALID_ROW_LEAK | 51 | 51 | +0 |
| AMBIGUOUS | 0 | 0 | +0 |
| NOT_APPLICABLE | 416 | 419 | +3 |

## Interpretation

**Static scan limitation accepted.** The scanner classifies callsites by
the presence of guard-pattern keywords within ±5 lines of each column
reference. The patch phase added explicit guard utility calls and module-
level filters at the data-loader boundary, but not every downstream callsite
receives a local ±5-line annotation. As a result:

- Direct patches (`src/data/equity_panel.py`, `market_flow.py`, `universe.py`,
  `sector_aggregator.py`, `backtest/engine.py`, `features/stock_rs_score.py`)
  introduce explicit guard keywords near the column reads and are reflected
  in the post-rescan as GUARDED or PASS where the window catches them.
- Upstream-guarded callsites in `src/features/` and `src/run_experiment.py`
  may still appear as MISSING_GUARD in the rescan because the local ±5-line
  window does not see the loader-level guard.
- Closed-strategy paths in `src/strategies/` and `src/ops/` remain as
  reopen blockers per Referee directive; they were not patched in this
  audit-only phase.

**`defect_patch_plan.csv`** is the authoritative per-defect `patch_status`
assignment. The static-scan re-classification is informational.

## Runtime mask propagation

NOT verified by this phase. Per Referee lock, runtime propagation
verification is a separate future phase (`KR-OHLCV-RUNTIME-MASK-
PROPAGATION-A0`) and is NOT auto-started.
