# H002 — USDKRW OFF Sleeve

H000 found that D013 OFF quarters had positive USDKRW movement on average,
meaning KRW weakened and USD cash would gain in KRW terms. H002 tests whether
replacing D013's zero-return OFF cash sleeve with USD cash marked by USDKRW
quarter-to-quarter movement is a useful sleeve candidate.

## Specification

- Carrier: D013 top 5, unchanged.
- ON quarters: existing D013 top 5 logic, unchanged.
- OFF quarters: hold USD cash, translated to KRW.
- USD short-term carry: 0.0, conservative simplification.
- FX source: `research_input_data/inputs/macro_features/fred_dexkous_usdkrw.csv`.
- FX return: `USDKRW(T+1Q) / USDKRW(T) - 1`.
- Timing: signal date T executes from T+1 KRX trading day. The FX contribution
  is measured over the exact quarter interval `[T, T+1Q]`, never as same-day
  execution alpha.

## Constraints

- Do not modify D013 strategy.
- Do not modify `src/backtest/engine.py`.
- Do not modify D-G, P, H000, or H001 experiment outputs.
- Add H002 code only through a new strategy module, config, dispatcher branch,
  and tests.

## Pre-Registered Verdict

PASS if all hold:

- Cumulative net return improves versus D013 baseline.
- Sharpe is at least 0.53.
- MDD worsens by no more than 5 percentage points versus D013.
- USDKRW sleeve-only drawdown is not worse than -5%.

## Required Outputs

- `reports/experiments/H002_usdkrw_sleeve/config.yaml`
- `reports/experiments/H002_usdkrw_sleeve/metrics.json`
- `reports/experiments/H002_usdkrw_sleeve/trades.csv`
- `reports/experiments/H002_usdkrw_sleeve/signals.csv`
- `reports/experiments/H002_usdkrw_sleeve/equity_curve.csv`
- `reports/experiments/H002_usdkrw_sleeve/baseline_comparison.csv`
- `reports/experiments/H002_usdkrw_sleeve/off_fx_contribution.csv`
- `reports/experiments/H002_usdkrw_sleeve/regime_breakdown.csv`
- `reports/experiments/H002_usdkrw_sleeve/report.md`
