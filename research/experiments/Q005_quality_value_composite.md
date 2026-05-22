# Q005 — Quality + Value Composite

Status: PRE-REGISTERED / RUN

## Purpose

Test a Q + V composite sleeve using the pre-registered quality and value
scores.

## Pre-registered Composite

- Quality score from Q002.
- Value score from Q003.
- Composite score = Quality score + Value score.
- Equal weight between the two pre-registered component scores.
- No additional grid, score weighting search, or factor expansion.

Framework:

- Same Q002 framework: PIT +35 days, Top 30, quarterly rebalance, equal weight,
  USD NAV, SPY benchmark.
- Costs: 0 gross only.
- Current survivor universe limitation remains.

## Explicit Failure Modes To Avoid

- Current S&P 500 constituents as historical universe = survivorship bias.
- Financial statement data before filing date = look-ahead bias.
- Weighting many factor combinations by highest Sharpe = overfitting.

## Dependency

Do not implement until Q000 passes, Q001 defines the universe, and Q002/Q003
are specified.
