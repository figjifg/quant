# W001 Korean Equity Backtest Engine Repair

Status: ACTIVE.

## Purpose

W001 is Korean equity backtest infrastructure repair.

This is infrastructure, alpha X.

W001 becomes the default foundation for future Korean single-stock research.
It does not revive S-family alpha and does not modify D013, H001,
`P08_IEF30`, or the legacy `src/backtest/engine.py`.

## Pre-registered Modules

1. `src/utils/korean_calendar.py`
2. `src/utils/corporate_action.py`
3. `src/utils/tradability.py`
4. `src/utils/sleeve_nav_simulator.py`
5. `src/utils/random_placebo_engine.py`
6. `src/utils/backtest_sanity_checks.py`

## Scope

- Implement corrected calendar, tradability, corporate-action, sleeve NAV,
  random placebo, and sanity-check utilities.
- Preserve signal date and execution date separation.
- Enforce T signal to T+1 or later execution.
- Provide a corrected smoke test for S001-G once W001 is complete.

## Non-scope

- No alpha rescue.
- No S-family continuation.
- No P08 satellite.
- No weight optimization.
- No edits to D013, H001, `P08_IEF30`, or `src/backtest/engine.py`.

## Completion Gate

W001 is complete only when the utilities have implementation tests covering
look-ahead, filtered-row execution, corporate actions, leverage, placebo
matching, and NAV sanity checks.
