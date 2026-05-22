# Q004 — Shareholder Yield Only

Status: PRE-REGISTERED / RUN

## Purpose

Test a shareholder-yield-only US individual-stock sleeve.

## Pre-registered Signal

Shareholder Yield Score:

- `SY_Score = z(Buyback_yield) + z(Dividend_yield) - z(Dilution)`

Definitions:

- `Buyback_yield = trailing_4Q_buybacks / market_cap_estimate`
- `Dividend_yield = trailing_4Q_dividends / market_cap_estimate`
- `Dilution = max(0, current_shares - shares_1y_ago) / shares_1y_ago`
- `market_cap_estimate = latest filed shares as of availability date * stock close on rebalance/execution date`

Missing dividend policy:

- If a cash dividend concept is missing for a ticker/period, dividend amount is
  treated as 0 and reported in `report.md`.

Framework:

- Same Q002 framework: PIT +35 days, Top 30, quarterly rebalance, equal weight,
  USD NAV, SPY benchmark.
- Costs: 0 gross only.
- No factor grid or shareholder-yield variants.

## Timestamp Requirements

- Buyback, dividend, and shares outstanding data must be aligned to their
  public availability date.
- Split-adjusted share counts and ticker changes must be documented.

## Explicit Failure Modes To Avoid

- Current S&P 500 constituents as historical universe = survivorship bias.
- Financial statement data before filing date = look-ahead bias.
- Searching many shareholder-yield variants for best Sharpe = overfitting.

## Dependency

Do not implement until Q000 passes and Q001 defines the universe.
