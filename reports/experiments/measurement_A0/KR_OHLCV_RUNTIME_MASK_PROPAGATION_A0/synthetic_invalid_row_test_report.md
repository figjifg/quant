# Synthetic Invalid-Row Test Report

Date: 2026-05-24  
Phase: KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0  
Method: each test constructs a synthetic dataframe with known invalid OHLCV
signatures and runs it through an actual runtime path. Outcome is recorded.

## Headline: **10/10 tests passed**

## Per-test results

| test_id | pipeline | signature | expected | observed | passed |
|---|---|---|---|---|---|
| T01 | `src/utils/ohlcv_quarantine.py: invalid_ohlcv_mask` | S1-S5 mixed | invalid mask for rows 1-5; row 0 valid | mask=[False, True, True, True, True, True] | PASS |
| T02 | `src/utils/ohlcv_quarantine.py: apply_ohlcv_quarantine(mode='filter')` | S1-S5 mixed | single row remaining (row 0) | 1 rows remaining | PASS |
| T03 | `src/utils/ohlcv_quarantine.py: apply_ohlcv_quarantine(mode='annotate')` | S1-S5 mixed | rowcount preserved + valid_ohlcv_mask+invalid_ohlcv_reason_codes+ohlcv_quarantine_run_at added | rowcount=6, annotation_cols_present=True | PASS |
| T04 | `src/utils/ohlcv_quarantine.py: assert_no_invalid_ohlcv` | S1-S5 mixed | raises OhlcvQuarantineError | OhlcvQuarantineError raised | PASS |
| T05 | `src/data/equity_panel.py: load_equity_panel (apply_ohlcv_quarantine inline)` | S1-S5 mixed | valid_ohlcv_mask column present; 1 valid row | mask_present=True, n_valid=1 | PASS |
| T06 | `src/backtest/engine.py: run_candidate_backtest` | missing valid_ohlcv_mask | raises OhlcvQuarantineError | OhlcvQuarantineError raised: run_candidate_backtest received a panel without `valid_ohlcv_mask`; load via src.data.equity_panel.load_equity_panel whi | PASS |
| T07 | `src/data/universe.py: build_execution_universe` | missing valid_ohlcv_mask | raises ValueError referencing valid_ohlcv_mask | ValueError: panel missing `valid_ohlcv_mask` from loader; use src.data.equity_panel.load_equity_panel which annotates it | PASS |
| T08 | `src/data/universe.py: build_execution_universe` | mixed valid + invalid rows (mask present) | completes without exception; filters invalid rows internally | OK; output rows=0 | PASS |
| T09 | `src/data/sector_aggregator.py: _read_panel` | S1 OHL=0 / close>0 | invalid row dropped (mode='filter') | sector_aggregator _read_panel kept 1 rows (expected 1) | PASS |
| T10 | `src/data/market_flow.py: load_market_flow` | ALLOW_WITH_GUARD field use | require_guarded_field_use logged for kospi_foreign_net + kospi_institution_net | guard_ack_log fields: ['kospi_foreign_net', 'kospi_institution_net'] | PASS |

## Pipelines covered

- `src/utils/ohlcv_quarantine.py` (guard module): T01-T04
- `src/data/equity_panel.py` (loader): T05
- `src/backtest/engine.py` (entry gate): T06
- `src/data/universe.py` (universe builder): T07-T08
- `src/data/sector_aggregator.py` (sector loader): T09
- `src/data/market_flow.py` (ALLOW_WITH_GUARD ack): T10

## Hard locks (preserved)

- No return / NAV / Sharpe / alpha / strategy metric.
- No performance diagnostic.
- No production / paper / P08 / live / shadow.
