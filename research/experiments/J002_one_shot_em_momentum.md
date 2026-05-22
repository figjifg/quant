# J002 One-shot EM Momentum

Status: BACKLOG (after J001)

## Purpose

Run exactly one J-family momentum rule under the same strict budget as K002.

## Pre-registered Rule

- Lookback: 12 months, 252 trading days.
- Universe: VWO, EWY, EWJ, EWZ, MCHI.
- Top count: top 2 equal weight.
- Rebalance: quarterly.
- Ranking: trailing KRW total return.
- H001 and EM Korea sleeve double exposure is allowed and must be noted.

## Variants

| Candidate | Definition |
|---|---|
| J002-A | Replace the SPY 29% sleeve with EM momentum 29% |
| J002-B | Replace SPY + QQQ 50% with EM momentum 50% |
| J002-C | Pure EM momentum 100% reference |

## Prohibited

- Lookback grid.
- Top-K grid.
- Weighting optimization.
- Additional EM ETFs.
- Direct `P08_IEF30` promotion.
