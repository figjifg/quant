# W001 Testing Plan

Status: testing skeleton.

## Required Test Areas

1. Calendar: next KRX trading day is derived from panel rows, not invented.
2. Timing: signal date T executes on T+1 or later.
3. Filtered rows: excluded or non-tradable rows cannot become executions.
4. Corporate actions: adjusted price inputs are required for return math.
5. Leverage: sleeve NAV cannot exceed explicit gross exposure limits.
6. Random placebo: controls are date-matched and tradability-matched.
7. NAV: daily NAV, cash, positions, and costs reconcile.
8. Impossible returns: split-like or data-error returns fail closed.
9. Estimated rows: headline policy excludes `거래대금추정여부 == True`.
10. Regression: corrected S001-G smoke test runs once after W001.

## Required Files

- Unit tests for each new utility module.
- `tests/test_no_lookahead.py` additions for any timing-sensitive feature.
- A corrected S001-G smoke test after W001 implementation.

## Out of Scope

- No D013/H001/P08 weight re-optimization.
- No S-family continuation after the single corrected smoke test.
