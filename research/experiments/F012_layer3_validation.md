# F012 Layer 3 Composite Validation

## Hypothesis

F011, the formally registered F010-A composite champion, should fail full
Layer 3 validation because its realized performance is far below F001-A even
before robustness stress.

## Specification

Validate the frozen F011 candidate set only:

- Cost stress: base, 2x, 3x.
- Spike exclusion: 2020, 2025, 2026, and 2020+2025+2026.
- Year contribution and stock/sector/rebalance contribution.
- D013 and E014 overlap.
- Top-K stability: K=5 exact frozen baseline only.

No new parameters may be adopted from F012.

## Pass/Fail Reference

F011 must at minimum beat F001-A on cumulative net, Sharpe, and drawdown to
justify continuing Layer 3. It is expected to fail all material comparisons.

## Outputs

`reports/experiments/F012_layer3_validation/`

