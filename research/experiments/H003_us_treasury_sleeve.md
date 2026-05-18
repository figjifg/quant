# H003 — US Treasury OFF Sleeve

## Context

H001 passed by replacing D013 OFF cash with KR short-rate carry. H002 failed
because the USDKRW sleeve-only drawdown was too large. H003 tests whether a
simple US 10Y Treasury sleeve, translated to KRW, is a better defensive OFF
asset than USD cash alone.

## Specification

- Carrier: D013 top 5, unchanged.
- ON quarters: existing D013 top 5 logic, unchanged.
- OFF quarters: hold a simple US 10Y Treasury return sleeve in KRW terms.
- US 10Y yield source: `research_input_data/inputs/macro_features/fred_dgs10.csv`.
- USDKRW source: `research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv`.
- Effective duration: 7.0.
- Quarterly USD Treasury return:
  `-delta_yield_decimal * 7 + start_yield_decimal / 4`.
- Quarterly KRW return:
  `duration_return + carry_return + usdkrw_quarter_return`.
- Timing: signal date T executes from T+1 KRX trading day. Treasury and FX
  observations are aligned as-of signal date T and next quarter signal date
  T+1Q. The sleeve return is applied only over the execution window starting
  T+1.

## Constraints

- Do not modify D013 strategy.
- Do not modify `src/backtest/engine.py`.
- Do not modify D-G, P, H000, H001, or H002 experiment outputs.
- Bond model is simple and pre-registered; no parameter optimization.

## Pre-Registered Verdict

PASS if all hold:

- Cumulative net return improves versus D013 baseline cumulative return
  of +254%.
- Sharpe is at least 0.53.
- US Treasury sleeve-only max drawdown is not worse than -10%.
- 2022 rate-rise impact is reported.

## Required Outputs

- `reports/experiments/H003_us_treasury_sleeve/config.yaml`
- `reports/experiments/H003_us_treasury_sleeve/metrics.json`
- `reports/experiments/H003_us_treasury_sleeve/trades.csv`
- `reports/experiments/H003_us_treasury_sleeve/signals.csv`
- `reports/experiments/H003_us_treasury_sleeve/equity_curve.csv`
- `reports/experiments/H003_us_treasury_sleeve/baseline_comparison.csv`
- `reports/experiments/H003_us_treasury_sleeve/treasury_return_decomposition.csv`
- `reports/experiments/H003_us_treasury_sleeve/regime_breakdown.csv`
- `reports/experiments/H003_us_treasury_sleeve/report.md`
