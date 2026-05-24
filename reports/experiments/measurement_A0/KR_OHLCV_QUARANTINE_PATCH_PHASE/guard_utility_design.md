# Guard Utility Design — `src/utils/ohlcv_quarantine.py`

Date: 2026-05-24  
Phase: KR-OHLCV-QUARANTINE-PATCH-PHASE.  
Status: design + implementation spec; the module itself is implemented in
`src/utils/ohlcv_quarantine.py` and exercised by `tests/test_ohlcv_quarantine.py`.

## Purpose

A small, reusable layer that:

- detects the S1–S6 signatures from `invalid_ohlcv_row_contract.md`,
- returns either a boolean mask or a filtered dataframe,
- fails closed on missing required columns,
- enforces ALLOW_WITH_GUARD field documentation at the call site.

The module is **measurement-layer infrastructure**. It does NOT compute returns,
signals, NAVs, or any strategy output.

## Public surface

```python
from src.utils.ohlcv_quarantine import (
    invalid_ohlcv_mask,
    apply_ohlcv_quarantine,
    assert_no_invalid_ohlcv,
    require_guarded_field_use,
    INVALID_ROW_REASON_CODES,
    DEFAULT_PRICE_COLS,
    DEFAULT_ADJUSTED_PRICE_COLS,
    DEFAULT_VOLUME_COL,
    DEFAULT_VALUE_COL,
)
```

## Function contracts

### `invalid_ohlcv_mask(df, *, price_cols=None, volume_col=None, value_col=None, value_flag_col=None, mode="any") -> pd.Series`

- Returns a boolean `pd.Series` indexed identically to `df`.
- `True` means the row is INVALID (matches at least one of S1–S6 depending on the
  columns provided).
- If `price_cols` is None, defaults to `["시가", "고가", "저가", "종가"]` if any of
  those exist in `df`, otherwise `["adj_open", "adj_high", "adj_low", "adj_close"]`.
- If `volume_col` is None, defaults to `"거래량"` or `"adj_volume"` if either exists.
- If `value_col` is None and the column exists, S4 + S5 use `"거래대금추정"` /
  `value_flag_col=`"거래대금추정여부"`.
- `mode="any"` (default): row is invalid if ANY signature matches.
- `mode="all"` (rare): row is invalid only if ALL provided signatures match.
- Fails closed if no candidate price column is found.

### `apply_ohlcv_quarantine(df, *, mode="filter") -> pd.DataFrame`

- `mode="filter"`: returns `df[~invalid_ohlcv_mask(df)]` (drops invalid rows).
- `mode="mask"`: returns a copy of `df` with all price / volume / value columns set
  to NaN on invalid rows. Row count preserved.
- `mode="annotate"`: returns a copy of `df` with three added columns:
  - `valid_ohlcv_mask` (bool; True where row is VALID),
  - `invalid_ohlcv_reason_codes` (string; pipe-joined S1..S6 hits),
  - `ohlcv_quarantine_run_at` (ISO datetime string of the run).
- Defaults to `"filter"`. Other modes require explicit opt-in.

### `assert_no_invalid_ohlcv(df, *, context: str) -> None`

- Raises `OhlcvQuarantineError` if any row in `df` matches an invalid signature.
- Error message contains the `context` argument and the first 10 offending row IDs.
- Used at the entry of any value-bearing computation as a hard gate.

### `require_guarded_field_use(field_name: str, context: str) -> None`

- Records an annotation in the in-memory log that the caller acknowledges using a
  field marked `ALLOW_WITH_GUARD` (per the P0-1 contract) and has applied the guard.
- The annotation is emitted to a module-level list `_GUARD_ACK_LOG` so test suites
  can verify the contract.
- No side effect on the dataframe. The function exists to enforce documentation, not
  to perform the guard itself.

## S1–S6 signature mapping

| Signature | Detection rule (default columns) |
|---|---|
| S1 vendor_non_trading_forward | `open == 0 AND high == 0 AND low == 0 AND close > 0` |
| S2 nonpos_price | any of `{open, high, low, close} <= 0` |
| S3 ohlc_order_violation | `high < low` OR `high < open` OR `high < close` OR `low > open` OR `low > close` |
| S4 neg_volume_or_value | `volume < 0` OR `value < 0` |
| S5 tv_estimated_mismatch | when `value_flag_col == True`: `abs(value − close × volume) / abs(close × volume) > 1e-6` |
| S6 adj_missing | adjusted columns required but null while raw `종가` exists |

The function:
- skips signatures whose required columns are absent (e.g., if `value_flag_col` is None,
  S5 is not evaluated).
- never silently converts `NaN <= 0` (always False) into "valid" — `NaN` price columns
  fail closed: the row gets `S2_nonpos_price` because price metadata is missing for
  that row.

## Fail-closed semantics

- If `price_cols` is provided but at least one referenced column is absent from `df`,
  raise `OhlcvQuarantineError`.
- If `price_cols` is None and no candidate column is found, raise.
- If `mode` is not one of `{"filter", "mask", "annotate"}`, raise `ValueError`.
- If `df` is None or not a DataFrame, raise `TypeError`.

## Constants

- `INVALID_ROW_REASON_CODES`: `("S1_vendor_non_trading_forward", "S2_nonpos_price",
  "S3_ohlc_order_violation", "S4_neg_volume_or_value", "S5_tv_estimated_mismatch",
  "S6_adj_missing")`.
- `DEFAULT_PRICE_COLS = ("시가", "고가", "저가", "종가")`.
- `DEFAULT_ADJUSTED_PRICE_COLS = ("adj_open", "adj_high", "adj_low", "adj_close")`.
- `DEFAULT_VOLUME_COL = "거래량"`.
- `DEFAULT_VALUE_COL = "거래대금추정"`.
- `DEFAULT_VALUE_FLAG_COL = "거래대금추정여부"`.

## Error type

- `class OhlcvQuarantineError(RuntimeError): pass`. Distinct from generic exceptions so
  call sites can choose to handle, but the default behaviour is to let it propagate.

## Logging

- `_GUARD_ACK_LOG: list[tuple[str, str]]` — module-level. Captures `(field_name, context)`
  every time `require_guarded_field_use` is called.
- Exposed via `get_guard_ack_log()` for tests / audit.
- Not thread-safe (intentional — patch phase scope only).

## Test coverage (see `tests/test_ohlcv_quarantine.py`)

The test suite must exercise:

1. S1 detection on synthetic OHL=0 / close>0 rows.
2. S2 detection on nonpositive open/high/low/close.
3. S3 detection on ordering violations (each of the 5 rules).
4. S4 detection on negative volume and negative trading value.
5. S5 detection on `거래대금추정여부 == True` rows where `거래대금추정 != close × volume`.
6. S6 detection on rows where adjusted columns are required but absent.
7. Fail-closed: missing required columns raise `OhlcvQuarantineError`.
8. `apply_ohlcv_quarantine(mode="filter")` reduces row count correctly.
9. `apply_ohlcv_quarantine(mode="mask")` preserves row count and NaNs the right columns.
10. `apply_ohlcv_quarantine(mode="annotate")` adds the three annotation columns.
11. `assert_no_invalid_ohlcv` raises on bad rows, passes on clean rows.
12. `require_guarded_field_use` appends to `_GUARD_ACK_LOG`.

## Cross references

- `invalid_ohlcv_row_contract.md` (S1–S6 specification)
- `required_patch_register.md` (10 patch families)
- `invalid_row_leak_defect_ledger.csv` (143 defects)
- `field_allowlist_denylist.csv` (ALLOW_WITH_GUARD list)

## Hard locks

- The guard module MUST NOT compute returns, signals, NAVs, or any strategy output.
- The guard module MUST NOT bypass the invalid-row contract.
- The guard module MUST NOT reinterpret a quarantined row as valid via `fillna(0)`,
  `ffill`, or any silent transformation.
