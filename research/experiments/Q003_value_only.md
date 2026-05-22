# Q003 — Value Only

Status: PRE-REGISTERED / RUN

## Purpose

Test a value-only US individual-stock sleeve.

## Pre-registered Signal

Value Score:

- `Value_Score = z(FCF_yield) + z(Earnings_yield)`

Only these two factors are allowed in Q003. No EV/EBITDA, P/B, P/S, sector
neutralization, or parameter grid is allowed in this ticket.

Definitions:

- `FCF_yield = (trailing_4Q_CFO - trailing_4Q_CapEx) / market_cap_estimate`
- `Earnings_yield = trailing_4Q_NetIncome / market_cap_estimate`
- `market_cap_estimate = latest filed shares as of availability date * stock close on rebalance/execution date`

Framework:

- Same Q002 framework: PIT +35 days, Top 30, quarterly rebalance, equal weight,
  USD NAV, SPY benchmark.
- Costs: 0 gross only.
- Current survivor universe limitation remains.

## Explicit Failure Modes To Avoid

- Current S&P 500 constituents as historical universe = survivorship bias.
- Financial statement data before filing date = look-ahead bias.
- Expanding factor combinations to find the best Sharpe = overfitting.

## Dependency

Do not implement until Q000 passes and Q001 defines the universe.
