# X-Lab

X-Lab is a quarantined alpha research lab.

The main `P08_IEF30` project is frozen and must not be modified by X-Lab
results. X-Lab exists to run diagnostic research, fail quickly when needed,
and keep experimental evidence separate from production tracking.

## Quarantine Rules

- X-Lab results do not change `P08_IEF30` weights.
- X-Lab results do not add paper-tracking candidates to P08.
- X-Lab results are not called production candidates before the Import Gate.
- X-Lab work is diagnostic only until the full audit gate passes.
- Import into the main project requires separate user approval and a separate
  import ticket.

## First Track

`x_etf/` is the X-ETF Global Tactical ETF Lab. Its first task is
`X-ETF000`: data audit and baseline board only. No strategy optimization is
authorized in `X-ETF000`.
