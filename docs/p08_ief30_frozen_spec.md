# P08_IEF30 Frozen Specification

Status: FROZEN formal candidate.

## Frozen Portfolio

| Component | Weight |
|---|---:|
| SPY | 29% |
| QQQ | 21% |
| H001 | 20% |
| IEF | 30% |

## Production Assumptions

- Rebalance: quarterly + 0pp no-trade band.
- Confirmation: `T001` + `T002`.
- Lot accounting: HIFO.
- Annual overseas capital-gains exemption: 250만원.
- Practical vehicle: MIX1 practical.
- MIX1 allocation: V1 taxable 50% + ISA 30% + pension 20%.

## Do Not Modify

The following changes are explicitly out of scope:

- No new weights grid.
- No new sleeve added directly into `P08_IEF30`.
- N-family is a separate backlog candidate library, not a direct
  `P08_IEF30` modification path.
- No macro gate.
- `I002` remains on hold.

## Allowed Reconsideration Conditions

The frozen specification may be reassessed only when all of the following
inputs are available:

- Four quarters of paper tracking.
- Tax-professional confirmation.
- N-family stress diversifier validation.
- A live deployment decision point.

Until then, `P08_IEF30` remains unchanged.

## Risk Statement

`P08_IEF30` is frozen as a formal candidate, not because it removes stress
risk. Expected stress vulnerabilities remain material:

- GFC-like regime: approximately -30% to -35% drawdown is possible.
- 2022-like rate shock: approximately -21% drawdown is possible.
- COVID-like equity crash: approximately -20% drawdown is possible.
- Live pilot sizing should start conservatively, for example with only 50-70%
  of total assets allocated to the live pilot.
- Defensive shadow candidates N002-B and N001-B are tracked forward to test
  whether cash 10% or GLD 10% improves stress-period behavior.

These defensive shadows do not modify `P08_IEF30`, do not authorize dynamic
hedging, and are not live allocations.
