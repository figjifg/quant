# F009 RS + Liquidity Confirmation

## Hypothesis

Stock RS should perform better when participation is expanding and extreme
volatility is avoided.

## Specification

- Base: stock RS score.
- Bonus: liquidity_change > 1.0 adds +1.
- Penalty: volatility_60d > sector mean + one sector sigma subtracts 1.
- Normalize final score within sector on each signal date.
- Carriers: D013 direct and E014 top-4 sector carrier.

## Outputs

`reports/experiments/F009_rs_liquidity_confirm/`

