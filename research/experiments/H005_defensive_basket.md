# H005 — Defensive Basket OFF Sleeve

## Context

H001 passed with KR short-rate carry, while H002 and H003 failed as standalone
defensive sleeves because single-sleeve drawdowns were too large. H005 tests a
fixed defensive basket for D013 OFF quarters to reduce single-sleeve risk.

## Specification

- Carrier: D013 top 5, unchanged.
- ON quarters: existing D013 top 5 logic, unchanged.
- OFF quarters: hold a fixed defensive basket.
- Basket option: A.
- Basket weights, pre-registered and not optimized:
  - KR short-rate carry: 50%.
  - USDKRW cash: 25%.
  - US 10Y Treasury in KRW: 25%.
- Weights are identical in every OFF quarter.
- KR short-rate source:
  `research_input_data/inputs/macro_features/fred_kr_short_rate.csv`.
- USDKRW source:
  `research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv`.
- US 10Y yield source:
  `research_input_data/inputs/macro_features/fred_dgs10.csv`.
- Treasury effective duration: 7.0.

## Timing

Signal date T executes from T+1 KRX trading day. All component observations are
aligned as-of signal date T and, where needed, the next quarter signal date.
The basket return is applied only over the OFF execution window beginning T+1.

## Constraints

- Do not modify D013 strategy.
- Do not modify `src/backtest/engine.py`.
- Do not edit D-G, P, H000-H003 outputs.
- Basket weights are pre-registered; do not change results after seeing H005.

## Pre-Registered Verdict

PASS if all hold:

- Cumulative D013 + basket return improves versus the D013 baseline threshold
  of +254%.
- Sharpe is at least 0.65.
- Basket sleeve-only max drawdown is not worse than -8%.

## Required Outputs

- `reports/experiments/H005_defensive_basket/config.yaml`
- `reports/experiments/H005_defensive_basket/metrics.json`
- `reports/experiments/H005_defensive_basket/trades.csv`
- `reports/experiments/H005_defensive_basket/signals.csv`
- `reports/experiments/H005_defensive_basket/equity_curve.csv`
- `reports/experiments/H005_defensive_basket/baseline_comparison.csv`
- `reports/experiments/H005_defensive_basket/basket_decomposition.csv`
- `reports/experiments/H005_defensive_basket/regime_breakdown.csv`
- `reports/experiments/H005_defensive_basket/report.md`
