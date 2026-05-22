# Risk Statement

## P08_IEF30 Stress Expectations

`P08_IEF30` is not a low-drawdown or hedge-complete portfolio.

Expected stress profile:

| Stress view | Expected MDD |
|---|---:|
| Normal backtest | About -16% |
| GFC-like proxy | About -30% to -35% |
| 2022-like rate shock | About -21% |
| COVID-like crash | About -20% |

These numbers should be treated as planning ranges, not guarantees.

## Defensive Shadow Effect

Defensive shadows may reduce stress drawdown, but they do not fully hedge the portfolio.

| Shadow | Expected GFC-like MDD effect |
|---|---:|
| N002-B cash 10% | About +3.7pp MDD improvement |
| N001-B GLD 10% | About +3.5pp MDD improvement |

Limits:

- They are partial defensive shadows only.
- They can lag in non-GFC stress regimes.
- They do not remove equity, rate, FX, or Korea sleeve risk.

## Live Sizing Guide

Sizing should be controlled at the total-wealth level rather than changing `P08_IEF30` itself.

Guidelines:

- Keep `P08_IEF30` weights frozen during paper tracking.
- Choose the allocation to `P08_IEF30` within total assets, for example 80-90% only after readiness.
- Maintain an external cash buffer of 10-20% in KOFR, MMF, or CMA-like instruments.
- During pilot, use conservative sizing such as 10-30% of total assets in `P08_IEF30`.

## Known Limits

- `H001` cannot be reproduced before 2010 under the current validated data setup.
- The 1993-2009 long-history proxy covers the US core only.
- Korean tax modeling is simplified and does not fully model comprehensive income taxation.
- Tax-professional review is required before live implementation.
