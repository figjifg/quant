# Feature Path Guard Check

Date: 2026-05-24  
Phase: KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0  
Method: combine static check (feature files with `require_guarded_field_use`
import or call) with a dynamic check on the patched `stock_rs_score` builder.

## Static check — feature files with `require_guarded_field_use`

Files containing the symbol (count: 1):

- `src/features/stock_rs_score.py`

## Dynamic check — `build_stock_rs_scores` records guard ack

- daily_return field guard logged: **True**
- observation: guard_ack_log fields=['daily_return']

## Interpretation

Only `stock_rs_score.py` was explicitly patched with
`require_guarded_field_use`. Other feature builders (`flow_ratios.py`,
`market_gate.py`, `sector_breadth_score.py`, `stock_combined_score.py`,
`stock_liquidity_score.py`) consume the loader-emitted
`valid_ohlcv_mask` annotated panel and rely on **upstream guard**
(see `defect_patch_plan.csv` patch_status = `upstream_guarded`).

The patch phase did NOT add per-feature guard ack annotations to those files
because the loader-side annotation + the engine's fail-closed gate are
sufficient under the audit-only scope of that phase. Runtime mask
propagation in those features therefore depends on the upstream annotation
remaining attached.

## Hard locks (preserved)

- No alpha / momentum / reversal / RS strategy output produced.
- No return-bearing metric computed.
- No production / paper / P08 / live touched.
