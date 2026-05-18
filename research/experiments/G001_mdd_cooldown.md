# G001 MDD Cooldown

## Objective

Test a portfolio drawdown-triggered exposure cooldown as a Layer 4 risk overlay on the registered D013 and E014 carriers.

## Carriers

- D013: `D013_d009_threshold_minus_0p2`
- E014: `E014_rs_breadth_top4_registration`

## Pre-registered Parameters

- `drawdown_lookback_days`: 252
- `warning_threshold`: -0.05
- `hard_threshold`: -0.15
- `hard_scalar`: 0.5

## Rule

For each quarterly signal date T:

- `portfolio_drawdown(T) = portfolio_value(T) / max(portfolio_value over past N days) - 1`
- If `portfolio_drawdown >= -0.05`, `exposure_scalar = 1.0`
- If `-0.15 <= portfolio_drawdown < -0.05`, linearly scale exposure from 0.5 to 1.0
- If `portfolio_drawdown < -0.15`, `exposure_scalar = 0.5`
- Recovery to `portfolio_drawdown >= -0.05` restores `exposure_scalar = 1.0`

The scalar is computed from information available through signal date T and applied only to T+1 or later execution weights.

## Constraints

- Do not modify `src/backtest/engine.py`.
- Do not modify existing D013 or E014 strategy files.
- Implement partial exposure at the G001 strategy-wrapper level.
- Do not use future data.
- Existing D001-D015, E003-E015, F002-F012, and G000 outputs must remain byte-identical.

## Implementation Targets

- Feature: `src/features/mdd_cooldown.py`
- Strategies:
  - `src/strategies/g001_mdd_cooldown_d013.py`
  - `src/strategies/g001_mdd_cooldown_e014.py`
- Configs:
  - `configs/backtests/g001_d013.yaml`
  - `configs/backtests/g001_e014.yaml`

## Required Outputs

Write all outputs under `reports/experiments/G001_mdd_cooldown/`:

- `D013_mdd/`
- `E014_mdd/`
- `baseline_comparison.csv`
- `exposure_scalar_timeseries.csv`
- `report.md`

Each carrier subdirectory must include the standard backtest outputs: `config.yaml`, `metrics.json`, `trades.csv`, `signals.csv`, `equity_curve.csv`, `quarterly_year_breakdown.csv`, `subperiod_breakdown.csv`, `quarterly_regime_log.csv`, `mdd_scalars.csv`, and `report.md`.

## Decision Rule

Effective if:

- MDD improves by at least 5 percentage points versus the carrier baseline, and
- cumulative return declines by no more than 50 percentage points versus the carrier baseline.

Baseline references:

- D013: cumulative +254%, Sharpe 0.53, MDD -34%
- E014: cumulative +362%, Sharpe 0.63, MDD -36%
