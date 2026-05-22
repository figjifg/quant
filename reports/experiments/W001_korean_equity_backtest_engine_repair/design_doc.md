# W001 Design Doc

Status: design skeleton.

## Purpose

Repair Korean equity backtest infrastructure before any further Korean
single-stock research interpretation.

This is infrastructure, alpha X.

## Design Requirements

1. KRX calendar comes from tradable panel dates with non-null `KRX종가`.
2. Signal date and execution date are separate fields.
3. Execution uses T+1 or later, never signal day T.
4. Filtered rows cannot be executed by jumping to an unrelated row.
5. Corporate actions must be adjusted before return calculation.
6. Sleeve NAV is daily, cash-aware, and non-levered unless explicitly allowed.
7. Random controls must be date-matched and tradability-matched.
8. Sanity checks fail closed on impossible returns, leverage, and missing dates.

## Module Boundaries

- `korean_calendar.py`: KRX trading-day calendar and date advancement.
- `corporate_action.py`: adjusted price validation and return inputs.
- `tradability.py`: execution eligibility and next executable date.
- `sleeve_nav_simulator.py`: daily sleeve NAV accounting.
- `random_placebo_engine.py`: matched random placebo generation.
- `backtest_sanity_checks.py`: audit checks for generated signals, trades, and NAV.

## Explicit Non-goals

- No strategy change.
- No S-family alpha rescue.
- No P08 weight change.
- No legacy engine rewrite in W001 skeleton registration.
