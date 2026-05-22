# K002 One-shot Sector Momentum

Status: BACKLOG (after K000-K001)

## Purpose

Run exactly one sector momentum diagnostic rule under a strict budget.

## Pre-registered Rule

- Lookback: 12 months only.
- Top count: top 3 sectors equal-weight.
- Rebalance: quarterly.
- Universe: all 11 sector ETFs.
- Replacement sleeve: replace the `P08_IEF30` SPY 29% sleeve with a 29%
  sector rotation sleeve.

## Prohibited

- Lookback grid such as 3 / 6 / 9 / 12 / 18 months.
- Top-K grid such as 1 / 2 / 3 / 4 / 5.
- Weighting optimization.
- Sector risk filter.
- Additional sector selection.

This ticket is diagnostic only and does not promote a primary allocation.
