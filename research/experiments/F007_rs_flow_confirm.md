# F007 RS + Flow Confirmation

## Hypothesis

Foreign flow is not an equal-weight alpha source; it is a confirmation
signal for stock RS.

## Specification

- Base: stock RS score.
- Bonus: foreign_flow_20 > 0 and foreign_flow_60 > 0 adds +1.
- Penalty: foreign_flow_20 < 0 and foreign_flow_60 < 0 subtracts 1.
- Missing flow inputs receive no bonus or penalty.
- Normalize final score within sector on each signal date.
- Carriers: D013 direct and E014 top-4 sector carrier.

## Outputs

`reports/experiments/F007_rs_flow_confirm/`

