# Q006 — QVSY Composite

Status: PRE-REGISTERED / RUN

## Purpose

Test the core final-candidate Q-family composite:

- Quality.
- Value.
- Shareholder Yield.

## Pre-registered Composite

- Quality score from Q002.
- Value score from Q003.
- Shareholder-yield score from Q004.
- Composite score = Q + V + SY.
- Equal weight across the three pre-registered component scores.
- This is the Q-family final-candidate composite for validation, with no
  additional grid or score weighting search.

Framework:

- Same Q002 framework: PIT +35 days, Top 30, quarterly rebalance, equal weight,
  USD NAV, SPY benchmark.
- Costs: 0 gross only.
- Current survivor universe limitation remains.

## Role

This is the main Q-family candidate only if Q000, Q001, and the component
factor tickets pass their gates.

## Explicit Failure Modes To Avoid

- Current S&P 500 constituents as historical universe = survivorship bias.
- Financial statement data before filing date = look-ahead bias.
- Searching many Q/V/SY weights for best Sharpe = overfitting.

## Separation Rule

Q006 does not promote, modify, or replace `P08_IEF30`. It remains a separate
US individual-stock fundamental sleeve.
