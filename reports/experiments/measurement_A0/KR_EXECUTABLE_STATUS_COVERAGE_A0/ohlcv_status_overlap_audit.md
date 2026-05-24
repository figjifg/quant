# OHLCV × Executable-Status Overlap Audit

Date: 2026-05-24  
Phase: KR-EXECUTABLE-STATUS-COVERAGE-A0

## W001 v2 `tradable_state` distribution (per-row)

| state | row count |
|---|---:|
| `panel_absence` | 937153 |
| `executable` | 158633 |
| `true_suspension` | 32378 |
| `delisting_transition` | 13448 |
| `data_missing` | 98 |
| `limit_lock_candidate` | 41 |

## Interpretation

Per the invariant contract in
`KR_OHLCV_QUARANTINE_ENFORCEMENT_A0/invalid_ohlcv_row_contract.md`:

- `OHL=0` / `close>0` rows are the vendor non-trading-row signature. These
  are quarantined; they do NOT prove suspension.
- W001 v2 `tradable_state` assigns `true_suspension` to a subset of these,
  but only when the assignment is **backed by an S3 official event**. Rows
  with the signature but no S3 backing remain `panel_absence` or `data_missing`.
- `limit_lock_candidate` is OHLCV-pattern-derived (close = upper-limit or
  lower-limit price). This is a CANDIDATE label, NOT KRX-official.

## Cross-check rule

Any future code path that decides executable status MUST:

1. Consult `tradable_state` AS PROXY.
2. If the row is `true_suspension`, verify the W001 v2 derivation traces
   to an S3 KRX status event.
3. If the row is `limit_lock_candidate`, treat as **candidate-only**; do not
   convert to a definitive executable claim.
4. NEVER use OHL=0 / `close>0` / zero-volume as standalone executable
   evidence.

## Hard locks (preserved)

- OHLCV invariant signatures are NOT executable-status proof.
- `limit_lock_candidate` is NOT official limit-lock data.
- No execution simulation.
