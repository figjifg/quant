# H001 — KR Short Rate Baseline Sleeve

## Context

H000 found that D013 OFF quarters are sideways rather than crash-heavy:
average KOSPI return was positive, and KR short-rate carry was positive.
H001 tests whether replacing D013's OFF cash sleeve with KR short-rate carry
improves the frozen D013 carrier.

## Frozen Variables

- Carrier: D013 top 5, unchanged.
- ON quarters: existing D013 top 5 logic, unchanged.
- OFF quarters: KR short-rate carry instead of zero-return cash.
- KR short rate: `research_input_data/inputs/macro_features/fred_kr_short_rate.csv`
  column `IR3TIB01KRM156N`, monthly annual rate.
- Quarterly carry: `(1 + annual_rate / 12)^3 - 1`, with annual rate expressed as a decimal.

## Implementation Constraints

- Do not modify D013 strategy.
- Do not modify `src/backtest/engine.py`.
- Apply sleeve return in H001 strategy code only.
- D/G/P/H000 outputs must not be regenerated or edited.

## Registered Verdict

Pass only if all are true:

- Cumulative net return improves by at least 20 percentage points versus D013.
- Sharpe is at least D013 baseline Sharpe.
- MDD worsens by no more than 3 percentage points versus D013.

Side output:

- Report cumulative OFF carry contribution by quarter.

## Required Outputs

- `reports/experiments/H001_kr_short_rate_sleeve/metrics.json`
- `reports/experiments/H001_kr_short_rate_sleeve/trades.csv`
- `reports/experiments/H001_kr_short_rate_sleeve/signals.csv`
- `reports/experiments/H001_kr_short_rate_sleeve/equity_curve.csv`
- `reports/experiments/H001_kr_short_rate_sleeve/baseline_comparison.csv`
- `reports/experiments/H001_kr_short_rate_sleeve/off_carry_contribution.csv`
- `reports/experiments/H001_kr_short_rate_sleeve/report.md`
