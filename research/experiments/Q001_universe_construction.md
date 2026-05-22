# Q001 — Universe Construction

Status: BACKLOG (only after Q000 pass)

## Purpose

Construct a Russell 1000 or S&P 1500 liquid US individual-stock universe for
Q-family fundamental sleeve research.

## Requirements

- Universe must be survivorship-safe and include delisted companies.
- Current S&P 500 membership must not be used as a historical proxy.
- Historical ticker changes, mergers, splits, and delistings must be handled
  explicitly.
- Liquidity filter example: average traded value at least USD 100M.
- Universe membership timestamp must be available before any rebalance that
  uses it.

## Explicit Failure Modes To Avoid

- Current S&P 500 constituents as historical universe = survivorship bias.
- Financial statement data before filing date = look-ahead bias.
- Parameter search for best Sharpe = overfitting.

## Dependency

Do not start until Q000 confirms PIT fundamentals and survivorship-free
universe feasibility.

