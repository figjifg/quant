# Future Work Item Resolution

Date: 2026-05-24  
Phase: KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE  

## Future_work items identified: 1

### QENF_00042 — `src/data/pit_sector_aggregator.py` line 215

- Severity: medium
- Column: `daily_return`
- Runtime status at runtime phase: `runtime_other`
- Pre-runtime patch_status: `not_patched_requires_future_work`

### Resolution decision

**New patch_status**: `false_positive_static_scan`

**Evidence:**

callsite at line 215 is a column-name reference inside a .loc[:, columns] selection list (output schema declaration), not a value-bearing read; data already filtered upstream by src/data/sector_aggregator.py:_read_panel via apply_ohlcv_quarantine(mode='filter') — see future_work_item_resolution.md

### Why this resolves the future_work flag

`src/data/pit_sector_aggregator.py` line 215 references the string
`'daily_return'` as a column-name entry inside a `.loc[:, columns]`
selection list. The line is:

```python
columns = [
    ...
    "institution_net_buy_shares",
    "daily_return",   # ← line 215: column name in selection list
]
return joined.loc[:, columns].sort_values(["date", "ticker"]).reset_index(drop=True)
```

This is a **column-name reference**, not a value-bearing read or
transformation. The `daily_return` column itself enters the frame upstream
via `src/data/sector_aggregator.py:_read_panel`, which in this audit/patch
cycle was modified to call `apply_ohlcv_quarantine(mode='filter')` before
the column is renamed. As a result:

- Any invalid OHLCV row (S1-S6) is dropped upstream before `daily_return`
  is computed.
- The line-215 reference selects from an already-filtered frame.
- No additional local guard is required.

Classification: `false_positive_static_scan` (with `upstream_guarded` as
secondary characterisation).

### Future-phase implication

If a future runtime-mask propagation check is performed on the PIT sector
aggregator specifically, it should re-verify that the upstream
`_read_panel` filter is in effect for both the standard and PIT pipelines.

## Hard locks (preserved)

- No source-code change to `pit_sector_aggregator.py` in this phase.
- No strategy testing.
- No performance metric.
- Closed paths remain closed.
