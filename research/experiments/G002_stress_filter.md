# G002 Stress Filter

## Objective

Test a macro/market stress exposure filter as the final Layer 4 risk overlay attempt on the registered D013 and E014 carriers.

## Carriers

- D013: `D013_d009_threshold_minus_0p2`
- E014: `E014_rs_breadth_top4_registration`

## Pre-registered Variables

- `VIX_z`: VIX 60-trading-day z-score. VIX uses the existing U.S. after-close timing policy, so Korean signal date T can only see VIX observations from T-1 or earlier.
- `USDKRW_z`: USDKRW year-over-year change z-score, with a 252-trading-day year-over-year lookback and 60-trading-day z-score window.
- `KOSPI_vol_z`: z-score of the 60-trading-day standard deviation of `cap_weighted_return` from `research_input_data/inputs/macro_features/krx_market_breadth_kospi_2010_2026.csv`.
- `stress_score`: average of `VIX_z`, `USDKRW_z`, and `KOSPI_vol_z`.

## Rule

For each quarterly signal date T:

- If `stress_score < 1.0`, `exposure_scalar = 1.0`
- If `1.0 <= stress_score <= 2.0`, linearly scale exposure from 1.0 to 0.5
- If `stress_score > 2.0`, `exposure_scalar = 0.5`

The scalar is computed from information available through signal date T and applied only to T+1 or later execution weights.

## Overlap Note

This partially overlaps D013's macro gate because both use VIX and USDKRW. This ticket is a confirmation test, not a new alpha layer.

## Constraints

- Do not modify `src/backtest/engine.py`.
- Do not modify existing D013 or E014 strategy files.
- Implement partial exposure at the G002 strategy-wrapper level.
- Do not use future data.
- KOSPI realized volatility must be computed from `cap_weighted_return` in `krx_market_breadth_kospi_2010_2026.csv`.
- Existing D001-D015, E003-E015, F002-F012, G000, and G001 outputs must remain byte-identical.

## Implementation Targets

- Feature: `src/features/stress_filter.py`
- Strategies:
  - `src/strategies/g002_stress_d013.py`
  - `src/strategies/g002_stress_e014.py`
- Configs:
  - `configs/backtests/g002_d013.yaml`
  - `configs/backtests/g002_e014.yaml`

## Required Outputs

Write all outputs under `reports/experiments/G002_stress_filter/`:

- `D013_stress/`
- `E014_stress/`
- `baseline_comparison.csv`
- `stress_scalar_timeseries.csv`
- `report.md`

Each carrier subdirectory must include the standard backtest outputs: `config.yaml`, `metrics.json`, `trades.csv`, `signals.csv`, `equity_curve.csv`, `quarterly_year_breakdown.csv`, `subperiod_breakdown.csv`, `quarterly_regime_log.csv`, `stress_scalars.csv`, and `report.md`.

## Decision Rule

Effective if:

- MDD improves by at least 5 percentage points versus the carrier baseline, and
- cumulative return declines by no more than 50 percentage points versus the carrier baseline.
