# H001 KR Short Rate Baseline Sleeve

## Portfolio Metrics

| variant | cumulative_net_total_return | sharpe | max_drawdown |
|---|---:|---:|---:|
| D013 baseline | 2.2994412001168385 | 0.5017312487668135 | -0.34235547651133513 |
| D013 + KR carry | 3.2542718250575646 | 0.6139370561780421 | -0.34235547651133524 |

## OFF Carry

- OFF carry cumulative contribution: 0.2893916172552795
- OFF carry quarters: 38

## Verdict

- Overall: PASS
- Cumulative uplift >= 0.20: True (0.9548306249407261)
- Sharpe >= D013: True (0.11220580741122854)
- MDD worsening <= 0.03: True (-1.1102230246251565e-16)

## Metadata

- Carrier: D013 top 5 unchanged.
- OFF sleeve: KR short-rate carry replaces zero-return cash in D013 OFF quarters.
- KR short-rate source: research_input_data/inputs/macro_features/fred_kr_short_rate.csv.
- Carry formula: `(1 + annual_rate / 12)^3 - 1`, with annual_rate as decimal.
- D013 strategy and backtest engine were not modified.
