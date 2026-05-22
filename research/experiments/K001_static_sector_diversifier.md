# K001 Static Sector Diversifier

Status: BACKLOG (after K000)

## Purpose

Extend the N-family candidate library by testing whether a small static
defensive sector sleeve improves `P08_IEF30` stress behavior.

## Pre-registered Candidates

Defensive sectors only:

| Candidate | Definition |
|---|---|
| K001-A | `P08_IEF30` + XLP 5% |
| K001-B | `P08_IEF30` + XLP 10% |
| K001-C | `P08_IEF30` + XLU 5% |
| K001-D | `P08_IEF30` + XLU 10% |
| K001-E | `P08_IEF30` + XLV 5% |
| K001-F | `P08_IEF30` + XLV 10% |

Sector sleeves are funded by proportional reduction from SPY / QQQ / H001 /
IEF unless a later ticket explicitly overrides that implementation detail.

## Comparison

Use the same N-family stress matrix:

- GFC.
- 2022.
- COVID.
- Dot-com.

## Prohibited

- Other sectors in this ticket.
- XLE, XLF, XLK, and similar momentum candidates.
- Parameter grid.
- Rotation timing.

Other sector or momentum candidates belong only to K002.
