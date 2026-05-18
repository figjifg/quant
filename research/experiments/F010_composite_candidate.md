# F010 Composite Candidate

## Hypothesis

The best Layer 3 candidate may combine RS, flow confirmation, and liquidity
confirmation while avoiding extreme volatility.

## Specification

- Score: average(RS, RS + flow confirmation, RS + liquidity confirmation)
  minus extreme volatility penalty.
- Flow confirmation follows F007.
- Liquidity and volatility confirmation follows F009.
- Normalize final score within sector on each signal date.
- Carriers: D013 direct and E014 top-4 sector carrier.

## Outputs

`reports/experiments/F010_composite_candidate/`

