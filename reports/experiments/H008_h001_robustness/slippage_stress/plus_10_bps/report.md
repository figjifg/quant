# H001 KR Short Rate Baseline Sleeve

## Portfolio Metrics

| variant | cumulative_net_total_return | sharpe | max_drawdown |
|---|---:|---:|---:|
| D013 baseline | 2.397253061129656 | 0.5145716123826451 | -0.3390579888103834 |
| D013 + KR carry | 3.380389618715636 | 0.6270123984716415 | -0.3390579888103834 |

## OFF Carry

- OFF carry cumulative contribution: 0.2893916172552795
- OFF carry quarters: 38

## Verdict

- Overall: PASS
- Cumulative uplift >= 0.20: True (0.9831365575859801)
- Sharpe >= D013: True (0.11244078608899633)
- MDD worsening <= 0.03: True (0.0)

## Metadata

- Carrier: D013 top 5 unchanged.
- OFF sleeve: KR short-rate carry replaces zero-return cash in D013 OFF quarters.
- KR short-rate source: research_input_data/inputs/macro_features/fred_kr_short_rate.csv.
- Carry formula: `(1 + annual_rate / 12)^3 - 1`, with annual_rate as decimal.
- D013 strategy and backtest engine were not modified.
