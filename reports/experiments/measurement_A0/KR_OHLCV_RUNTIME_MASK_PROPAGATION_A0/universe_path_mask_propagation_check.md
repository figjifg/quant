# Universe Path Mask Propagation Check

Date: 2026-05-24  
Phase: KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0  
Method: invoke `src/data/universe.py:build_execution_universe` with (1) a
panel missing `valid_ohlcv_mask` and (2) a panel with the annotation present.

## Result table

| case | input | expected | observed | passed |
|---|---|---|---|---|
| 1 | panel without `valid_ohlcv_mask` | raises ValueError referencing mask | PASS — ValueError: panel missing `valid_ohlcv_mask` from loader; use src.data.equity_panel.load_equity_panel which annotates it | PASS |
| 2 | annotated panel | accepts, invalid rows filtered via mask | PASS — annotated panel accepted; output rows=0; 5 invalid rows were excluded via mask filter | PASS |

## Interpretation

- Case 1 confirms the universe builder's fail-closed gate is active at runtime.
- Case 2 confirms invalid rows do not enter universe construction when the mask
  is present; they are removed by the in-function filter.
- No survivorship-safe claim is made; the vendor `동적유니버스포함` flag remains
  ALLOW_WITH_GUARD (per P0-1) and `require_guarded_field_use` is logged.

## Hard locks (preserved)

- No strategy test.
- No performance metric.
- No survivorship-safe claim without official listed universe.
