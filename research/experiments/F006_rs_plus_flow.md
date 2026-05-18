# F006 RS + Foreign Flow

## Hypothesis

Layer 3 stock relative strength may be improved by simple foreign flow
confirmation, but Layer 2 E006 suggests flow may dilute RS.

## Specification

- Score: average of stock RS score and stock foreign flow score.
- Normalize final score within sector on each signal date.
- Carriers: D013 direct and E014 top-4 sector carrier.
- Compare against F001 baseline and F002-F005 single-variable candidates.
- IS/OOS split, costs, regime gate, universe, panels: inherit F002-F005.

## Outputs

`reports/experiments/F006_rs_plus_flow/`

