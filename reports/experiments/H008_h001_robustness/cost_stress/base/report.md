# H001 KR Short Rate Baseline Sleeve

## Portfolio Metrics

| variant | cumulative_net_total_return | sharpe | max_drawdown |
|---|---:|---:|---:|
| D013 baseline | 2.5457702903350135 | 0.5333654677635088 | -0.3392346174957135 |
| D013 + KR carry | 3.571886489071015 | 0.6461391042868482 | -0.3392346174957135 |

## OFF Carry

- OFF carry cumulative contribution: 0.2893916172552795
- OFF carry quarters: 38

## Verdict

- Overall: PASS
- Cumulative uplift >= 0.20: True (1.0261161987360015)
- Sharpe >= D013: True (0.11277363652333938)
- MDD worsening <= 0.03: True (0.0)

## Metadata

- Carrier: D013 top 5 unchanged.
- OFF sleeve: KR short-rate carry replaces zero-return cash in D013 OFF quarters.
- KR short-rate source: research_input_data/inputs/macro_features/fred_kr_short_rate.csv.
- Carry formula: `(1 + annual_rate / 12)^3 - 1`, with annual_rate as decimal.
- D013 strategy and backtest engine were not modified.
