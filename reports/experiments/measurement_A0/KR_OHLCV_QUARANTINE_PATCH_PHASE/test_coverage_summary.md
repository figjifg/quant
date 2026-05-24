# Test Coverage Summary

Date: 2026-05-24  
Phase: KR-OHLCV-QUARANTINE-PATCH-PHASE.

## Test file

- `tests/test_ohlcv_quarantine.py`
- Test functions: **19**
- Status (last run): **all passed** (19/19) — see `pytest tests/test_ohlcv_quarantine.py`

## Coverage of guard utility surface

| Tested behaviour | Function | Test |
|---|---|---|
| S1 OHL=0 / close>0 detection | `invalid_ohlcv_mask` | `test_s1_vendor_non_trading_forward` |
| S2 non-positive price detection | `invalid_ohlcv_mask` | `test_s2_nonpos_price`, `test_nan_price_fails_closed_via_s2` |
| S3 OHLC ordering violations | `invalid_ohlcv_mask` | `test_s3_ordering_violations` |
| S4 negative volume/value | `invalid_ohlcv_mask` | `test_s4_negative_volume_or_value` |
| S5 vendor TV estimation mismatch | `invalid_ohlcv_mask` | `test_s5_tv_estimated_mismatch` |
| S6 missing adjusted overlay | `invalid_ohlcv_mask` | `test_s6_adjusted_missing` |
| Fail-closed on missing price columns | `_choose_price_cols` | `test_fail_closed_on_missing_price_cols`, `test_fail_closed_on_explicit_missing_col` |
| Filter mode drops invalid rows | `apply_ohlcv_quarantine(mode='filter')` | `test_apply_filter_drops_invalid_rows` |
| Mask mode preserves row count | `apply_ohlcv_quarantine(mode='mask')` | `test_apply_mask_preserves_rowcount_nan_invalid` |
| Annotate mode adds 3 columns | `apply_ohlcv_quarantine(mode='annotate')` | `test_apply_annotate_adds_three_columns` |
| Assert passes on clean rows | `assert_no_invalid_ohlcv` | `test_assert_passes_on_clean_rows` |
| Assert raises on invalid rows | `assert_no_invalid_ohlcv` | `test_assert_raises_on_invalid_rows` |
| Guard ack log captures field+context | `require_guarded_field_use` | `test_require_guarded_field_use_appends_log` |
| Guard ack log rejects empty input | `require_guarded_field_use` | `test_require_guarded_field_use_rejects_empty` |
| Invalid mode raises ValueError | `apply_ohlcv_quarantine` / `invalid_ohlcv_mask` | `test_mode_invalid_raises_value_error` |
| Non-DataFrame raises TypeError | `apply_ohlcv_quarantine` / `invalid_ohlcv_mask` | `test_non_dataframe_raises_type_error` |
| Adjusted-only panel auto-resolves cols | `_choose_price_cols` | `test_adjusted_only_panel_resolves_default_cols` |

## What is NOT covered

- Runtime mask propagation across the full data pipeline (separate future phase).
- Performance / NAV / return-bearing pipelines (forbidden under Referee lock).
- Strategy-level integration tests against the guard utility (strategies CLOSED).
