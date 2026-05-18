# F011 Layer 3 Composite Champion Registration

## Hypothesis

F010-A is the best F006-F010 Layer 3 composite candidate and should be
formally registered before validation, despite being materially weaker than
the F001-A neutral baseline.

## Specification

- Exact strategy: F010-A.
- Carrier: D013 direct.
- Score: F010 composite
  `average(D013 direct RS, RS + Flow confirmation, RS + Liquidity confirmation)
  - extreme volatility penalty`.
- Final stock score is cross-sectionally z-scored on each signal date.
- Selection: top 5 stocks.
- Costs: base model only.
- No new weights, windows, K, allocation, or macro variables.

## Pre-Registered Context

- F010-A is the best F006-F010 result:
  cumulative net +35%, Sharpe 0.08, IC t-stat 3.69.
- F001-A baseline cumulative net is +254%.
- F010-A is therefore only about 14% of F001-A and is expected to remain weak.

## Outputs

`reports/experiments/F011_layer3_composite_champion/`

